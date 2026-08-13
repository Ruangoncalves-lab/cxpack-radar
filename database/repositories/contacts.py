"""
Repositório para gerenciamento e deduplicação de Contatos Públicos de empresas.
"""

from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from database.models import Contact


class ContactRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_contact(
        self,
        company_id: int,
        contact_type: str,
        value: str,
        raw_value: Optional[str] = None,
        source_url: Optional[str] = None,
        is_verified: bool = False
    ) -> tuple[Contact, bool]:
        """
        Adiciona um contato se ainda não existir para a empresa (deduplicação por empresa_id + valor).
        Retorna tuple (Contact, is_new: bool).
        """
        clean_value = value.strip().lower()
        stmt = select(Contact).where(
            and_(
                Contact.company_id == company_id,
                Contact.value == clean_value
            )
        )
        existing = self.session.scalar(stmt)
        if existing:
            return existing, False

        contact = Contact(
            company_id=company_id,
            contact_type=contact_type,
            value=clean_value,
            raw_value=raw_value or value,
            source_url=source_url,
            is_verified=is_verified
        )
        self.session.add(contact)
        self.session.commit()
        return contact, True

    def get_company_contacts(self, company_id: int) -> List[Contact]:
        """Retorna todos os contatos associados a uma empresa."""
        stmt = select(Contact).where(Contact.company_id == company_id).order_by(Contact.contact_type, Contact.created_at)
        return list(self.session.scalars(stmt).all())
