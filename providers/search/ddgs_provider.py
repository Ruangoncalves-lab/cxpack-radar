"""
Implementação do DDGSSearchProvider para busca web gratuita via DuckDuckGo Search (DDGS).
Estende a classe abstrata SearchProvider sem acoplar o restante do sistema.
"""

import time
import logging
from typing import List, Optional

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

from core.config import SEARCH_DELAY_SECONDS
from utils.domains import normalize_domain, is_blacklisted
from providers.search.base import SearchProvider, SearchCandidate

logger = logging.getLogger(__name__)


class DDGSSearchProvider(SearchProvider):
    def __init__(self, delay_seconds: float = SEARCH_DELAY_SECONDS, max_retries: int = 2):
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries
        self.provider_name = "DDGS"
        self.last_error: Optional[str] = None

    def search_candidates(self, query: str, max_results: int = 10) -> List[SearchCandidate]:
        """
        Executa uma busca web no DuckDuckGo (DDGS) de forma responsável com retries e fallback.
        Normaliza e deduplica os domínios encontrados.
        """
        candidates: List[SearchCandidate] = []
        seen_domains = set()
        raw_results = []
        self.last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                with DDGS() as ddgs:
                    # 1. Tentar busca regionalizada br-pt
                    res = ddgs.text(query, max_results=max_results, region="br-pt")
                    if res:
                        raw_results = list(res)

                    # 2. Fallback sem filtro de região se br-pt retornar vazio
                    if not raw_results:
                        res = ddgs.text(query, max_results=max_results)
                        if res:
                            raw_results = list(res)

                    if raw_results:
                        self.last_error = None
                        break
            except Exception as e:
                self.last_error = str(e)
                logger.warning(f"[DDGSSearchProvider] Tentativa {attempt}/{self.max_retries} falhou para query '{query}': {e}")
                if attempt < self.max_retries:
                    time.sleep(self.delay_seconds * attempt)

        if self.delay_seconds > 0:
            time.sleep(self.delay_seconds)

        for item in raw_results:
            url = item.get("href") or item.get("link") or ""
            title = item.get("title") or ""
            snippet = item.get("body") or item.get("snippet") or ""

            if not url:
                continue

            domain = normalize_domain(url)
            if domain and not is_blacklisted(domain) and domain not in seen_domains:
                seen_domains.add(domain)

                # Tratar nome da empresa a partir do título do site
                clean_title = title.split("-")[0].split("|")[0].split("–")[0].strip()
                company_name = clean_title if clean_title and len(clean_title) > 2 else domain.capitalize()

                candidates.append(
                    SearchCandidate(
                        company_name=company_name,
                        website=f"https://{domain}",
                        domain=domain,
                        reason=f"Mencionado nos resultados DDGS: '{snippet[:500]}...'",
                        source_title=title,
                        source_url=url,
                        query=query,
                        confidence=0.85
                    )
                )

        return candidates[:max_results]
