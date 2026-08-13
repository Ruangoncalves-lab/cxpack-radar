"""
Testes unitários para geração de hash de pesquisa e detecção de cache.
"""

from utils.normalization import generate_search_hash


def test_generate_search_hash_deterministic():
    hash1 = generate_search_hash("frasco plástico", "500 ml", "PET", "Brasil", "Fabricante")
    hash2 = generate_search_hash("Frasco Plástico ", "500 ml", "pet", "brasil", "fabricante")

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex digest length
