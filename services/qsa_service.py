"""
Serviço de Importação do Quadro de Sócios e Administradores (QSAService - Fase D).
Importa sócios para company_partners e promove Sócios-Administradores a decisores CORPORATE.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from database.repositories.partners import PartnerRepository
from database.repositories.decision_makers import DecisionMakerRepository
from database.repositories.companies import CompanyRepository


class QSAService:
    def __init__(self, session: Session):
        self.session = session
        self.partner_repo = PartnerRepository(session)
        self.dm_repo = DecisionMakerRepository(session)
        self.company_repo = CompanyRepository(session)

    def import_qsa_partners(self, company_id: int, qsa_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Cadastra sócios no QSA da empresa e cria decisores do tipo CORPORATE para administradores.
        """
        from database.models import Company
        company = self.session.get(Company, company_id)

        if not company or not qsa_list:
            return {"success": False, "imported_partners": 0, "corporate_decision_makers": 0}

        imported_partners_count = 0
        corporate_dms_count = 0

        for partner_info in qsa_list:
            name = partner_info.get("name")
            qual = partner_info.get("qualification") or "SOCIO"
            if not name:
                continue

            # 1. Salvar no QSA
            partner_rec, is_new_partner = self.partner_repo.add_partner(
                company_id=company.id,
                name=name,
                qualification=qual,
                country=partner_info.get("country", "Brasil"),
                legal_representative=partner_info.get("legal_representative"),
                source="Dados Abertos CNPJ / Receita Federal"
            )
            if is_new_partner:
                imported_partners_count += 1

            # 2. Promover a Decisor Societário (CORPORATE) se for Administrador/Sócio-Admin
            qual_upper = qual.upper()
            is_admin = any(k in qual_upper for k in ["ADMINISTRADOR", "PROPRIETARIO", "PRESIDENTE", "GERENTE"])
            is_socio = "SOCIO" in qual_upper

            if is_admin or is_socio:
                dm_role = qual_upper if not is_admin else "Sócio-Administrador"
                priority = 9 if is_admin else 10
                score = 70 if is_admin else 60

                dm_rec, is_new_dm = self.dm_repo.add_decision_maker(
                    company_id=company.id,
                    name=name,
                    role=dm_role,
                    email=None,
                    email_status="NAO_CONFIRMADO",
                    source_url=company.website,
                    source_title="Dados Abertos CNPJ / Receita Federal",
                    confidence=1.0
                )
                if is_new_dm:
                    dm_rec.decision_maker_type = "CORPORATE"
                    dm_rec.decision_priority = priority
                    dm_rec.decision_maker_score = score
                    dm_rec.department = "Administração / Societário"
                    corporate_dms_count += 1

                    # Adicionar evidência oficial
                    self.company_repo.add_evidence(
                        company_id=company.id,
                        field_name="corporate_partner_qsa",
                        value=f"{name} ({dm_role})",
                        source_url=company.website,
                        source_title="Dados Abertos CNPJ / Receita Federal",
                        source_text=f"Sócio/Administrador no QSA: {name} - Qualificação: {qual_upper}",
                        confidence=1.0
                    )

        self.session.commit()

        return {
            "success": True,
            "imported_partners": imported_partners_count,
            "corporate_decision_makers": corporate_dms_count
        }
