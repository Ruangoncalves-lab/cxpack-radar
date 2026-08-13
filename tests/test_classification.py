"""
Testes unitários para as regras locais de classificação (ClassificationService).
"""

from services.classification_service import ClassificationService


def test_classify_by_local_rules_manufacturer():
    classifier = ClassificationService()
    sample_text = "Somos uma indústria de embalagens plásticas e fabricamos frascos PET com linha de produção própria."
    res = classifier.classify_by_local_rules(sample_text, "empresa.com.br")

    assert res["company_type"] == "FABRICANTE"
    assert res["confidence"] >= 0.70
    assert "LOCAL_RULES" == res["method"]


def test_classify_by_local_rules_marketplace():
    classifier = ClassificationService()
    res = classifier.classify_by_local_rules("Qualquer texto", "mercadolivre.com.br")

    assert res["company_type"] == "MARKETPLACE"
    assert res["confidence"] == 0.99
