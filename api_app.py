"""API HTTP do CXPack Radar para o frontend Vite."""

from __future__ import annotations

import io
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from core.exceptions import QuotaExceededError
from database.connection import get_session_factory, init_db
from database.models import Company, DecisionMaker, Search, SearchResult
from database.repositories.companies import CompanyRepository
from database.repositories.searches import SearchRepository
from services.contact_service import ContactService
from services.decision_maker_service import DecisionMakerService
from services.enrichment_service import EnrichmentService
from services.export_service import ExportService
from services.quota_service import QuotaService
from services.search_service import SearchService


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="CXPack Radar API", version="2.0.0", lifespan=lifespan)
executor = ThreadPoolExecutor(max_workers=2)
jobs: dict[str, dict[str, Any]] = {}
jobs_lock = Lock()


class SearchPayload(BaseModel):
    product: str = Field(min_length=2, max_length=255)
    capacity: str = Field(default="", max_length=100)
    material: str = Field(default="", max_length=100)
    country: str = Field(default="Brasil", max_length=100)
    state: str = Field(default="", max_length=2)
    company_type: str = "Fabricante"
    max_queries: int = Field(default=3, ge=1, le=5)
    search_contacts: bool = True
    search_decision_makers: bool = True
    force_refresh: bool = False


def get_db():
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def company_summary(company: Company) -> dict[str, Any]:
    contacts = list(company.contacts)
    emails = [item.value for item in contacts if "EMAIL" in item.contact_type]
    phones = [item.value for item in contacts if item.contact_type in ("TELEFONE", "WHATSAPP")]
    return {
        "id": company.id,
        "name": company.name,
        "legal_name": company.legal_name,
        "trade_name": company.trade_name,
        "domain": company.domain,
        "website": company.website,
        "cnpj": company.cnpj,
        "status": company.status_cadastral,
        "cnae_code": company.cnae_code,
        "cnae_text": company.cnae_text,
        "capital_social": company.capital_social,
        "company_type": company.company_type,
        "description": company.description,
        "city": company.city,
        "state": company.state,
        "country": company.country,
        "score": company.score,
        "confidence": company.confidence,
        "crm_status": company.crm_status,
        "assigned_to": company.assigned_to,
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "contact_count": len(contacts) + len(company.department_contacts),
        "decision_maker_count": len(company.decision_makers),
        "partner_count": len(company.partners),
        "updated_at": iso(company.updated_at),
    }


def company_detail(company: Company) -> dict[str, Any]:
    data = company_summary(company)
    latest_match = max(company.cnpj_matches, key=lambda item: item.id, default=None)
    data.update({
        "address": latest_match.address if latest_match else None,
        "secondary_cnaes": latest_match.cnaes_secondary if latest_match else None,
        "notes": company.notes,
        "first_seen_at": iso(company.first_seen_at),
        "last_seen_at": iso(company.last_seen_at),
        "last_crawled_at": iso(company.last_crawled_at),
        "contacts": [
            {
                "id": item.id,
                "type": item.contact_type,
                "value": item.value,
                "source_url": item.source_url,
                "verified": item.is_verified,
            }
            for item in company.contacts
        ],
        "department_contacts": [
            {
                "department": item.department,
                "email": item.email,
                "phone": item.phone,
                "whatsapp": item.whatsapp,
                "source_url": item.source_url,
            }
            for item in company.department_contacts
        ],
        "decision_makers": [
            {
                "name": item.name,
                "role": item.role,
                "department": item.department,
                "email": item.email,
                "phone": item.phone,
                "linkedin_url": item.linkedin_url,
                "confidence": item.confidence,
                "source_url": item.source_url,
            }
            for item in company.decision_makers
        ],
        "partners": [
            {"name": item.name, "qualification": item.qualification, "country": item.country, "source": item.source}
            for item in company.partners
        ],
        "evidences": [
            {
                "field": item.field_name,
                "value": item.value,
                "source_url": item.source_url,
                "source_title": item.source_title,
                "source_text": item.source_text,
                "confidence": item.confidence,
            }
            for item in company.evidences
        ],
    })
    return data


