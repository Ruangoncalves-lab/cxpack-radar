"""
Repositório para gerenciamento de Pesquisas (Searches), Queries e Resultados.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from database.models import Search, SearchQuery, SearchResult, Company
from core.config import CACHE_EXPIRATION_DAYS


class SearchRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_recent_completed_search_by_hash(
        self, search_hash: str, expiration_days: int = CACHE_EXPIRATION_DAYS
    ) -> Optional[Search]:
        """
        Busca uma pesquisa concluída recentemente com o mesmo search_hash (Cache).
        """
        cutoff_date = datetime.now() - timedelta(days=expiration_days)
        stmt = (
            select(Search)
            .where(
                and_(
                    Search.search_hash == search_hash,
                    Search.status == "COMPLETED",
                    Search.created_at >= cutoff_date
                )
            )
            .order_by(Search.created_at.desc())
        )
        return self.session.scalar(stmt)

    def create_search(
        self,
        search_hash: str,
        product: str,
        capacity: Optional[str] = None,
        material: Optional[str] = None,
        location: str = "Brasil",
        company_type: str = "Fabricante",
        operator: str = "sistema"
    ) -> Search:
        """Cria um novo registro de pesquisa com status CREATED."""
        search = Search(
            search_hash=search_hash,
            product=product,
            capacity=capacity,
            material=material,
            location=location,
            company_type=company_type,
            status="CREATED",
            operator=operator
        )
        self.session.add(search)
        self.session.commit()
        return search

    def update_status(
        self, search_id: int, status: str, error_message: Optional[str] = None
    ) -> Search:
        """Atualiza o status da pesquisa (CREATED, RUNNING, COMPLETED, FAILED)."""
        search = self.session.get(Search, search_id)
        if search:
            search.status = status
            if status == "RUNNING" and not search.started_at:
                search.started_at = datetime.now()
            elif status in ("COMPLETED", "FAILED"):
                search.completed_at = datetime.now()
            if error_message:
                search.error_message = error_message
            self.session.commit()
        return search

    def add_query(self, search_id: int, query_text: str, query_type: str = "LOCAL_TEMPLATE") -> SearchQuery:
        """Adiciona uma query gerada à pesquisa."""
        sq = SearchQuery(search_id=search_id, query_text=query_text, query_type=query_type)
        self.session.add(sq)
        self.session.commit()
        return sq

    def add_result(
        self,
        search_id: int,
        domain: str,
        company_id: Optional[int] = None,
        source_url: Optional[str] = None,
        source_title: Optional[str] = None,
        confidence: float = 0.0,
        reason: Optional[str] = None
    ) -> SearchResult:
        """Adiciona um resultado à pesquisa."""
        sr = SearchResult(
            search_id=search_id,
            company_id=company_id,
            domain=domain,
            source_url=source_url,
            source_title=source_title,
            confidence=confidence,
            reason=reason
        )
        self.session.add(sr)
        self.session.commit()
        return sr

    def get_search_with_results(self, search_id: int) -> Optional[Search]:
        """Carrega a pesquisa com suas queries e resultados."""
        return self.session.get(Search, search_id)

    def list_searches(self, limit: int = 50) -> List[Search]:
        """Lista as pesquisas mais recentes."""
        stmt = select(Search).order_by(Search.created_at.desc()).limit(limit)
        return list(self.session.scalars(stmt).all())
