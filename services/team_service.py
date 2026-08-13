"""
Serviço de Gestão de Membros da Equipe (TeamService - Fase 6).
Permite gerenciar colaboradores para atribuição de leads sem armazenar senhas.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models import TeamMember
from utils.emails import is_valid_email_format


class TeamService:
    def __init__(self, session: Session):
        self.session = session

    def add_member(self, name: str, email: str) -> Dict[str, Any]:
        """Adiciona um novo membro à equipe."""
        clean_name = name.strip().title()
        clean_email = email.strip().lower()

        if not clean_name:
            return {"success": False, "message": "Nome do membro é obrigatório."}

        if not is_valid_email_format(clean_email):
            return {"success": False, "message": "E-mail inválido."}

        stmt = select(TeamMember).where(TeamMember.email == clean_email)
        existing = self.session.scalar(stmt)
        if existing:
            return {"success": False, "message": f"Já existe um membro cadastrado com o e-mail '{clean_email}'."}

        member = TeamMember(name=clean_name, email=clean_email, active=True)
        self.session.add(member)
        self.session.commit()

        return {"success": True, "member_id": member.id, "name": member.name, "email": member.email}

    def toggle_member_active(self, member_id: int) -> Dict[str, Any]:
        """Alterna o status de um membro entre Ativo e Inativo."""
        member = self.session.get(TeamMember, member_id)
        if not member:
            return {"success": False, "message": "Membro não encontrado."}

        member.active = not member.active
        self.session.commit()
        return {"success": True, "member_id": member.id, "active": member.active}

    def list_active_members(self) -> List[TeamMember]:
        """Retorna apenas os membros da equipe que estão ativos."""
        stmt = select(TeamMember).where(TeamMember.active == True).order_by(TeamMember.name)
        return list(self.session.scalars(stmt).all())

    def list_all_members(self) -> List[TeamMember]:
        """Retorna todos os membros cadastrados."""
        stmt = select(TeamMember).order_by(TeamMember.active.desc(), TeamMember.name)
        return list(self.session.scalars(stmt).all())
