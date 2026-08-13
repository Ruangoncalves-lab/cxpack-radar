"""
Interface abstrata e modelos para Provedores de Pesquisa Web.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field


class SearchCandidate(BaseModel):
    """Modelo Pydantic para candidato a empresa encontrado em busca web."""
    company_name: str = Field(..., description="Nome da empresa encontrada")
    website: Optional[str] = Field(None, description="URL do site principal da empresa")
    domain: str = Field(..., description="Domínio limpo/normalizado (ex: empresa.com.br)")
    reason: Optional[str] = Field(None, description="Motivo pelo qual foi considerada fabricante/compatível")
    source_title: Optional[str] = Field(None, description="Título da página onde foi encontrada")
    source_url: Optional[str] = Field(None, description="URL da fonte original do resultado")
    query: Optional[str] = Field(None, description="Query de busca que retornou o resultado")
    confidence: float = Field(0.7, description="Nível de confiança inicial (0.0 a 1.0)")


class SearchProvider(ABC):
    @abstractmethod
    def search_candidates(
        self, query: str, max_results: int = 10
    ) -> List[SearchCandidate]:
        """Realiza busca web e retorna lista de empresas candidatas."""
        pass
