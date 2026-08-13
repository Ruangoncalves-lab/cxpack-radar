"""
Repositório para gerenciamento de Páginas Crawleadas no banco de dados.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models import Page


class PageRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_page(
        self,
        company_id: int,
        url: str,
        status_code: int = 200,
        status: str = "COMPLETED",
        title: Optional[str] = None,
        content_text: Optional[str] = None
    ) -> Page:
        """Salva um registro de página visitada pelo crawler."""
        page = Page(
            company_id=company_id,
            url=url,
            status_code=status_code,
            status=status,
            title=title,
            content_text=content_text
        )
        self.session.add(page)
        self.session.commit()
        return page

    def get_company_pages(self, company_id: int) -> List[Page]:
        """Retorna todas as páginas crawleadas de uma empresa."""
        stmt = select(Page).where(Page.company_id == company_id).order_by(Page.crawled_at.desc())
        return list(self.session.scalars(stmt).all())
