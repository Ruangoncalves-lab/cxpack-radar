"""
Módulo de manipulação de segredos e chaves de API.
Busca em ordem de prioridade:
1. st.secrets (Streamlit Cloud ou local .streamlit/secrets.toml)
2. os.environ (Variáveis de ambiente do sistema)
"""

import os
from typing import Optional


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retorna o valor de uma chave de configuração/segredo.
    Verifica primeiramente st.secrets (se disponível) e posteriormente os.getenv.
    """
    # 1. Tentar ler do Streamlit Secrets se estiver rodando no contexto do Streamlit
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass

    # 2. Tentar ler de variável de ambiente
    env_val = os.getenv(key)
    if env_val is not None:
        return env_val

    # 3. Retornar padrão se não encontrado
    return default


def get_gemini_api_key() -> Optional[str]:
    """Retorna a chave da API do Gemini se configurada."""
    return get_secret("GEMINI_API_KEY")


def is_gemini_configured() -> bool:
    """Verifica se a chave da API do Gemini está presente e não vazia."""
    key = get_gemini_api_key()
    return bool(key and key.strip() and key != "SUA_CHAVE_GEMINI_AQUI")
