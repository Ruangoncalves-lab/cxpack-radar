"""
Implementação de SearchProvider utilizando Gemini + Grounding with Google Search.
"""

from typing import List, Optional
from core.config import DEFAULT_GEMINI_MODEL
from core.secrets import get_gemini_api_key
from core.exceptions import GeminiAPIError
from utils.domains import normalize_domain, is_blacklisted
from providers.search.base import SearchProvider, SearchCandidate


class GeminiSearchProvider(SearchProvider):
    def __init__(self, model_name: str = DEFAULT_GEMINI_MODEL, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key or get_gemini_api_key()

    def _get_client(self):
        if not self.api_key or not self.api_key.strip() or self.api_key == "SUA_CHAVE_GEMINI_AQUI":
            raise GeminiAPIError("Chave da API do Gemini não configurada para busca grounded.")

        try:
            from google import genai
            return genai.Client(api_key=self.api_key)
        except ImportError:
            raise GeminiAPIError("SDK 'google-genai' não encontrado.")

    def search_candidates(self, query: str, max_results: int = 10) -> List[SearchCandidate]:
        """
        Executa uma busca na web via Gemini Search Grounding e extrai os sites de empresas candidatas.
        """
        client = self._get_client()
        prompt = (
            f"Você é um pesquisador especialista em prospecção industrial B2B.\n"
            f"Encontre fabricantes e fornecedores industriais para a seguinte busca: '{query}'.\n"
            f"Utilize o Google Search para encontrar empresas reais no Brasil.\n"
            f"Para cada empresa encontrada, mencione explicitamente o nome completo e o site oficial (URL)."
        )

        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                tools=[{"google_search": {}}]
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            candidates: List[SearchCandidate] = []
            seen_domains = set()

            # 1. Extrair metadados de Grounding se disponíveis
            grounding_urls = []
            if hasattr(response, "candidates") and response.candidates:
                first_cand = response.candidates[0]
                if hasattr(first_cand, "grounding_metadata") and first_cand.grounding_metadata:
                    gm = first_cand.grounding_metadata
                    # Inspect grounding chunks
                    if hasattr(gm, "grounding_chunks") and gm.grounding_chunks:
                        for chunk in gm.grounding_chunks:
                            if hasattr(chunk, "web") and chunk.web:
                                uri = getattr(chunk.web, "uri", None)
                                title = getattr(chunk.web, "title", None)
                                if uri:
                                    grounding_urls.append((uri, title or uri))

            # Processar URLs obtidas dos metadados de grounding
            for url, title in grounding_urls:
                domain = normalize_domain(url)
                if domain and not is_blacklisted(domain) and domain not in seen_domains:
                    seen_domains.add(domain)
                    company_name = title.split("-")[0].split("|")[0].strip() if title else domain
                    candidates.append(
                        SearchCandidate(
                            company_name=company_name,
                            website=f"https://{domain}",
                            domain=domain,
                            reason="Encontrado via Google Search Grounding",
                            source_title=title,
                            source_url=url,
                            query=query,
                            confidence=0.85
                        )
                    )

            # 2. Se poucos candidatos dos metadados de grounding, extrair URLs do texto retornado pela IA
            import re
            text_content = response.text or ""
            url_matches = re.findall(r"https?://[^\s\)\>\"']+", text_content)

            for raw_url in url_matches:
                domain = normalize_domain(raw_url)
                if domain and not is_blacklisted(domain) and domain not in seen_domains:
                    seen_domains.add(domain)
                    candidates.append(
                        SearchCandidate(
                            company_name=domain.capitalize(),
                            website=f"https://{domain}",
                            domain=domain,
                            reason="Mencionado no texto da busca",
                            source_title=domain,
                            source_url=raw_url,
                            query=query,
                            confidence=0.75
                        )
                    )

            return candidates[:max_results]

        except Exception as e:
            raise GeminiAPIError(f"Erro na pesquisa web grounded com Gemini: {str(e)}")
