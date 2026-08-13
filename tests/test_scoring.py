"""
Testes unitários para a calculadora determinística de Score (ScoringService).
"""

from services.scoring_service import ScoringService


def test_calculate_score_manufacturer():
    scoring = ScoringService()
    res = scoring.calculate_score(
        company_type="FABRICANTE",
        product_matched=True,
        material_matched=True,
        capacity_matched=True,
        location_matched=True,
        has_phone=True,
        has_email=True,
        has_decision_maker=False
    )
    # 30 (Fabricante) + 25 (Produto) + 15 (Material) + 15 (Capacidade) + 5 (Local) + 3 (Fone) + 3 (Email) = 96
    assert res["total_score"] == 96
    assert len(res["breakdown"]) == 7


def test_calculate_score_distributor():
    scoring = ScoringService()
    res = scoring.calculate_score(
        company_type="DISTRIBUIDOR",
        product_matched=True,
        material_matched=False,
        capacity_matched=False,
        location_matched=True,
        has_phone=False,
        has_email=False,
        has_decision_maker=False
    )
    # 15 (Distribuidor) + 25 (Produto) + 5 (Local) = 45
    assert res["total_score"] == 45
