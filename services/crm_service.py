"""
Serviço de Gestão de Leads e Mini CRM (CRMService - Fase 5).
Permite alterar status do lead, atribuir responsáveis e registrar notas comerciais.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Company, TeamMember
from database.repositories.companies import CompanyRepository

VALID_CRM_STATUSES = [
    "NOVO", "INTERESSANTE", "CONTATAR", "CONTATADO",
    "COTACAO_SOLICITADA", "NEGOCIANDO", "DESCARTADO"
]


class CRMService:
    def __init__(self, session: Session):
        self.session = session
        self.company_repo = CompanyRepository(session)

    def update_lead_status(self, company_id: int, new_status: str) -> Dict[str, Any]:
        """Atualiza o estágio do lead no funil do CRM."""
        status_upper = new_status.upper().strip()
        if status_upper not in VALID_CRM_STATUSES:
            return {"success": False, "message": f"Status inválido. Escolha entre: {', '.join(VALID_CRM_STATUSES)}"}

        company = self.session.get(Company, company_id)
        if not company:
            return {"success": False, "message": "Empresa não encontrada."}

        company.crm_status = status_upper
        company.updated_at = datetime.now()
        self.session.commit()

        return {
            "success": True,
            "company_name": company.name,
            "new_status": company.crm_status
        }

    def assign_lead(self, company_id: int, team_member_name: str) -> Dict[str, Any]:
        """Atribui o lead a um membro da equipe."""
        company = self.session.get(Company, company_id)
        if not company:
            return {"success": False, "message": "Empresa não encontrada."}

        company.assigned_to = team_member_name.strip()
        company.updated_at = datetime.now()
        self.session.commit()

        return {
            "success": True,
            "company_name": company.name,
            "assigned_to": company.assigned_to
        }

    def update_lead_notes(self, company_id: int, notes: str) -> Dict[str, Any]:
        """Atualiza as observações comerciais do lead."""
        company = self.session.get(Company, company_id)
        if not company:
            return {"success": False, "message": "Empresa não encontrada."}

        company.notes = notes.strip()
        company.updated_at = datetime.now()
        self.session.commit()

        return {
            "success": True,
            "company_name": company.name,
            "notes": company.notes
        }

    def get_crm_funnel_summary(self) -> Dict[str, int]:
        """Retorna a contagem de leads por estágio do funil."""
        summary = {st: 0 for st in VALID_CRM_STATUSES}
        companies = self.company_repo.list_companies(min_score=0)
        for c in companies:
            st_val = (c.crm_status or "NOVO").upper()
            if st_val in summary:
                summary[st_val] += 1
            else:
                summary["NOVO"] += 1
        return summary
