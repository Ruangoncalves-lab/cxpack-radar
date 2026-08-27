"""
Testes unitários para o ExtractionService (E-mails, telefones, WhatsApp e CNPJ).
"""

from services.extraction_service import ExtractionService


def test_extract_contacts_from_html():
    extractor = ExtractionService()
    sample_html = """
    <html>
        <body>
            <p>Entre em contato conosco pelo e-mail: contato@empresaembalagens.com.br</p>
            <p>Telefone: (11) 4004-1234 ou WhatsApp: (11) 98765-4321</p>
            <a href="mailto:vendas@empresaembalagens.com.br">Fale com Vendas</a>
            <a href="https://wa.me/5511987654321">Falar no WhatsApp</a>
            <a href="tel:+551140041234">Ligar para a empresa</a>
            <footer>CNPJ: 12.345.678/0001-90</footer>
        </body>
    </html>
    """
    contacts = extractor.extract_contacts_from_html(sample_html, "https://empresaembalagens.com.br")
    values = [c["value"] for c in contacts]

    assert "contato@empresaembalagens.com.br" in values
    assert "vendas@empresaembalagens.com.br" in values
    assert "(11) 4004-1234" in values
    assert "(11) 98765-4321" in values

    whatsapp = next(c for c in contacts if c["value"] == "(11) 98765-4321")
    assert whatsapp["contact_type"] == "WHATSAPP"

    cnpj = extractor.extract_cnpj(sample_html)
    assert cnpj == "12.345.678/0001-90"
