"""
Testes unitários para a busca, inferência de e-mails e validação MX (DecisionMakerService).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from unittest.mock import MagicMock
from services.decision_maker_service import DecisionMakerService


def test_infer_email_pattern():
    dm_service = DecisionMakerService(None)
    email1 = dm_service.infer_email_pattern("Maria Souza Lima", "empresa.com.br")
    assert email1 == "maria.lima@empresa.com.br"

    email2 = dm_service.infer_email_pattern("Carlos", "empresa.com.br")
    assert email2 == "carlos@empresa.com.br"


def test_check_mx_record():
    dm_service = DecisionMakerService(None)
    # Testar com domínios conhecidos com servidores MX válidos
    assert dm_service.check_mx_record("google.com") is True
    assert dm_service.check_mx_record("dominioinvalido123456789.xyz") is False


def test_low_score_company_can_still_be_enriched():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine)
    session = SessionFactory()

    from database.models import Company
    comp_low = Company(name="Inativa", domain="inativa.com.br", score=40)
    session.add(comp_low)
    session.commit()

    ddgs = MagicMock()
    ddgs.search_candidates.return_value = []
    gemini = MagicMock()
    gemini.is_available.return_value = False
    dm_service = DecisionMakerService(session, ddgs_provider=ddgs, gemini_provider=gemini)
    dm_service.check_mx_record = lambda domain: False
    res = dm_service.search_decision_makers(comp_low.id)

    assert res["success"] is True
    ddgs.search_candidates.assert_called_once()
