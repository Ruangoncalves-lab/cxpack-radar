"""
Serviço de Exportação de Dados em CSV e Excel (ExportService - Fase G).
Inclui dados de CNPJ, QSA, Contatos de Departamento e Decisores Operacionais/Societários.
"""

import io
import pandas as pd
from typing import List, Optional
from sqlalchemy.orm import Session
from database.repositories.companies import CompanyRepository
from database.repositories.contacts import ContactRepository
from database.repositories.decision_makers import DecisionMakerRepository
from database.repositories.partners import PartnerRepository
from database.repositories.department_contacts import DepartmentContactRepository


class ExportService:
    def __init__(self, session: Session):
        self.session = session
        self.company_repo = CompanyRepository(session)
        self.contact_repo = ContactRepository(session)
        self.dm_repo = DecisionMakerRepository(session)
        self.partner_repo = PartnerRepository(session)
        self.dept_repo = DepartmentContactRepository(session)

    def build_export_dataframe(self, min_score: int = 0) -> pd.DataFrame:
        """
        Monta um DataFrame completo consolidando CNPJ, Razão Social, CNAE, QSA, Contatos do Setor, Decisores e CRM.
        """
        companies = self.company_repo.list_companies(min_score=min_score)
        rows = []

        for comp in companies:
            contacts = self.contact_repo.get_company_contacts(comp.id)
            dms = self.dm_repo.get_company_decision_makers(comp.id)
            partners = self.partner_repo.get_company_partners(comp.id)
            dept_contacts = self.dept_repo.get_company_department_contacts(comp.id)

            public_emails = [c.value for c in contacts if "EMAIL" in c.contact_type]
            phones = [c.value for c in contacts if c.contact_type in ("TELEFONE", "WHATSAPP")]

            str_emails = ", ".join(public_emails) if public_emails else "Não identificado"
            str_phones = ", ".join(phones) if phones else "Não identificado"

            # String formatada de QSA
            str_qsa = ", ".join([f"{p.name} ({p.qualification})" for p in partners]) if partners else "Não consultado"

            # String formatada de Contatos do Setor de Compras
            str_dept = ", ".join([f"{dc.department}: {dc.email or dc.phone or ''}" for dc in dept_contacts]) if dept_contacts else "Não identificado"

            if dms:
                for dm in dms:
                    rows.append({
                        "Empresa": comp.name,
                        "Razão Social": comp.legal_name or comp.name,
                        "Site": comp.website or comp.domain,
                        "CNPJ": comp.cnpj or "",
                        "Situação Cadastral": comp.status_cadastral or "ATIVA",
                        "CNAE": f"{comp.cnae_code or ''} - {comp.cnae_text or ''}".strip(" -"),
                        "Tipo": comp.company_type,
                        "Score": comp.score,
                        "Cidade": comp.city or "",
                        "UF": comp.state or "",
                        "Telefones Empresa": str_phones,
                        "E-mails Públicos Empresa": str_emails,
                        "Contatos do Setor": str_dept,
                        "QSA (Sócios/Admins)": str_qsa,
                        "Nome Decisor": dm.name,
                        "Cargo": dm.role,
                        "Departamento": dm.department or "Compras",
                        "Tipo Decisor": dm.decision_maker_type,
                        "E-mail Decisor": dm.email or "",
                        "Status E-mail": dm.email_status,
                        "Fonte": dm.source_title or dm.source_url or "Website",
                        "Confiança": f"{int(dm.confidence * 100)}%",
                        "Status CRM": comp.crm_status,
                        "Responsável": comp.assigned_to or "Não atribuído"
                    })
            else:
                rows.append({
                    "Empresa": comp.name,
                    "Razão Social": comp.legal_name or comp.name,
                    "Site": comp.website or comp.domain,
                    "CNPJ": comp.cnpj or "",
                    "Situação Cadastral": comp.status_cadastral or "ATIVA",
                    "CNAE": f"{comp.cnae_code or ''} - {comp.cnae_text or ''}".strip(" -"),
                    "Tipo": comp.company_type,
                    "Score": comp.score,
                    "Cidade": comp.city or "",
                    "UF": comp.state or "",
                    "Telefones Empresa": str_phones,
                    "E-mails Públicos Empresa": str_emails,
                    "Contatos do Setor": str_dept,
                    "QSA (Sócios/Admins)": str_qsa,
                    "Nome Decisor": "Nenhum mapeado",
                    "Cargo": "",
                    "Departamento": "",
                    "Tipo Decisor": "",
                    "E-mail Decisor": "",
                    "Status E-mail": "",
                    "Fonte": comp.website or "",
                    "Confiança": "",
                    "Status CRM": comp.crm_status,
                    "Responsável": comp.assigned_to or "Não atribuído"
                })

        return pd.DataFrame(rows)

    def export_to_csv(self, min_score: int = 0) -> bytes:
        df = self.build_export_dataframe(min_score=min_score)
        return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

    def export_to_xlsx(self, min_score: int = 0) -> bytes:
        df = self.build_export_dataframe(min_score=min_score)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Prospecção Enriquecida")
        return output.getvalue()
