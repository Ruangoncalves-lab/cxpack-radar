"""
Interface abstrata para Provedores de LLM.
Garante que a troca futura de modelo ou provedor (Groq, OpenAI, Anthropic) não afete o sistema.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class LLMProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Gera texto a partir de um prompt."""
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, schema: Any, system_instruction: Optional[str] = None) -> Any:
        """Gera dados estruturados alinhados a um schema Pydantic."""
        pass

    @abstractmethod
    def test_connection(self) -> tuple[bool, str]:
        """Testa se a API do provedor está ativa e funcionando."""
        pass
