"""
Testes unitários para o algoritmo de matching empresa ↔ CNPJ (CNPJMatchingService).
"""

from services.cnpj_matching_service import CNPJMatchingService, AUTO_CNPJ_MATCH_MIN_SCORE


def test_cnpj_match_score_high_confidence():
    matcher = CNPJMatchingService()

    res = matcher.calculate_match_score(
        company_name="Plásticos Indústria e Comércio",
        cnpj_legal_name="PLÁSTICOS INDÚSTRIA E COMÉRCIO LTDA",
        cnpj_trade_name="Plásticos Indústria",
        company_city="Joinville",
        cnpj_city="Joinville",
        company_state="SC",
        cnpj_state="SC",
        company_phone="4733334444",
        cnpj_phone="4733334444",
        company_domain="plasticosind.com.br",
        cnpj_email="contato@plasticosind.com.br"
    )

    assert res["match_score"] >= AUTO_CNPJ_MATCH_MIN_SCORE
    assert res["is_auto_matched"] is True
    assert res["status"] == "AUTO_MATCHED"


def test_cnpj_match_score_low_confidence():
    matcher = CNPJMatchingService()

    res = matcher.calculate_match_score(
        company_name="Embalagens ABC",
        cnpj_legal_name="XYZ SERVIÇOS TÉCNICOS LTDA",
        company_city="São Paulo",
        cnpj_city="Curitiba",
        company_state="SP",
        cnpj_state="PR"
    )

    assert res["match_score"] < AUTO_CNPJ_MATCH_MIN_SCORE
    assert res["is_auto_matched"] is False
    assert res["status"] == "CNPJ_MATCH_REVIEW"
