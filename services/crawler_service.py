"""
Serviço de Crawling Respeitoso e Leve (CrawlerService).
Realiza requisições HTTP rápidas via httpx e descobre páginas prioritárias da mesma empresa.
"""

import re
import httpx
from typing import List, Dict, Any, Optional, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from utils.domains import normalize_domain

# Palavras-chave prioritárias para URLs institucionais e industriais
PRIORITY_KEYWORDS = [
    "contato", "fale-conosco", "sobre", "empresa", "quem-somos",
    "produto", "produtos", "catalogo", "catalog", "embalagem",
    "embalagens", "solucoes", "aplicacoes", "equipe", "diretoria",
    "telefone", "whatsapp", "atendimento", "comercial", "orcamento",
    "representante", "representantes", "sac", "suporte", "localizacao"
]

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CXPackRadar/1.0 (B2B IndustrialProspector)"


class CrawlerService:
    def __init__(self, max_pages_per_domain: int = 5, timeout: float = 8.0):
        self.max_pages_per_domain = max_pages_per_domain
        self.timeout = timeout

    def _is_same_domain(self, target_url: str, base_domain: str) -> bool:
        """Verifica se a URL pertence ao mesmo domínio raiz da empresa."""
        cand_domain = normalize_domain(target_url)
        return cand_domain == base_domain or cand_domain.endswith("." + base_domain)

    def _score_url(self, url: str) -> int:
        """Calcula uma pontuação de prioridade para a URL."""
        score = 0
        lower_url = url.lower()
        for kw in PRIORITY_KEYWORDS:
            if kw in lower_url:
                score += 10
        # Penalizar extensões de arquivos estáticos pesados
        if re.search(r"\.(pdf|png|jpg|jpeg|gif|zip|rar|mp4|svg)$", lower_url):
            score -= 100
        return score

    def discover_priority_links(self, base_url: str, html_content: str) -> List[str]:
        """Extrai e ordena links internos prioritários a partir do HTML inicial."""
        base_domain = normalize_domain(base_url)
        discovered_urls: Set[str] = set()

        try:
            soup = BeautifulSoup(html_content, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()
                if not href or href.startswith(("javascript:", "mailto:", "tel:", "#")):
                    continue
                full_url = urljoin(base_url, href)
                # Manter apenas se for do mesmo domínio
                if self._is_same_domain(full_url, base_domain):
                    clean_url = full_url.split("#")[0].rstrip("/")
                    if clean_url:
                        discovered_urls.add(clean_url)
        except Exception:
            pass

        # Ordenar URLs por score de relevância
        sorted_urls = sorted(list(discovered_urls), key=self._score_url, reverse=True)
        return sorted_urls

    def fetch_page(self, url: str) -> Dict[str, Any]:
        """
        Realiza o download HTTP de uma única página respeitando timeouts.
        Returns dict com status, status_code, html, url e title.
        """
        headers = {"User-Agent": USER_AGENT}
        try:
            with httpx.Client(timeout=self.timeout, follow_redirects=True, verify=False) as client:
                response = client.get(url, headers=headers)
                status_code = response.status_code

                if status_code == 200:
                    html_text = response.text
                    title = ""
                    try:
                        soup = BeautifulSoup(html_text, "html.parser")
                        if soup.title and soup.title.string:
                            title = soup.title.string.strip()
                    except Exception:
                        pass

                    return {
                        "url": str(response.url),
                        "status_code": status_code,
                        "status": "COMPLETED",
                        "html": html_text,
                        "title": title,
                        "error": None
                    }
                elif status_code in (403, 401, 503):
                    return {
                        "url": url,
                        "status_code": status_code,
                        "status": "BLOCKED",
                        "html": "",
                        "title": "Acesso Bloqueado",
                        "error": f"HTTP {status_code} - Bloqueado por WAF ou proteção do servidor."
                    }
                else:
                    return {
                        "url": url,
                        "status_code": status_code,
                        "status": "FAILED",
                        "html": "",
                        "title": "Erro HTTP",
                        "error": f"HTTP {status_code}"
                    }

        except httpx.TimeoutException:
            return {
                "url": url,
                "status_code": -1,
                "status": "TIMEOUT",
                "html": "",
                "title": "Tempo de Resposta Excedido",
                "error": f"Timeout após {self.timeout}s"
            }
        except Exception as e:
            return {
                "url": url,
                "status_code": -1,
                "status": "FAILED",
                "html": "",
                "title": "Erro de Conexão",
                "error": str(e)
            }

    def crawl_website(self, start_url: str) -> List[Dict[str, Any]]:
        """
        Executa o crawling de um site até o limite de MAX_PAGES_PER_DOMAIN.
        """
        crawled_results: List[Dict[str, Any]] = []
        visited_urls: Set[str] = set()

        # 1. Baixar Home Page
        first_page = self.fetch_page(start_url)
        visited_urls.add(start_url)
        crawled_results.append(first_page)

        if first_page["status"] != "COMPLETED" or not first_page["html"]:
            return crawled_results

        # 2. Descobrir links prioritários a partir da Home Page
        priority_links = self.discover_priority_links(first_page["url"], first_page["html"])

        # 3. Visitar páginas secundárias até atingir o limite
        for link in priority_links:
            if len(crawled_results) >= self.max_pages_per_domain:
                break
            if link not in visited_urls:
                visited_urls.add(link)
                page_res = self.fetch_page(link)
                crawled_results.append(page_res)

        return crawled_results
