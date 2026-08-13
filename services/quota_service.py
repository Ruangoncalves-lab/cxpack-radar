"""
Serviço de gerenciamento de cotas e limites internos (QuotaService).
Garante uso responsável com limites internos de segurança para Busca Web (DDGS) e Inteligência Artificial (Gemini).
"""

from typing import Dict, Any
from sqlalchemy.orm import Session
from core.config import (
    MAX_WEB_SEARCHES_TOTAL_DAY,
    MAX_WEB_SEARCHES_PER_USER_DAY
)
from core.exceptions import QuotaExceededError
from database.repositories.usage import UsageRepository


class QuotaService:
    def __init__(self, session: Session):
        self.usage_repo = UsageRepository(session)

    def check_quota_available(self, requested_calls: int = 1, user_or_operator: str = "sistema") -> Dict[str, Any]:
        """
        Verifica se os limites internos de busca web do CXPack Radar foram atingidos.
        Lança QuotaExceededError se o limite de proteção for atingido.
        """
        today_total = self.usage_repo.get_today_grounded_calls_count()
        today_user = self.usage_repo.get_today_user_grounded_calls_count(user_or_operator)

        # 1. Verificar limite interno de proteção global do sistema
        if today_total + requested_calls > MAX_WEB_SEARCHES_TOTAL_DAY:
            raise QuotaExceededError(
                f"Limite interno diário de busca atingido ({today_total}/{MAX_WEB_SEARCHES_TOTAL_DAY}).",
                user_friendly_message="Limite de proteção interno atingido. Você ainda pode consultar fornecedores já existentes no banco de dados."
            )

        # 2. Verificar limite por usuário
        if today_user + requested_calls > MAX_WEB_SEARCHES_PER_USER_DAY:
            raise QuotaExceededError(
                f"Limite diário por usuário atingido ({today_user}/{MAX_WEB_SEARCHES_PER_USER_DAY}).",
                user_friendly_message=f"Você atingiu seu limite diário individual de {MAX_WEB_SEARCHES_PER_USER_DAY} buscas web."
            )

        remaining = max(0, MAX_WEB_SEARCHES_TOTAL_DAY - (today_total + requested_calls))
        alert_level = "GREEN"
        if today_total >= int(MAX_WEB_SEARCHES_TOTAL_DAY * 0.9):
            alert_level = "ORANGE"
        elif today_total >= int(MAX_WEB_SEARCHES_TOTAL_DAY * 0.8):
            alert_level = "YELLOW"

        return {
            "allowed": True,
            "today_total": today_total,
            "today_user": today_user,
            "safety_limit": MAX_WEB_SEARCHES_TOTAL_DAY,
            "remaining": remaining,
            "alert_level": alert_level
        }

    def get_quota_dashboard_data(self, user_or_operator: str = "sistema") -> Dict[str, Any]:
        """Retorna dados estruturados para o painel de consumo de busca web e IA."""
        today_web = self.usage_repo.get_today_grounded_calls_count()
        today_user = self.usage_repo.get_today_user_grounded_calls_count(user_or_operator)
        remaining = max(0, MAX_WEB_SEARCHES_TOTAL_DAY - today_web)
        usage_pct = min(100.0, (today_web / MAX_WEB_SEARCHES_TOTAL_DAY) * 100.0)

        alert_level = "GREEN"
        if today_web >= int(MAX_WEB_SEARCHES_TOTAL_DAY * 0.9):
            alert_level = "ORANGE"
        elif today_web >= int(MAX_WEB_SEARCHES_TOTAL_DAY * 0.8):
            alert_level = "YELLOW"

        return {
            "today_total": today_web,
            "today_user": today_user,
            "safety_limit": MAX_WEB_SEARCHES_TOTAL_DAY,
            "remaining": remaining,
            "usage_pct": usage_pct,
            "alert_level": alert_level
        }
