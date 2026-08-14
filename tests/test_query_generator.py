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
    assert all("500 ml" in query and "PET" in query and "Brasil" in query for query in queries)


def test_generate_queries_corrects_common_product_typo():
    queries = QueryGenerator().generate_queries("farsco", "500 ml", "resina", "Brasil")
    assert all("frasco" in query for query in queries)