def search_dict(item: Search) -> dict[str, Any]:
    return {
        "id": item.id,
        "product": item.product,
        "capacity": item.capacity,
        "material": item.material,
        "location": item.location,
        "company_type": item.company_type,
        "status": item.status,
        "companies_found": item.companies_found,
        "new_companies_found": item.new_companies_found,
        "error_message": item.error_message,
        "created_at": iso(item.created_at),
        "completed_at": iso(item.completed_at),
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/overview")
def overview(session: Session = Depends(get_db)):
    companies = list(session.scalars(select(Company).order_by(Company.score.desc())).all())
    searches = list(session.scalars(select(Search).order_by(Search.created_at.desc()).limit(6)).all())
    decision_makers = session.scalar(select(func.count()).select_from(DecisionMaker)) or 0
    actionable = sum(bool(item.contacts or item.department_contacts) for item in companies)
    quota = QuotaService(session).get_quota_dashboard_data()
    return {
        "metrics": {
            "companies": len(companies),
            "manufacturers": sum(item.company_type == "FABRICANTE" for item in companies),
            "candidates": sum(item.company_type == "CANDIDATO_CNAE" for item in companies),
            "actionable": actionable,
            "decision_makers": decision_makers,
        },
        "quota": quota,
        "recent_companies": [company_summary(item) for item in companies[:7]],
        "recent_searches": [search_dict(item) for item in searches],
    }


@app.get("/api/searches")
def list_searches(limit: int = Query(default=100, ge=1, le=500), session: Session = Depends(get_db)):
    items = session.scalars(select(Search).order_by(Search.created_at.desc()).limit(limit)).all()
    return [search_dict(item) for item in items]


@app.get("/api/companies")
def list_companies(
    search_id: int | None = None,
    min_score: int = Query(default=0, ge=0, le=100),
    company_type: str | None = None,
    q: str | None = Query(default=None, max_length=100),
    session: Session = Depends(get_db),
):
    stmt = select(Company)
    if search_id:
        stmt = stmt.join(SearchResult, SearchResult.company_id == Company.id).where(SearchResult.search_id == search_id)
    stmt = stmt.where(Company.score >= min_score)
    if company_type and company_type != "TODOS":
        stmt = stmt.where(Company.company_type == company_type)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(or_(
            Company.name.ilike(pattern), Company.legal_name.ilike(pattern),
            Company.cnpj.ilike(pattern), Company.city.ilike(pattern), Company.state.ilike(pattern),
        ))
    items = session.scalars(stmt.order_by(Company.score.desc(), Company.updated_at.desc())).unique().all()
    return [company_summary(item) for item in items]


@app.get("/api/companies-export.xlsx")
def export_companies(
    search_id: int | None = None,
    min_score: int = Query(default=0, ge=0, le=100),
    company_type: str | None = None,
    q: str | None = Query(default=None, max_length=100),
    session: Session = Depends(get_db),
):
    stmt = select(Company)
    if search_id:
        stmt = stmt.join(SearchResult, SearchResult.company_id == Company.id).where(SearchResult.search_id == search_id)
    stmt = stmt.where(Company.score >= min_score)
    if company_type and company_type != "TODOS":
        stmt = stmt.where(Company.company_type == company_type)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(or_(
            Company.name.ilike(pattern), Company.legal_name.ilike(pattern),
            Company.cnpj.ilike(pattern), Company.city.ilike(pattern), Company.state.ilike(pattern),
        ))
    companies = session.scalars(stmt.order_by(Company.score.desc(), Company.updated_at.desc())).unique().all()
    scope = f"Busca #{search_id}" if search_id else "Base completa"
    content = ExportService(session).export_to_xlsx(companies=companies, scope_label=scope)
    filename = f"cxpack_empresas_busca_{search_id}.xlsx" if search_id else "cxpack_empresas.xlsx"
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/companies/{company_id}")
def get_company(company_id: int, session: Session = Depends(get_db)):
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")
    return company_detail(company)


@app.post("/api/companies/{company_id}/enrich")
def enrich_company(company_id: int, session: Session = Depends(get_db)):
    result = EnrichmentService(session).enrich_company(company_id, operator="web")
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message", "Não foi possível enriquecer a empresa."))
    return result


@app.delete("/api/companies/{company_id}", status_code=204)
def delete_company(company_id: int, session: Session = Depends(get_db)):
    if not CompanyRepository(session).delete_company(company_id):
        raise HTTPException(status_code=404, detail="Empresa não encontrada.")


def set_job(job_id: str, **values: Any):
    with jobs_lock:
        jobs[job_id] = {**jobs.get(job_id, {}), **values}


def run_search(job_id: str, payload: SearchPayload):
    session = get_session_factory()()
    try:
        location = f"{payload.state.upper()}, {payload.country}" if payload.state else payload.country
        set_job(job_id, status="RUNNING", stage="Pesquisando fontes públicas", progress=12)
        result = SearchService(session).execute_prospecting_search(
            product=payload.product,
            capacity=payload.capacity,
            material=payload.material,
            location=location,
            company_type=payload.company_type,
            max_queries=payload.max_queries,
            operator="web",
            force_refresh=payload.force_refresh,
        )

        companies = SearchRepository(session).list_companies_for_search(result["search_id"])
        confirmed = [item for item in companies if item.company_type == "FABRICANTE" and item.website]
        contacts_saved = 0
        decision_makers_saved = 0

        if payload.search_contacts and confirmed:
            set_job(job_id, stage="Extraindo telefones e e-mails", progress=58)
            contact_service = ContactService(session)
            for item in confirmed:
                contact_result = contact_service.crawl_and_extract_company_contacts(item.id)
                contacts_saved += contact_result.get("new_contacts_saved", 0) if contact_result.get("success") else 0

        if payload.search_decision_makers and confirmed:
            set_job(job_id, stage="Mapeando compras e diretoria", progress=82)
            decision_service = DecisionMakerService(session)
            for item in confirmed:
                decision_result = decision_service.search_decision_makers(item.id, operator="web")
                decision_makers_saved += decision_result.get("new_decision_makers_saved", 0) if decision_result.get("success") else 0

        set_job(
            job_id,
            status="COMPLETED",
            stage="Pesquisa concluída",
            progress=100,
            result={**result, "contacts_saved": contacts_saved, "decision_makers_saved": decision_makers_saved},
        )
    except QuotaExceededError as exc:
        set_job(job_id, status="FAILED", stage="Limite de busca atingido", progress=100, error=exc.user_friendly_message)
    except Exception as exc:
        set_job(job_id, status="FAILED", stage="Falha na pesquisa", progress=100, error=str(exc))
    finally:
        session.close()


@app.post("/api/search-jobs", status_code=202)
def create_search_job(payload: SearchPayload):
    job_id = uuid4().hex
    set_job(job_id, id=job_id, status="QUEUED", stage="Preparando pesquisa", progress=2, error=None, result=None)
    executor.submit(run_search, job_id, payload)
    return jobs[job_id]


@app.get("/api/search-jobs/{job_id}")
def get_search_job(job_id: str):
    # ponytail: jobs ficam no processo único; persistir no banco quando houver múltiplos workers.
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Execução não encontrada.")
    return job


dist = Path(__file__).resolve().parent / "dist"
if dist.exists():
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        return FileResponse(dist / "index.html")
