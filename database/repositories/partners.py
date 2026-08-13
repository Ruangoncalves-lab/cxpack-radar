"""
Repositório para gerenciamento do Quadro de Sócios e Administradores (CompanyPartner - QSA).
"""

from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from database.models import CompanyPartner


class PartnerRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_partner(
        self,
        company_id: int,
        name: str,
        qualification: str = "SOCIO",
        country: str = "Brasil",
        legal_representative: Optional[str] = None,
        source: str = "Dados Abertos CNPJ / Receita Federal"
    ) -> tuple[CompanyPartner, bool]:
        """
        Adiciona um novo sócio/administrador com deduplicação por (company_id + name).
        Retorna tuple (CompanyPartner, is_new: bool).
        """
        clean_name = name.strip().title()
        stmt = select(CompanyPartner).where(
            and_(
                CompanyPartner.company_id == company_id,
                CompanyPartner.name == clean_name
            )
        )
        existing = self.session.scalar(stmt)
        if existing:
            existing.qualification = qualification.strip().upper()
            self.session.commit()
            return existing, False

        partner = CompanyPartner(
            company_id=company_id,
            name=clean_name,
            qualification=qualification.strip().upper(),
            country=country,
            legal_representative=legal_representative,
            source=source
        )
        self.session.add(partner)
        self.session.commit()
        return partner, True

    def get_company_partners(self, company_id: int) -> List[CompanyPartner]:
        """Retorna todos os sócios/administradores de uma empresa."""
        stmt = select(CompanyPartner).where(CompanyPartner.company_id == company_id).order_by(CompanyPartner.name)
        return list(self.session.scalars(stmt).all())
