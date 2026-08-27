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

    @staticmethod
    def _phones_from_data(data: Dict[str, Any]) -> List[str]:
        """Retorna todos os telefones públicos informados no cadastro do CNPJ."""
        phones = []
        for key in ("ddd_telefone_1", "ddd_telefone_2", "telefone"):
            value = str(data.get(key) or "").strip()
            if value and value not in phones:
                phones.append(value)
        return phones

    @staticmethod
    def _address_from_data(data: Dict[str, Any]) -> str:
        """Monta o endereço cadastral completo sem deixar separadores vazios."""
        street = ", ".join(filter(None, [data.get("logradouro"), str(data.get("numero") or ""), data.get("complemento")]))
        city_state = " / ".join(filter(None, [data.get("municipio"), data.get("uf")]))
        parts = [street, data.get("bairro"), city_state]
        if data.get("cep"):
            parts.append(f"CEP {data['cep']}")
        return " — ".join(filter(None, parts))

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
                    phones = self._phones_from_data(data)
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
                        "address": self._address_from_data(data),
                        "phone": phones[0] if phones else "",
                        "phones": phones,
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
                    phones = self._phones_from_data(data)
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
                        "address": self._address_from_data(data),
                        "phone": phones[0] if phones else "",
                        "phones": phones,
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

    def search_companies_by_cnae(self, cnae: str, state: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Consulta gratuita da base Receita Federal espelhada pelo Minha Receita."""
        params = {"cnae": re.sub(r"\D", "", cnae), "limit": min(max(limit, 1), 1000)}
        if state:
            params["uf"] = state.upper()
        try:
            with httpx.Client(timeout=max(self.timeout, 20.0), follow_redirects=True) as client:
                response = client.get("https://minhareceita.org/", params=params, headers={"User-Agent": USER_AGENT})
                response.raise_for_status()
                rows = response.json().get("data", [])
        except Exception:
            return []

        companies = []
        for data in rows:
            if data.get("situacao_cadastral") not in (2, "2") and data.get("descricao_situacao_cadastral") != "ATIVA":
                continue
            cnpj = str(data.get("cnpj") or "")
            if len(cnpj) != 14:
                continue
            phones = self._phones_from_data(data)
            companies.append({
                "cnpj": cnpj,
                "legal_name": data.get("razao_social") or "",
                "trade_name": data.get("nome_fantasia") or data.get("razao_social") or "",
                "status_cadastral": data.get("descricao_situacao_cadastral") or "ATIVA",
                "cnae_code": str(data.get("cnae_fiscal") or ""),
                "cnae_text": data.get("cnae_fiscal_descricao") or "",
                "city": data.get("municipio") or "",
                "state": data.get("uf") or "",
                "phone": phones[0] if phones else "",
                "phones": phones,
                "email": data.get("email") or "",
                "qsa": data.get("qsa") or [],
                "source": "Minha Receita / Dados Abertos Receita Federal",
            })
        return companies
