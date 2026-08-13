"""
Configurações centrais do CXPack Radar.
Todas as constantes e limites operacionais são definidos aqui para evitar hardcoding.
"""

import os
from pathlib import Path

# Diretórios principais
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Banco de dados padrão (SQLite local)
DEFAULT_SQLITE_URL = f"sqlite:///{DATA_DIR / 'cxpack_radar.db'}"

# Modelo padrão do Google Gemini (Configuração centralizada)
DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"

# Provedor de Busca Web Padrão
SEARCH_PROVIDER = "ddgs"

# Limites Internos do CXPack Radar para Busca Web (DDGS - R$ 0)
MAX_WEB_QUERIES_PER_SEARCH = 3        # Máximo de variações por busca do usuário
MAX_WEB_SEARCHES_PER_USER_DAY = 100   # Limite interno de segurança por usuário/dia
MAX_WEB_SEARCHES_TOTAL_DAY = 500      # Limite interno total da plataforma/dia
SEARCH_DELAY_SECONDS = 1.5            # Delay responsável entre requisições
MAX_CONCURRENT_SEARCHES = 2           # Concorrência conservadora

# Validade do Cache de Pesquisa (Dias)
CACHE_EXPIRATION_DAYS = 30

# Arquivos de segredos
SECRETS_FILE_NAME = ".streamlit/secrets.toml"
