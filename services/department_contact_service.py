"""
Serviço de Gestão de Contatos de Departamento e Níveis de Prospecção A/B/C (DepartmentContactService - Fase E).
"""

import re
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from database.repositories.department_contacts import DepartmentContactRepository
from database.repositories.contacts import ContactRepository
from database.repositories.decision_makers import DecisionMakerRepository

DEPARTMENT_EMAIL_PREFIXES = {
    "compras": "Compras",
    "suprimentos": "Suprimentos",
    "procurement": "Procurement",
    "purchasing": "Compras",
    "fornecedores": "Fornecedores",
    "sejafornecedor": "Fornecedores",
    "cotacao": "Compras / Cotação",
    "supplychain": "Supply Chain",
    "sourcing": "Sourcing",
    "comercial": "Comercial / Vendas"
}


class DepartmentContactService:
    def __init__(self, session: Session):
        self.session = session
        self.dept_repo = DepartmentContactRepository(session)
        self.contact_repo = ContactRepository(session)
        self.dm_repo = DecisionMakerRepository(session)

    def extract_and_save_department_contacts(self, company_id: int) -> int:
        """
        Analisa os contatos públicos da empresa e identifica e-mails genéricos de setor (compras@, suprimentos@, etc.).
        """
        contacts = self.contact_repo.get_company_contacts(company_id)
        saved_dept_count = 0

        for c in contacts:
            if "EMAIL" in c.contact_type and c.value:
                local_part = c.value.split("@")[0].lower()
                for prefix, dept_name in DEPARTMENT_EMAIL_PREFIXES.items():
                    if prefix in local_part:
                        _, is_new = self.dept_repo.add_department_contact(
                            company_id=company_id,
                            department=dept_name,
                            email=c.value,
                            source_url=c.source_url,
                            confidence=0.95
                        )
                        if is_new:
                            saved_dept_count += 1
                        break

        return saved_dept_count

    def classify_prospecting_levels(self, company_id: int) -> Dict[str, Any]:
        """
        Classifica os resultados disponíveis para prospecção B2B nos Níveis A, B e C:
        - NÍVEL A: Nome + Cargo + Contato (Decisor Operacional com E-mail/Telefone)
        - NÍVEL B: Nome + Cargo (Decisor sem e-mail direto)
        - NÍVEL C: Contato do Departamento (e-mail do setor de compras)
        """
        dms = self.dm_repo.get_company_decision_makers(company_id)
        dept_contacts = self.dept_repo.get_company_department_contacts(company_id)

        level_a = []
        level_b = []
        level_c = []

        for dm in dms:
            if dm.email or dm.phone:
                level_a.append({
                    "name": dm.name,
                    "role": dm.role,
                    "contact": dm.email or dm.phone,
                    "email_status": dm.email_status,
                    "type": dm.decision_maker_type,
                    "source": dm.source_title or dm.source_url
                })
            else:
                level_b.append({
                    "name": dm.name,
                    "role": dm.role,
                    "type": dm.decision_maker_type,
                    "source": dm.source_title or dm.source_url
                })

        for dc in dept_contacts:
            level_c.append({
                "department": dc.department,
                "email": dc.email,
                "phone": dc.phone,
                "source": dc.source_url
            })

        best_level = "NENHUM"
        if level_a:
            best_level = "NÍVEL A (Nome + Cargo + Contato)"
        elif level_b:
            best_level = "NÍVEL B (Nome + Cargo)"
        elif level_c:
            best_level = "NÍVEL C (Contato do Departamento)"

        return {
            "best_level": best_level,
            "level_a": level_a,
            "level_b": level_b,
            "level_c": level_c
        }
