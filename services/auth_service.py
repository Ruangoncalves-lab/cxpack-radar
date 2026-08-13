"""
Serviço de Autenticação e Gestão de Sessão (AuthService).
Gerencia login de usuários, hash de senhas e sessão ativa no Streamlit.
"""

import hashlib
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models import TeamMember
from database.repositories.settings import SettingsRepository


def hash_password(password: str) -> str:
    """Gera hash SHA-256 seguro para a senha."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.settings_repo = SettingsRepository(session)

    def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """
        Valida as credenciais digitadas pelo usuário.
        Aceita o admin padrão (admin@cxpack.com.br / admin123) ou membros cadastrados na equipe.
        """
        clean_email = email.strip().lower()
        clean_password = password.strip()

        if not clean_email or not clean_password:
            return {"success": False, "message": "Preencha o e-mail e a senha."}

        # 1. Checar credencial de Admin Padrão
        admin_email = "admin@cxpack.com.br"
        admin_pass = "admin123"

        saved_admin_pass = self.settings_repo.get("ADMIN_PASSWORD", admin_pass)

        if clean_email == admin_email and clean_password == saved_admin_pass:
            return {
                "success": True,
                "message": "Login realizado com sucesso!",
                "user": {
                    "email": admin_email,
                    "name": "Administrador CXPack",
                    "role": "ADMIN"
                }
            }

        # 2. Checar membros da equipe no banco
        stmt = select(TeamMember).where(TeamMember.email == clean_email)
        member = self.session.scalar(stmt)

        if member and member.active:
            return {
                "success": True,
                "message": f"Bem-vindo(a), {member.name}!",
                "user": {
                    "email": member.email,
                    "name": member.name,
                    "role": "MEMBER"
                }
            }

        return {
            "success": False,
            "message": "E-mail ou senha inválidos. Verifique suas credenciais."
        }
