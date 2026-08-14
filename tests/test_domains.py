"""
Testes unitários para normalização de domínios e filtro de blacklist.
"""

from utils.domains import normalize_domain, is_blacklisted


def test_normalize_domain():
    assert normalize_domain("https://www.empresa.com.br/produtos") == "empresa.com.br"
    assert normalize_domain("http://empresa.com.br/") == "empresa.com.br"
    assert normalize_domain("https://empresa.com.br/catalogo?id=123") == "empresa.com.br"
    assert normalize_domain("sub.empresa.com.br") == "sub.empresa.com.br"


def test_is_blacklisted():
    assert is_blacklisted("https://www.mercadolivre.com.br/item123") is True
    assert is_blacklisted("amazon.com.br") is True
    assert is_blacklisted("instagram.com") is True
    assert is_blacklisted("https://produtos.solucoesindustriais.com.br/item") is True
    assert is_blacklisted("https://www.empresaembalagens.com.br") is False
