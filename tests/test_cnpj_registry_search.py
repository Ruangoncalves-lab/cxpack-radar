from unittest.mock import Mock, patch

from providers.cnpj.public_cnpj_provider import PublicCNPJProvider


def test_search_companies_by_cnae_maps_only_active_companies():
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "data": [
            {
                "cnpj": "12345678000190",
                "razao_social": "INDUSTRIA DE EMBALAGENS LTDA",
                "nome_fantasia": "EMBALAGENS BRASIL",
                "situacao_cadastral": 2,
                "descricao_situacao_cadastral": "ATIVA",
                "cnae_fiscal": 2222600,
                "cnae_fiscal_descricao": "Fabricação de embalagens de material plástico",
                "municipio": "SAO PAULO",
                "uf": "SP",
            },
            {
                "cnpj": "98765432000100",
                "razao_social": "EMPRESA BAIXADA LTDA",
                "situacao_cadastral": 8,
                "descricao_situacao_cadastral": "BAIXADA",
            },
        ]
    }
    client = Mock()
    client.__enter__ = Mock(return_value=client)
    client.__exit__ = Mock(return_value=False)
    client.get.return_value = response

    with patch("providers.cnpj.public_cnpj_provider.httpx.Client", return_value=client):
        rows = PublicCNPJProvider().search_companies_by_cnae("2222-6/00", "sp", limit=2500)

    assert len(rows) == 1
    assert rows[0]["cnpj"] == "12345678000190"
    assert rows[0]["trade_name"] == "EMBALAGENS BRASIL"
    assert client.get.call_args.kwargs["params"] == {"cnae": "2222600", "limit": 1000, "uf": "SP"}
