"""
Serviço de cache de pesquisas (CacheService).
Evita requisições redundantes de API verificando o histórico do banco de dados.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from utils.normalization import generate_search_hash
from database.repositories.searches import SearchRepository


class CacheService:
    def __init__(self, session: Session):
        self.search_repo = SearchRepository(session)

    def check_cache(
        self,
        product: str,
        capacity: Optional[str] = None,
        material: Optional[str] = None,
        location: Optional[str] = "Brasil",
        company_type: Optional[str] = "Fabricante"
    ) -> Dict[str, Any]:
        """
        Calcula o search_hash e consulta se a pesquisa foi realizada nos últimos 30 dias.
        Retorna dicionário com o resultado do cache.
        """
        search_hash = generate_search_hash(product, capacity, material, location, company_type)
        existing_search = self.search_repo.get_recent_completed_search_by_hash(search_hash)

        if existing_search:
            days_ago = (datetime.now() - existing_search.created_at).days
            return {
                "hit": True,
                "search_hash": search_hash,
                "existing_search_id": existing_search.id,
                "created_at": existing_search.created_at,
                "days_ago": days_ago,
                "companies_found": existing_search.companies_found,
                "message": f"Esta busca já foi realizada há {days_ago} dias ({existing_search.created_at.strftime('%d/%m/%Y')})."
            }

        return {
            "hit": False,
            "search_hash": search_hash,
            "existing_search_id": None,
            "days_ago": 0,
            "companies_found": 0,
            "message": "Nenhum cache recente encontrado. Nova busca pronta para ser executada."
        }
