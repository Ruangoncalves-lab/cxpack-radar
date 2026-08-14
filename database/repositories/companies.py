"""
Repositório para gerenciamento de Empresas no banco de dados.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models import Company, Evidence


class CompanyRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_domain(self, domain: str) -> Optional[Company]:
        """Busca uma empresa pelo domínio normalizado (único)."""
        stmt = select(Company).where(Company.domain == domain.lower().strip())
        return self.session.scalar(stmt)

    def upsert_company(
        self,
        domain: str,
        name: str,
        website: Optional[str] = None,
        company_type: str = "DESCONHECIDO",
        city: Optional[str] = None,
        state: Optional[str] = None,
        score: int = 0,
        confidence: float = 0.0,
        description: Optional[str] = None
    ) -> tuple[Company, bool]:
        """
        Cria uma nova empresa ou atualiza os dados se o domínio já existir.
        Retorna tuple (Company, is_created: bool).
        """
        clean_domain = domain.lower().strip()
        company = self.get_by_domain(clean_domain)
        is_created = False

        if not company:
            company = Company(
                domain=clean_domain,
                name=name,
                website=website,
                company_type=company_type,
                city=city,
                state=state,
                score=score,
                confidence=confidence,
                description=description
            )
            self.session.add(company)
            is_created = True
        else:
            # Atualiza dados existentes preservando informações melhores
            if name and (company.name == clean_domain or not company.name):
                company.name = name
            if company_type != "DESCONHECIDO":
                company.company_type = company_type
            if city:
                company.city = city
            if state:
                company.state = state
            if score > company.score:
                company.score = score
            if confidence > company.confidence:
                company.confidence = confidence
            if description and not company.description:
                company.description = description
            company.last_seen_at = datetime.now()

        self.session.commit()
        return company, is_created

    def delete_company(self, company_id: int) -> bool:
        """Exclui permanentemente uma empresa e todos os seus relacionamentos do banco de dados."""
        company = self.session.get(Company, company_id)
        if company:
            self.session.delete(company)
            self.session.commit()
            return True
        return False

    def add_evidence(
        self,
        company_id: int,
        field_name: str,
        value: Optional[str] = None,
        source_url: Optional[str] = None,
        source_title: Optional[str] = None,
        source_text: Optional[str] = None,
        confidence: float = 0.0
    ) -> Evidence:
        """Adiciona uma evidência à empresa."""
        evidence = Evidence(
            company_id=company_id,
            field_name=field_name,
            value=value,
            source_url=source_url,
            source_title=source_title,
            source_text=source_text,
            confidence=confidence
        )
        self.session.add(evidence)
        self.session.commit()
        return evidence

    def list_companies(self, min_score: int = 0, company_type: Optional[str] = None, limit: Optional[int] = None) -> List[Company]:
        """Lista empresas cadastradas com filtros simples e limite opcional."""
        stmt = select(Company).where(Company.score >= min_score)
        if company_type and company_type != "TODOS":
            stmt = stmt.where(Company.company_type == company_type)
        stmt = stmt.order_by(Company.score.desc(), Company.updated_at.desc())
        if limit:
            stmt = stmt.limit(limit)
        return list(self.session.scalars(stmt).all())
