from providers.search.base import SearchCandidate
from services.search_service import SearchService


def candidate(title, snippet, domain="empresa.com.br"):
    return SearchCandidate(company_name="Empresa", website=f"https://{domain}", domain=domain,
                           source_title=title, source_url=f"https://{domain}/produto", reason=snippet)


def test_strict_filter_requires_public_evidence_for_every_filter():
    service = SearchService.__new__(SearchService)
    good = candidate("Frascos de resina 500 ml", "Fabricante brasileiro de frascos e embalagens em resina.")
    no_capacity = candidate("Frascos de resina", "Fabricante brasileiro de frascos e embalagens.")
    reseller = candidate("Frascos de resina 500 ml", "Loja virtual de embalagens.")

    assert service._candidate_matches_filters(good, "frascos", "500 ml", "resina", "Brasil", "Fabricante")[0]
    assert not service._candidate_matches_filters(no_capacity, "frascos", "500 ml", "resina", "Brasil", "Fabricante")[0]
    assert not service._candidate_matches_filters(reseller, "frascos", "500 ml", "resina", "Brasil", "Fabricante")[0]


def test_filter_tolerates_typo_and_industry_material_names():
    service = SearchService.__new__(SearchService)
    result = candidate("Frascos PET 500ml", "Indústria brasileira fabricante de embalagens PET.")

    matches, details = service._candidate_matches_filters(
        result, "farsco", "500 ml", "resina", "Brasil", "Fabricante"
    )

    assert matches is True
    assert all(details.values())


def test_registry_cnae_for_plastic_packaging():
    service = SearchService.__new__(SearchService)

    assert service._registry_cnae("frascos", "PEAD") == "2222600"
    assert service._registry_cnae("garrafas", "PET") == "2222600"
    assert service._registry_cnae("peças automotivas", "PEAD") is None
