"""
Testes unitários para o gerador local de queries (QueryGenerator).
"""

from services.query_generator import QueryGenerator


def test_generate_queries_basic():
    qg = QueryGenerator()
    queries = qg.generate_queries(
        product="frasco plástico",
        capacity="500 ml",
        material="PET",
        location="Brasil",
        company_type="Fabricante",
        max_queries=3
    )

    assert len(queries) == 3
    assert "Fabricante" in queries[0] or "fabricante" in queries[0]
    assert "PET" in queries[0]
    assert "500 ml" in queries[0]
