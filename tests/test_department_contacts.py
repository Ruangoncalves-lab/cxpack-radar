"""
Testes unitários para contatos de departamento e classificação de Níveis A/B/C (DepartmentContactService).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.models import Company, Contact
from services.department_contact_service import DepartmentContactService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine)
    session = SessionFactory()
    yield session
    session.close()


def test_extract_department_contacts(db_session):
    comp = Company(name="Empresa Teste", domain="empresateste.com.br")
    db_session.add(comp)
    db_session.commit()

    c1 = Contact(company_id=comp.id, contact_type="EMAIL_PUBLICO", value="compras@empresateste.com.br")
    c2 = Contact(company_id=comp.id, contact_type="EMAIL_PUBLICO", value="suprimentos@empresateste.com.br")
    db_session.add_all([c1, c2])
    db_session.commit()

    dept_service = DepartmentContactService(db_session)
    count = dept_service.extract_and_save_department_contacts(comp.id)

    assert count == 2
    dept_contacts = comp.department_contacts
    assert len(dept_contacts) == 2
    depts = [dc.department for dc in dept_contacts]
    assert "Compras" in depts
    assert "Suprimentos" in depts


def test_classify_prospecting_levels(db_session):
    comp = Company(name="Empresa Nível C", domain="nivelc.com.br")
    db_session.add(comp)
    db_session.commit()

    dept_service = DepartmentContactService(db_session)
    dept_service.dept_repo.add_department_contact(comp.id, "Compras", email="compras@nivelc.com.br")

    levels = dept_service.classify_prospecting_levels(comp.id)
    assert "NÍVEL C" in levels["best_level"]
    assert len(levels["level_c"]) == 1
