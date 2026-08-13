"""
Interface abstrata para Provedores de Dados de CNPJ (CNPJDataProvider).
Garante que a origem dos dados públicos (BrasilAPI, MinhaReceita, Serpro, Dados Abertos) possa ser alternada facilmente.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class CNPJDataProvider(ABC):
    @abstractmethod
    def get_company_by_cnpj(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Busca os dados cadastrais da empresa pelo número de CNPJ.
        Retorna dicionário padronizado ou None se não encontrado.
        """
        pass

    @abstractmethod
    def get_partners(self, cnpj: str) -> List[Dict[str, Any]]:
        """
        Retorna o Quadro de Sócios e Administradores (QSA) associado ao CNPJ.
        """
        pass

    @abstractmethod
    def search_cnpj_by_name_or_domain(
        self, company_name: str, domain: Optional[str] = None, city: Optional[str] = None, state: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Busca candidatos a CNPJ com base no nome da empresa, domínio, cidade e UF.
        """
        pass
