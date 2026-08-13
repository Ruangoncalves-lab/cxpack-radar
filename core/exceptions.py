"""
Exceções customizadas do CXPack Radar.
Proporcionam mensagens amigáveis em português para o usuário final sem expor tracebacks técnicos confusos na UI.
"""

class CXPackError(Exception):
    """Exceção base para o CXPack Radar."""
    def __init__(self, message: str, user_friendly_message: str = None):
        super().__init__(message)
        self.user_friendly_message = user_friendly_message or message


class QuotaExceededError(CXPackError):
    """Disparada quando o limite de chamadas de API do sistema ou do usuário é atingido."""
    pass


class GeminiAPIError(CXPackError):
    """Disparada quando ocorre uma falha na chamada do Google Gemini."""
    pass


class DatabaseConnectionError(CXPackError):
    """Disparada quando não é possível conectar ao banco de dados."""
    pass


class SearchAlreadyExistsError(CXPackError):
    """Disparada quando uma pesquisa idêntica foi executada recentemente (cache)."""
    pass
