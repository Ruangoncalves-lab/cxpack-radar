"""
Repositório para gerenciamento e consulta de Tomadores de Decisão (DecisionMaker).
"""

from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from database.models import DecisionMaker


class DecisionMakerRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_decision_maker(
        self,
        company_id: int,
        name: str,
        role: str,
        email: Optional[str] = None,
        email_status: str = "INFERIDO",
        department: Optional[str] = None,
        phone: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        source_url: Optional[str] = None,
        source_title: Optional[str] = None,
        confidence: float = 0.7
    ) -> tuple[DecisionMaker, bool]:
        """
        Adiciona um novo decisor para a empresa com deduplicação por (company_id + name).
        Retorna (DecisionMaker, is_new: bool).
        """
        clean_name = name.strip().title()
        stmt = select(DecisionMaker).where(
            and_(
                DecisionMaker.company_id == company_id,
                DecisionMaker.name == clean_name
            )
        )
        existing = self.session.scalar(stmt)
        if existing:
            # Atualizar e-mail se não possuía
            if email and not existing.email:
                existing.email = email
                existing.email_status = email_status
            if linkedin_url and not existing.linkedin_url:
                existing.linkedin_url = linkedin_url
            self.session.commit()
            return existing, False

        dm = DecisionMaker(
            company_id=company_id,
            name=clean_name,
            role=role.strip().title(),
            email=email,
            email_status=email_status,
            department=department,
            phone=phone,
            linkedin_url=linkedin_url,
            source_url=source_url,
            source_title=source_title,
            confidence=confidence
        )
        self.session.add(dm)
        self.session.commit()
        return dm, True

    def get_company_decision_makers(self, company_id: int) -> List[DecisionMaker]:
        """Retorna os decisores associados a uma empresa."""
        stmt = select(DecisionMaker).where(DecisionMaker.company_id == company_id).order_by(DecisionMaker.created_at.desc())
        return list(self.session.scalars(stmt).all())

    def get_by_company(self, company_id: int) -> List[DecisionMaker]:
        return self.get_company_decision_makers(company_id)

    def list_all_decision_makers(self, limit: int = 100) -> List[DecisionMaker]:
        """Lista todos os decisores cadastrados no sistema."""
        stmt = select(DecisionMaker).order_by(DecisionMaker.created_at.desc()).limit(limit)
        return list(self.session.scalars(stmt).all())
