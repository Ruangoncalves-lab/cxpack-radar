"""
Testes unitários para o AuthService e controle de autenticação.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from services.auth_service import AuthService, hash_password


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine)
    session = SessionFactory()
    yield session
    session.close()


def test_auth_admin_success(db_session):
    """Testa autenticação do admin padrão."""
    auth_service = AuthService(db_session)
    res = auth_service.authenticate("admin@cxpack.com.br", "admin123")
    assert res["success"] is True
    assert res["user"]["role"] == "ADMIN"
    assert res["user"]["email"] == "admin@cxpack.com.br"


def test_auth_invalid_credentials(db_session):
    """Testa falha de autenticação com credenciais incorretas."""
    auth_service = AuthService(db_session)
    res = auth_service.authenticate("admin@cxpack.com.br", "senha_errada")
    assert res["success"] is False
    assert "inválidos" in res["message"]


def test_hash_password():
    """Testa geração de hash SHA-256."""
    h1 = hash_password("admin123")
    h2 = hash_password("admin123")
    assert h1 == h2
    assert len(h1) == 64
