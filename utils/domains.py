"""
Utilitário para normalização de URLs e filtragem de domínios (Blacklist).
"""

import re
from urllib.parse import urlparse
from typing import Set

# Blacklist de domínios genéricos, marketplaces, redes sociais e diretórios
DEFAULT_BLACKLIST: Set[str] = {
    "mercadolivre.com.br",
    "mercadolibre.com",
    "amazon.com.br",
    "amazon.com",
    "shopee.com.br",
    "shopee.com",
    "facebook.com",
    "instagram.com",
    "youtube.com",
    "pinterest.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
    "tiktok.com",
    "olx.com.br",
    "magazineluiza.com.br",
    "americanas.com.br",
    "casasbahia.com.br",
    "aliexpress.com",
    "wikipedia.org",
    "whatsapp.com",
    "google.com",
    "google.com.br",
}


def normalize_domain(url_or_domain: str) -> str:
    """
    Normaliza uma URL ou string de domínio para o domínio raiz sem subdomínio 'www' ou portas.
    Exemplos:
    - https://www.empresa.com.br/produtos -> empresa.com.br
    - http://empresa.com.br/ -> empresa.com.br
    - https://sub.empresa.com.br/catalogo -> sub.empresa.com.br (ou empresa.com.br se www)
    """
    if not url_or_domain:
        return ""

    raw = url_or_domain.strip().lower()

    # Adicionar esquema se não possuir para urlparse funcionar corretamente
    if not raw.startswith(("http://", "https://", "ftp://")):
        raw = "http://" + raw

    try:
        parsed = urlparse(raw)
        host = parsed.netloc or parsed.path

        # Remover porta se houver
        if ":" in host:
            host = host.split(":")[0]

        # Remover prefixo 'www.' se houver
        if host.startswith("www."):
            host = host[4:]

        return host.strip()
    except Exception:
        # Fallback usando regex se urlparse falhar
        clean = re.sub(r"^https?://", "", raw)
        clean = re.sub(r"^www\.", "", clean)
        clean = clean.split("/")[0].split(":")[0]
        return clean.strip()


def is_blacklisted(domain_or_url: str, custom_blacklist: Set[str] = None) -> bool:
    """
    Verifica se o domínio pertence à blacklist de marketplaces ou redes sociais.
    """
    domain = normalize_domain(domain_or_url)
    blacklist = custom_blacklist if custom_blacklist is not None else DEFAULT_BLACKLIST

    if not domain:
        return True

    # Checar se o domínio exato ou sufixo está na blacklist
    for bl_item in blacklist:
        if domain == bl_item or domain.endswith("." + bl_item):
            return True

    return False
