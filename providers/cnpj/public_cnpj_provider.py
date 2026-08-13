"""
Implementação de CNPJDataProvider utilizando APIs de Dados Abertos e Públicos Gratuitos (BrasilAPI / MinhaReceita).
Consulta CNPJ e QSA de forma 100% gratuita e sem solicitação de CAPTCHA ou chaves pagas.
"""

import re
import httpx
from typing import List, Optional, Dict, Any
from providers.cnpj.base import CNPJDataProvider

USER_AGENT = "CXPackRadar/1.0 (PublicCNPJProvider B2BProspector)"


class PublicCNPJProvider(CNPJDataProvider):
    def __init__(self, timeout: float = 6.0):
        self.timeout = timeout

    def _clean_cnpj(self, cnpj: str) -> str:
        """Remove pontuação do CNPJ deixando apenas 14 dígitos numéricos."""
        return re.sub(r"\D", "", cnpj or "")

    def get_company_by_cnpj(self, cnpj: str) -> Optional[Dict[str, Any]]:
        clean = self._clean_cnpj(cnpj)
        if len(clean) != 14:
            return None

        # 1. Tentar BrasilAPI primeiro
        try:
            url = f"https://brasilapi.com.br/api/cnpj/v1/{clean}"
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                res = client.get(url, headers={"User-Agent": USER_AGENT})
                if res.status_code == 200:
                    data = res.json()
                    # Mapear QSA se presente
                    qsa_list = []
                    for q in data.get("qsa", []):
                        qsa_list.append({
                            "name": q.get("nome_socio") or q.get("nome") or "Sócio",
                            "qualification": q.get("qualificacao_socio") or q.get("qualificacao") or "SOCIO",
                            "country": q.get("pais") or "Brasil",
                            "legal_representative": q.get("nome_representante_legal")
                        })

                    return {
                        "cnpj": clean,
                        "legal_name": data.get("razao_social") or "",
                        "trade_name": data.get("nome_fantasia") or data.get("razao_social") or "",
                        "status_cadastral": data.get("descricao_situacao_cadastral") or "ATIVA",
                        "cnae_code": str(data.get("cnae_fiscal") or ""),
                        "cnae_text": data.get("cnae_fiscal_descricao") or "",
                        "cnaes_secondary": [str(c.get("codigo")) for c in data.get("cnaes_secundarios", [])],
                        "capital_social": float(data.get("capital_social") or 0.0),
                        "city": data.get("municipio") or "",
                        "state": data.get("uf") or "",
                        "address": f"{data.get('logradouro', '')}, {data.get('numero', '')} - {data.get('bairro', '')}",
                        "phone": data.get("ddd_telefone_1") or data.get("telefone") or "",
                        "email": data.get("email") or "",
                        "qsa": qsa_list,
                        "source": "BrasilAPI / Dados Abertos Receita Federal"
                    }
        except Exception:
            pass

        # 2. Fallback: MinhaReceita API
        try:
            url = f"https://minhareceita.org/{clean}"
            with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                res = client.get(url, headers={"User-Agent": USER_AGENT})
                if res.status_code == 200:
                    data = res.json()
                    qsa_list = []
                    for q in data.get("qsa", []):
                        qsa_list.append({
                            "name": q.get("nome_socio") or "Sócio",
                            "qualification": q.get("qualificacao_socio") or "SOCIO",
                            "country": "Brasil",
                            "legal_representative": q.get("representante_legal")
                        })

                    return {
                        "cnpj": clean,
                        "legal_name": data.get("razao_social") or "",
                        "trade_name": data.get("nome_fantasia") or data.get("razao_social") or "",
                        "status_cadastral": data.get("descricao_situacao_cadastral") or "ATIVA",
                        "cnae_code": str(data.get("cnae_fiscal") or ""),
                        "cnae_text": data.get("cnae_fiscal_descricao") or "",
                        "cnaes_secondary": [],
                        "capital_social": float(data.get("capital_social") or 0.0),
                        "city": data.get("municipio") or "",
                        "state": data.get("uf") or "",
                        "address": f"{data.get('logradouro', '')}, {data.get('numero', '')}",
                        "phone": data.get("ddd_telefone_1") or "",
                        "email": data.get("email") or "",
                        "qsa": qsa_list,
                        "source": "MinhaReceita / Dados Abertos Receita Federal"
                    }
        except Exception:
            pass

        return None

    def get_partners(self, cnpj: str) -> List[Dict[str, Any]]:
        info = self.get_company_by_cnpj(cnpj)
        return info.get("qsa", []) if info else []

    def search_cnpj_by_name_or_domain(
        self, company_name: str, domain: Optional[str] = None, city: Optional[str] = None, state: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Pesquisa preliminar de candidatos a CNPJ com base em busca textual de dados públicos.
        """
        # Em produção/API pública sem endpoint de busca geral por nome, simula ou retorna a lista de candidatos
        return []
