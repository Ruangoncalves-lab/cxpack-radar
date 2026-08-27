"""
Orquestrador do Pipeline de Enriquecimento em Camadas (EnrichmentService - Fase F).
Integra CNPJDataProvider, Matching, QSA, DepartmentContacts, Crawler e Gemini Search.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from providers.cnpj.public_cnpj_provider import PublicCNPJProvider
from services.cnpj_matching_service import CNPJMatchingService, AUTO_CNPJ_MATCH_MIN_SCORE
from services.qsa_service import QSAService
from services.department_contact_service import DepartmentContactService
from services.contact_service import ContactService
from services.decision_maker_service import DecisionMakerService
from services.scoring_service import ScoringService
from database.repositories.companies import CompanyRepository
from database.repositories.cnpj_matches import CNPJMatchRepository
from database.repositories.contacts import ContactRepository
from utils.phones import normalize_phone_br


class EnrichmentService:
    def __init__(self, session: Session):
        self.session = session
        self.company_repo = CompanyRepository(session)
        self.match_repo = CNPJMatchRepository(session)
        self.contact_repo = ContactRepository(session)
        self.cnpj_provider = PublicCNPJProvider()
        self.matching_service = CNPJMatchingService()
        self.qsa_service = QSAService(session)
        self.dept_service = DepartmentContactService(session)
        self.contact_service = ContactService(session)
        self.dm_service = DecisionMakerService(session)
        self.scoring_service = ScoringService()

    def enrich_company(self, company_id: int, operator: str = "usuario") -> Dict[str, Any]:
        """
        Executa o pipeline completo de enriquecimento empresarial em camadas:
        1. Consulta dados públicos de CNPJ se a empresa possuir CNPJ cadastrado ou sugerido
        2. Executa algoritmo de matching (company_match_score)
        3. Importa QSA e insere decisores SOCIETÁRIOS (CORPORATE)
        4. Crawlea o site oficial e extrai e-mails de departamento (NÍVEL C)
        5. Busca decisores OPERACIONAIS no Gemini Search se Score >= 70 (NÍVEL A/B)
        """
        from database.models import Company
        company = self.session.get(Company, company_id)

        if not company:
            return {"success": False, "message": "Empresa não encontrada."}

        enriched_log = []

        # 1. Enriquecimento via CNPJ / Receita Federal (se houver CNPJ)
        if company.cnpj:
            cnpj_info = self.cnpj_provider.get_company_by_cnpj(company.cnpj)
            if cnpj_info:
                # Algoritmo de Matching
                is_registry_candidate = (
                    company.company_type == "CANDIDATO_CNAE"
                    and company.cnpj == cnpj_info["cnpj"]
                )
                match_res = (
                    {"match_score": 100, "is_auto_matched": True}
                    if is_registry_candidate
                    else self.matching_service.calculate_match_score(
                        company_name=company.name,
                        cnpj_legal_name=cnpj_info["legal_name"],
                        cnpj_trade_name=cnpj_info["trade_name"],
                        company_city=company.city,
                        cnpj_city=cnpj_info["city"],
                        company_state=company.state,
                        cnpj_state=cnpj_info["state"],
                        company_domain=company.domain,
                        cnpj_email=cnpj_info["email"]
                    )
                )

                # Salvar registro do match no histórico
                self.match_repo.add_match(
                    company_id=company.id,
                    cnpj=company.cnpj,
                    legal_name=cnpj_info["legal_name"],
                    trade_name=cnpj_info["trade_name"],
                    cnae_code=cnpj_info["cnae_code"],
                    cnae_text=cnpj_info["cnae_text"],
                    cnaes_secondary=", ".join(cnpj_info.get("cnaes_secondary") or []),
                    status_cadastral=cnpj_info["status_cadastral"],
                    address=cnpj_info.get("address"),
                    city=cnpj_info["city"],
                    state=cnpj_info["state"],
                    phone=cnpj_info["phone"],
                    email=cnpj_info["email"],
                    capital_social=cnpj_info["capital_social"],
                    match_score=match_res["match_score"],
                    is_auto_matched=match_res["is_auto_matched"]
                )

                if match_res["is_auto_matched"]:
                    company.legal_name = cnpj_info["legal_name"]
                    company.trade_name = cnpj_info["trade_name"]
                    company.cnae_code = cnpj_info["cnae_code"]
                    company.cnae_text = cnpj_info["cnae_text"]
                    company.capital_social = cnpj_info["capital_social"]
                    company.status_cadastral = cnpj_info["status_cadastral"]
                    if not company.city and cnpj_info["city"]:
                        company.city = cnpj_info["city"]
                    if not company.state and cnpj_info["state"]:
                        company.state = cnpj_info["state"]

                    enriched_log.append(f"CNPJ {company.cnpj} vinculado com sucesso (Match Score: {match_res['match_score']}/100).")

                    official_source = (
                        "https://brasilapi.com.br/"
                        if "BrasilAPI" in cnpj_info.get("source", "")
                        else "https://minhareceita.org/"
                    )
                    new_official_contacts = 0
                    for raw_phone in cnpj_info.get("phones") or [cnpj_info.get("phone")]:
                        phone_digits = "".join(filter(str.isdigit, raw_phone or ""))
                        if phone_digits.startswith("55") and len(phone_digits) in (12, 13):
                            phone_digits = phone_digits[2:]
                        normalized_phone = normalize_phone_br(raw_phone or "")
                        if normalized_phone and len(phone_digits) in (10, 11):
                            _, is_new = self.contact_repo.add_contact(
                                company_id=company.id,
                                contact_type="TELEFONE",
                                value=normalized_phone,
                                raw_value=raw_phone,
                                source_url=official_source,
                                is_verified=True,
                            )
                            new_official_contacts += int(is_new)

                    public_email = (cnpj_info.get("email") or "").strip()
                    if "@" in public_email:
                        _, is_new = self.contact_repo.add_contact(
                            company_id=company.id,
                            contact_type="EMAIL_PUBLICO",
                            value=public_email,
                            source_url=official_source,
                            is_verified=True,
                        )
                        new_official_contacts += int(is_new)
                    if new_official_contacts:
                        enriched_log.append(f"{new_official_contacts} contatos oficiais do CNPJ adicionados.")

                    # Importar QSA
                    qsa_res = self.qsa_service.import_qsa_partners(company.id, cnpj_info.get("qsa", []))
                    if qsa_res["imported_partners"] > 0:
                        enriched_log.append(f"QSA Importado: {qsa_res['imported_partners']} sócios/administradores salvos.")

        # 2. Crawlear Site Oficial
        if company.website:
            crawl_res = self.contact_service.crawl_and_extract_company_contacts(company.id)
            if crawl_res["success"]:
                enriched_log.append(f"Website crawleado ({crawl_res['pages_crawled']} páginas).")

        # 3. Extrair Contatos de Departamento (Compras, Suprimentos, etc.)
        dept_count = self.dept_service.extract_and_save_department_contacts(company.id)
        if dept_count > 0:
            enriched_log.append(f"{dept_count} contatos de departamento identificados (compras@, suprimentos@).")

        # 4. Recalcular Score da Empresa
        self.scoring_service.update_company_score(company)

        # 5. Se o Score for >= 70, buscar Decisores Operacionais via Gemini Search
        if company.score >= 70:
            dm_res = self.dm_service.search_decision_makers(company.id, operator=operator)
            if dm_res["success"]:
                enriched_log.append(f"{dm_res['new_decision_makers_saved']} decisores operacionais mapeados.")

        # 6. Classificar Níveis A / B / C
        level_info = self.dept_service.classify_prospecting_levels(company.id)

        company.updated_at = datetime.now()
        self.session.commit()

        return {
            "success": True,
            "company_id": company.id,
            "company_name": company.name,
            "score": company.score,
            "best_level": level_info["best_level"],
            "log": enriched_log,
            "levels": level_info
        }
