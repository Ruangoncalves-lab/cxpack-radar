"""
Testes unitários para o gerenciamento de leads e Mini CRM (CRMService).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.models import Company
from services.crm_service import CRMService, VALID_CRM_STATUSES


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine)
    session = SessionFactory()
    yield session
    session.close()


def test_update_lead_status(db_session):
    comp = Company(name="Test Indústria", domain="testind.com.br", crm_status="NOVO")
    db_session.add(comp)
    db_session.commit()

    crm = CRMService(db_session)
    res = crm.update_lead_status(comp.id, "COTACAO_SOLICITADA")

    assert res["success"] is True
    assert comp.crm_status == "COTACAO_SOLICITADA"


def test_assign_lead_and_notes(db_session):
    comp = Company(name="Test Indústria 2", domain="testind2.com.br")
    db_session.add(comp)
    db_session.commit()

    crm = CRMService(db_session)
    crm.assign_lead(comp.id, "Sérgio")
    crm.update_lead_notes(comp.id, "Cliente solicitou catálogo de frascos PET 500ml.")

    assert comp.assigned_to == "Sérgio"
    assert "catálogo de frascos" in comp.notes
