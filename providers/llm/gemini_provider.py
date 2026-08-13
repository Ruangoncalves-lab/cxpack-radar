"""
Implementação oficial do GeminiProvider utilizando o SDK google-genai.
Centralizado em DEFAULT_GEMINI_MODEL.
"""

import json
from typing import Optional, Any, List, Tuple, Dict
from core.config import DEFAULT_GEMINI_MODEL
from core.secrets import get_gemini_api_key, is_gemini_configured
from core.exceptions import GeminiAPIError
from providers.llm.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self, model_name: str = DEFAULT_GEMINI_MODEL, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key or get_gemini_api_key()

    def is_available(self) -> bool:
        """Verifica se a chave da API do Gemini está configurada."""
        return is_gemini_configured()

    def _get_client(self):
        """Inicializa e retorna o cliente oficial do SDK google-genai."""
        if not self.api_key or not self.api_key.strip() or self.api_key == "SUA_CHAVE_GEMINI_AQUI":
            raise GeminiAPIError("Chave da API do Gemini não configurada.")

        try:
            from google import genai
            return genai.Client(api_key=self.api_key)
        except ImportError:
            raise GeminiAPIError("SDK 'google-genai' não encontrado. Instale via 'pip install google-genai'.")
        except Exception as e:
            raise GeminiAPIError(f"Erro ao inicializar cliente do Gemini: {str(e)}")

    def list_available_models(self) -> List[str]:
        """
        Consulta via SDK google-genai a lista de modelos ativos disponíveis para a API Key.
        Evita o uso de modelos descontinuados.
        """
        try:
            client = self._get_client()
            models_page = client.models.list()
            available = []
            for m in models_page:
                name = getattr(m, "name", str(m))
                if "gemini" in name.lower():
                    available.append(name.replace("models/", ""))
            return available if available else [self.model_name]
        except Exception:
            return [self.model_name]

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        client = self._get_client()
        try:
            from google.genai import types
            config = types.GenerateContentConfig()
            if system_instruction:
                config.system_instruction = system_instruction

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return response.text or ""
        except Exception as e:
            raise GeminiAPIError(f"Erro durante geração de texto no Gemini: {str(e)}")

    def generate_structured(self, prompt: str, schema: Any, system_instruction: Optional[str] = None) -> Any:
        client = self._get_client()
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema
            )
            if system_instruction:
                config.system_instruction = system_instruction

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            if hasattr(response, "parsed") and response.parsed is not None:
                return response.parsed
            return response.text
        except Exception as e:
            raise GeminiAPIError(f"Erro na geração estruturada do Gemini: {str(e)}")

    def analyze_company(self, company_name: str, domain: str, crawled_text: str) -> Dict[str, Any]:
        """Analisa os textos coletados sobre uma empresa e extrai dados estruturados."""
        if not self.is_available():
            return {"extractions": {}}

        prompt = f"Empresa: {company_name} ({domain})\nTextos:\n{crawled_text[:3000]}"
        try:
            res_text = self.generate_text(prompt, system_instruction="Extraia dados em formato JSON com o objeto 'extractions'.")
            if "{" in res_text and "}" in res_text:
                start = res_text.find("{")
                end = res_text.rfind("}") + 1
                parsed = json.loads(res_text[start:end])
                return parsed if isinstance(parsed, dict) else {"extractions": {}}
            return {"extractions": {}}
        except Exception:
            return {"extractions": {}}

    def test_connection(self) -> Tuple[bool, str, Optional[str]]:
        """
        Realiza uma chamada mínima e barata enviando apenas 'OK' para verificar se o modelo está ativo.
        Retorna (sucesso: bool, mensagem_amigavel: str, detalhes_tecnicos: Optional[str]).
        """
        if not is_gemini_configured():
            return False, "Não foi possível conectar: Chave da API do Gemini não configurada.", None

        try:
            client = self._get_client()
            response = client.models.generate_content(
                model=self.model_name,
                contents="OK"
            )
            if response and response.text:
                return True, "Gemini conectado com sucesso", None
            return False, "Não foi possível conectar ao modelo Gemini selecionado.", "Resposta vazia retornada pela API."
        except Exception as e:
            err_msg = str(e)
            return False, "Não foi possível conectar ao modelo Gemini selecionado.", err_msg
