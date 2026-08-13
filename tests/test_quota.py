"""
Testes unitários para o controle de cota e limites internos de busca web.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.usage import UsageRepository
from services.quota_service import QuotaService
from core.exceptions import QuotaExceededError


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine)
    session = SessionFactory()
    yield session
    session.close()


def test_quota_limit_exceeded(db_session):
    usage_repo = UsageRepository(db_session)
    # Simular limite interno atingido (500 buscas web hoje)
    usage_repo.log_usage(
        operation="ddgs_web_search",
        user_or_operator="sistema",
        request_count=500,
        success=True
    )

    quota_service = QuotaService(db_session)
    with pytest.raises(QuotaExceededError):
        quota_service.check_quota_available(requested_calls=1, user_or_operator="sistema")
