"""
Repositório para gerenciamento de configurações do sistema em banco de dados.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from database.models import SystemSetting


class SettingsRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Obtém o valor de uma configuração."""
        stmt = select(SystemSetting).where(SystemSetting.key == key)
        setting = self.session.scalar(stmt)
        return setting.value if setting else default

    def set(self, key: str, value: str, description: Optional[str] = None) -> SystemSetting:
        """Define ou atualiza uma configuração."""
        stmt = select(SystemSetting).where(SystemSetting.key == key)
        setting = self.session.scalar(stmt)
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = SystemSetting(key=key, value=value, description=description)
            self.session.add(setting)
        self.session.commit()
        return setting
