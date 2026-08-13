"""
Testes unitários para o DDGSSearchProvider.
"""

from unittest.mock import patch, MagicMock
from providers.search.ddgs_provider import DDGSSearchProvider
from providers.search.base import SearchCandidate


def test_ddgs_provider_search_candidates_mocked():
    """Testa se o DDGSSearchProvider normaliza e deduplica os resultados do DDGS."""
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = [
        {
            "title": "Empresa Alfa - Frascos Plásticos",
            "href": "https://www.empresaalfa.com.br/produtos",
            "body": "Fabricante de frascos plásticos PET em São Paulo."
        },
        {
            "title": "Empresa Alfa | Contatos",
            "href": "https://empresaalfa.com.br/contato",
            "body": "Entre em contato com a fábrica."
        },
        {
            "title": "Mercado Livre - Frascos",
            "href": "https://www.mercadolivre.com.br/frascos",
            "body": "Compre frascos plásticos online."
        },
        {
            "title": "Empresa Beta Embalagens",
            "href": "https://www.empresabeta.com.br",
            "body": "Indústria de embalagens PET 500ml."
        }
    ]

    with patch("providers.search.ddgs_provider.DDGS") as mock_ddgs_class:
        mock_ddgs_class.return_value.__enter__.return_value = mock_ddgs_instance

        provider = DDGSSearchProvider(delay_seconds=0.0, max_retries=1)
        candidates = provider.search_candidates("frasco pet 500ml", max_results=10)

        # 1. Verifica deduplicação (empresaalfa.com.br deve aparecer 1 vez)
        # 2. Verifica blacklist (mercadolivre.com.br deve ser ignorado)
        domains = [c.domain for c in candidates]
        assert "empresaalfa.com.br" in domains
        assert "empresabeta.com.br" in domains
        assert "mercadolivre.com.br" not in domains
        assert len(candidates) == 2


def test_ddgs_provider_failure_resilience():
    """Testa a resiliência do provider quando o DDGS levanta exceção."""
    with patch("providers.search.ddgs_provider.DDGS") as mock_ddgs_class:
        mock_ddgs_class.return_value.__enter__.side_effect = Exception("Rate limit temporário")

        provider = DDGSSearchProvider(delay_seconds=0.0, max_retries=1)
        candidates = provider.search_candidates("frasco pet", max_results=5)

        # Não deve quebrar com exceção unhandled, apenas retornar lista vazia
        assert candidates == []
