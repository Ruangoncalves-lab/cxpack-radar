"""
Gerenciamento de conexão com o banco de dados via SQLAlchemy 2.x.
Suporta SQLite local por padrão ou PostgreSQL/Supabase via DATABASE_URL.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from core.config import DEFAULT_SQLITE_URL
from core.secrets import get_secret


class Base(DeclarativeBase):
    """Classe base declarativa do SQLAlchemy 2.x."""
    pass


def get_database_url() -> str:
    """
    Retorna a URL do banco de dados.
    Procura DATABASE_URL nos segredos; se não encontrar, utiliza SQLite local.
    """
    db_url = get_secret("DATABASE_URL")
    if db_url and db_url.strip():
        # Ajustar prefixo postgres:// para postgresql:// se necessário para SQLAlchemy 2.x
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return db_url
    return DEFAULT_SQLITE_URL


# Inicialização do Engine e SessionFactory
_engine = None
_SessionFactory = None


def get_engine():
    """Retorna o engine global do SQLAlchemy."""
    global _engine
    if _engine is None:
        url = get_database_url()
        # Argumentos específicos para SQLite
        connect_args = {}
        if url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}

        _engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True)
    return _engine


def get_session_factory():
    """Retorna a fábrica de sessões do SQLAlchemy."""
    global _SessionFactory
    if _SessionFactory is None:
        engine = get_engine()
        _SessionFactory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return _SessionFactory


def init_db():
    """Cria todas as tabelas no banco de dados se não existirem."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def get_db_session() -> Generator[Session, None, None]:
    """Gerador de sessão do SQLAlchemy para ser usado em serviços e contextos."""
    SessionFactory = get_session_factory()
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def test_db_connection() -> tuple[bool, str]:
    """
    Testa a conexão com o banco de dados.
    Retorna (sucesso: bool, mensagem: str).
    """
    try:
        engine = get_engine()
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        db_url = get_database_url()
        mode = "PostgreSQL / Cloud" if "postgresql" in db_url else "SQLite Local"
        return True, f"Conexão realizada com sucesso ({mode})."
    except Exception as e:
        return False, f"Erro ao conectar ao banco de dados: {str(e)}"
