"""
Modelos de Dados do SQLAlchemy 2.x para o CXPack Radar.
Inclui tabelas para Empresas, Buscas, Evidências, Contatos, Decisores, Páginas, QSA (Sócios), Contatos de Departamento e Match de CNPJ.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, Float, Boolean, Text, DateTime, ForeignKey, Index, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.connection import Base


class Company(Base):
    """Tabela principal de Empresas/Fornecedores industriais."""
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    trade_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    domain: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    website: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cnpj: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, index=True)
    status_cadastral: Mapped[Optional[str]] = mapped_column(String(50), default="ATIVA")
    cnae_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    cnae_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    capital_social: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    company_type: Mapped[str] = mapped_column(String(50), default="DESCONHECIDO")  # FABRICANTE, DISTRIBUIDOR, etc.
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    country: Mapped[str] = mapped_column(String(50), default="Brasil")
    score: Mapped[int] = mapped_column(Integer, default=0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)

    # CRM Básico
    crm_status: Mapped[str] = mapped_column(String(50), default="NOVO")  # NOVO, INTERESSANTE, CONTATAR, etc.
    assigned_to: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    last_crawled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_decision_maker_search_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    # Relacionamentos
    evidences: Mapped[List["Evidence"]] = relationship("Evidence", back_populates="company", cascade="all, delete-orphan")
    pages: Mapped[List["Page"]] = relationship("Page", back_populates="company", cascade="all, delete-orphan")
    contacts: Mapped[List["Contact"]] = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    decision_makers: Mapped[List["DecisionMaker"]] = relationship("DecisionMaker", back_populates="company", cascade="all, delete-orphan")
    partners: Mapped[List["CompanyPartner"]] = relationship("CompanyPartner", back_populates="company", cascade="all, delete-orphan")
    department_contacts: Mapped[List["DepartmentContact"]] = relationship("DepartmentContact", back_populates="company", cascade="all, delete-orphan")
    cnpj_matches: Mapped[List["CNPJMatch"]] = relationship("CNPJMatch", back_populates="company", cascade="all, delete-orphan")


class CompanyPartner(Base):
    """Quadro de Sócios e Administradores (QSA)."""
    __tablename__ = "company_partners"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    qualification: Mapped[str] = mapped_column(String(100), default="SOCIO")  # SOCIO, SOCIO_ADMINISTRADOR, ADMINISTRADOR, etc.
    country: Mapped[str] = mapped_column(String(100), default="Brasil")
    legal_representative: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="Dados Abertos CNPJ / Receita Federal")
    source_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="partners")


class DepartmentContact(Base):
    """Contatos por departamento (ex: compras@, suprimentos@, fornecedores@)."""
    __tablename__ = "department_contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)  # Compras, Suprimentos, Procurement, Fornecedores
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    whatsapp: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.9)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="department_contacts")


class CNPJMatch(Base):
    """Histórico de matching e validação entre Empresa e CNPJ."""
    __tablename__ = "cnpj_matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    cnpj: Mapped[str] = mapped_column(String(20), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trade_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    cnae_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    cnae_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cnaes_secondary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status_cadastral: Mapped[Optional[str]] = mapped_column(String(50), default="ATIVA")
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    capital_social: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    match_score: Mapped[int] = mapped_column(Integer, default=0)
    is_auto_matched: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="cnpj_matches")


class DecisionMaker(Base):
    """Tomadores de decisão e profissionais associados às empresas (Societários & Operacionais)."""
    __tablename__ = "decision_makers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(255), nullable=False)  # Cargo
    department: Mapped[Optional[str]] = mapped_column(String(100), default="Compras")  # Compras, Suprimentos, Diretoria, etc.
    decision_maker_type: Mapped[str] = mapped_column(String(50), default="OPERATIONAL")  # CORPORATE (Societário) vs OPERATIONAL (Comprador/Diretor)
    decision_priority: Mapped[int] = mapped_column(Integer, default=5)  # 1 = Alta Prioridade (Compras), 10 = Sócios
    decision_maker_score: Mapped[int] = mapped_column(Integer, default=70)  # Pontuação de atratividade (60 a 100)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email_status: Mapped[str] = mapped_column(String(50), default="INFERIDO")  # PUBLICADO, DEPARTAMENTO, INFERIDO, NAO_CONFIRMADO
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    raw_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.7)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="decision_makers")


class Page(Base):
    """Páginas visitadas pelo crawler para cada empresa."""
    __tablename__ = "pages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, default=200)
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED")  # COMPLETED, BLOCKED, NEEDS_BROWSER, TIMEOUT
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    crawled_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="pages")


class Contact(Base):
    """Contatos públicos extraídos do website da empresa."""
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    contact_type: Mapped[str] = mapped_column(String(50), nullable=False)  # EMAIL_PUBLICO, TELEFONE, WHATSAPP
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_value: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="contacts")


class Search(Base):
    """Tabela de pesquisas realizadas pelos usuários (Idempotência e Cache)."""
    __tablename__ = "searches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    search_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    product: Mapped[str] = mapped_column(String(255), nullable=False)
    capacity: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    material: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), default="Brasil")
    company_type: Mapped[Optional[str]] = mapped_column(String(50), default="Fabricante")

    # Estados: CREATED, RUNNING, COMPLETED, FAILED
    status: Mapped[str] = mapped_column(String(30), default="CREATED")
    operator: Mapped[Optional[str]] = mapped_column(String(255), default="sistema")

    grounded_calls: Mapped[int] = mapped_column(Integer, default=0)
    companies_found: Mapped[int] = mapped_column(Integer, default=0)
    new_companies_found: Mapped[int] = mapped_column(Integer, default=0)

    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    queries: Mapped[List["SearchQuery"]] = relationship("SearchQuery", back_populates="search", cascade="all, delete-orphan")
    results: Mapped[List["SearchResult"]] = relationship("SearchResult", back_populates="search", cascade="all, delete-orphan")


class SearchQuery(Base):
    """Queries geradas para cada pesquisa."""
    __tablename__ = "search_queries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    search_id: Mapped[int] = mapped_column(Integer, ForeignKey("searches.id", ondelete="CASCADE"), nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[str] = mapped_column(String(50), default="LOCAL_TEMPLATE")  # LOCAL_TEMPLATE, GROUNDED
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    search: Mapped["Search"] = relationship("Search", back_populates="queries")


class SearchResult(Base):
    """Resultados vinculados a uma pesquisa."""
    __tablename__ = "search_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    search_id: Mapped[int] = mapped_column(Integer, ForeignKey("searches.id", ondelete="CASCADE"), nullable=False)
    company_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    search: Mapped["Search"] = relationship("Search", back_populates="results")


class Evidence(Base):
    """Evidências que comprovam dados das empresas (URLs, trechos do site)."""
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    decision_maker_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)  # ex: company_type, product_match
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    company: Mapped["Company"] = relationship("Company", back_populates="evidences")


class APIUsage(Base):
    """Registro de chamadas de API (Controle de Cota e Custo)."""
    __tablename__ = "api_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(50), default="gemini")
    operation: Mapped[str] = mapped_column(String(100), nullable=False)  # gemini_grounded_search, gemini_analysis
    user_or_operator: Mapped[str] = mapped_column(String(255), default="sistema")
    search_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    request_count: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class TeamMember(Base):
    """Membros da equipe para atribuição de leads (Sem senhas)."""
    __tablename__ = "team_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


class Synonym(Base):
    """Dicionário configurável de sinônimos industriais."""
    __tablename__ = "synonyms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # FRASCO, BISNAGA, FABRICANTE, etc.
    term: Mapped[str] = mapped_column(String(100), nullable=False)
    synonyms_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON com lista de sinônimos
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class SystemSetting(Base):
    """Configurações dinâmicas do sistema em banco de dados."""
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
