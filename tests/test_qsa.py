"""
Testes unitários para importação do QSA (QSAService).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.models import Company
from services.qsa_service import QSAService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine)
    session = SessionFactory()
    yield session
    session.close()


def test_import_qsa_partners(db_session):
    comp = Company(name="Test Indústria", domain="testind.com.br")
    db_session.add(comp)
    db_session.commit()

    qsa_service = QSAService(db_session)

    mock_qsa = [
        {"name": "Carlos Souza", "qualification": "49-SÓCIO-ADMINISTRADOR", "country": "Brasil"},
        {"name": "Ana Maria", "qualification": "22-SÓCIO", "country": "Brasil"}
    ]

    res = qsa_service.import_qsa_partners(comp.id, mock_qsa)

    assert res["success"] is True
    assert res["imported_partners"] == 2
    assert res["corporate_decision_makers"] >= 1

    partners = comp.partners
    assert len(partners) == 2
    assert partners[0].name in ["Carlos Souza", "Ana Maria"]
