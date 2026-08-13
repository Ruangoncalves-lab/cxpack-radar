"""
Repositório para consulta e salvamento de uso de API (api_usage) e buscas web.
"""

from datetime import datetime, date
from typing import Optional
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session
from database.models import APIUsage


class UsageRepository:
    def __init__(self, session: Session):
        self.session = session

    def log_usage(
        self,
        operation: str,
        provider: str = "ddgs",
        user_or_operator: str = "sistema",
        search_id: Optional[int] = None,
        request_count: int = 1,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> APIUsage:
        """Registra uma nova operação de busca web ou chamada de IA."""
        record = APIUsage(
            provider=provider,
            operation=operation,
            user_or_operator=user_or_operator,
            search_id=search_id,
            request_count=request_count,
            success=success,
            error_message=error_message
        )
        self.session.add(record)
        self.session.commit()
        return record

    def get_today_grounded_calls_count(self) -> int:
        """Retorna o total de buscas web realizadas hoje no sistema."""
        today_start = datetime.combine(date.today(), datetime.min.time())
        stmt = (
            select(func.coalesce(func.sum(APIUsage.request_count), 0))
            .where(
                or_(
                    APIUsage.operation == "ddgs_web_search",
                    APIUsage.operation == "gemini_grounded_search",
                    APIUsage.operation == "web_search"
                )
            )
            .where(APIUsage.created_at >= today_start)
            .where(APIUsage.success == True)
        )
        return self.session.scalar(stmt) or 0

    def get_today_user_grounded_calls_count(self, user_or_operator: str) -> int:
        """Retorna o total de buscas web realizadas hoje por um usuário específico."""
        today_start = datetime.combine(date.today(), datetime.min.time())
        stmt = (
            select(func.coalesce(func.sum(APIUsage.request_count), 0))
            .where(
                or_(
                    APIUsage.operation == "ddgs_web_search",
                    APIUsage.operation == "gemini_grounded_search",
                    APIUsage.operation == "web_search"
                )
            )
            .where(APIUsage.user_or_operator == user_or_operator)
            .where(APIUsage.created_at >= today_start)
            .where(APIUsage.success == True)
        )
        return self.session.scalar(stmt) or 0

    def get_today_usage(self, provider: Optional[str] = None):
        """Retorna todas as requisições registradas hoje."""
        today_start = datetime.combine(date.today(), datetime.min.time())
        stmt = select(APIUsage).where(APIUsage.created_at >= today_start)
        if provider:
            stmt = stmt.where(APIUsage.provider == provider)
        stmt = stmt.order_by(APIUsage.created_at.desc())
        return list(self.session.scalars(stmt).all())
