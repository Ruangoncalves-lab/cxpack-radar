"""
Testes unitários para a gestão de colaboradores e membros da equipe (TeamService).
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from services.team_service import TeamService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionFactory = sessionmaker(bind=engine)
    session = SessionFactory()
    yield session
    session.close()


def test_add_and_toggle_team_member(db_session):
    ts = TeamService(db_session)
    res = ts.add_member("Sérgio", "sergio@empresa.com.br")

    assert res["success"] is True
    assert res["name"] == "Sérgio"

    active_members = ts.list_active_members()
    assert len(active_members) == 1
    assert active_members[0].email == "sergio@empresa.com.br"

    # Alternar status
    toggle_res = ts.toggle_member_active(res["member_id"])
    assert toggle_res["active"] is False
    assert len(ts.list_active_members()) == 0
