"""
Repositório para gerenciamento de contatos de departamento (DepartmentContact).
"""

from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from database.models import DepartmentContact


class DepartmentContactRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_department_contact(
        self,
        company_id: int,
        department: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        whatsapp: Optional[str] = None,
        source_url: Optional[str] = None,
        confidence: float = 0.9
    ) -> tuple[DepartmentContact, bool]:
        """
        Adiciona ou atualiza um contato de setor (ex: compras@, suprimentos@).
        Deduplicação por (company_id + department + email).
        """
        clean_dept = department.strip().title()
        clean_email = email.strip().lower() if email else None

        stmt = select(DepartmentContact).where(
            and_(
                DepartmentContact.company_id == company_id,
                DepartmentContact.department == clean_dept,
                DepartmentContact.email == clean_email
            )
        )
        existing = self.session.scalar(stmt)
        if existing:
            if phone and not existing.phone:
                existing.phone = phone
            if whatsapp and not existing.whatsapp:
                existing.whatsapp = whatsapp
            self.session.commit()
            return existing, False

        dept_contact = DepartmentContact(
            company_id=company_id,
            department=clean_dept,
            email=clean_email,
            phone=phone,
            whatsapp=whatsapp,
            source_url=source_url,
            confidence=confidence
        )
        self.session.add(dept_contact)
        self.session.commit()
        return dept_contact, True

    def get_company_department_contacts(self, company_id: int) -> List[DepartmentContact]:
        """Retorna todos os contatos de departamento de uma empresa."""
        stmt = select(DepartmentContact).where(DepartmentContact.company_id == company_id).order_by(DepartmentContact.department)
        return list(self.session.scalars(stmt).all())
