"""
Testes unitários para o serviço de exportação (ExportService).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.models import Company
from services.export_service import ExportService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine)
    session = SessionFactory()
    yield session
    session.close()


def test_export_csv_and_xlsx(db_session):
    comp = Company(
        name="Plásticos Brasil",
        domain="plasticosbrasil.com.br",
        company_type="FABRICANTE",
        score=85,
        city="São Paulo",
        state="SP"
    )
    db_session.add(comp)
    db_session.commit()

    exporter = ExportService(db_session)

    # Validar DataFrame
    df = exporter.build_export_dataframe()
    assert len(df) == 1
    assert df.iloc[0]["Empresa"] == "Plásticos Brasil"
    assert df.iloc[0]["Tipo"] == "FABRICANTE"

    # Validar geração de bytes CSV (UTF-8-SIG)
    csv_bytes = exporter.export_to_csv()
    assert isinstance(csv_bytes, bytes)
    assert len(csv_bytes) > 0
    assert "Plásticos Brasil".encode("utf-8") in csv_bytes

    # Validar geração de bytes XLSX (Excel)
    xlsx_bytes = exporter.export_to_xlsx()
    assert isinstance(xlsx_bytes, bytes)
    assert len(xlsx_bytes) > 0
