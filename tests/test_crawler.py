"""
Testes unitários para o CrawlerService (Priorização de links e verificação de domínio).
"""

from services.crawler_service import CrawlerService


def test_is_same_domain():
    crawler = CrawlerService()
    assert crawler._is_same_domain("https://www.empresa.com.br/contato", "empresa.com.br") is True
    assert crawler._is_same_domain("https://sub.empresa.com.br/sobre", "empresa.com.br") is True
    assert crawler._is_same_domain("https://outraempresa.com.br", "empresa.com.br") is False


def test_discover_priority_links():
    crawler = CrawlerService()
    sample_html = """
    <html>
        <body>
            <a href="/contato">Contato</a>
            <a href="/produtos">Nossos Produtos</a>
            <a href="https://facebook.com/empresa">Facebook</a>
            <a href="/sobre-nos">Sobre Nós</a>
            <a href="/catalogo.pdf">Catálogo PDF</a>
        </body>
    </html>
    """
    links = crawler.discover_priority_links("https://www.empresa.com.br", sample_html)
    assert len(links) >= 3
    # Garantir que links de outros domínios foram ignorados
    assert not any("facebook.com" in l for l in links)
    # Garantir que /contato e /produtos receberam maior prioridade
    assert "contato" in links[0] or "produto" in links[0] or "sobre" in links[0]
