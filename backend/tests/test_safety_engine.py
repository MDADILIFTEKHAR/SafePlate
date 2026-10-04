import pytest
from app.services.safety.allergy_engine import AllergyEngine

@pytest.fixture
def allergy_engine():
    return AllergyEngine()

def test_peanut_direct_avoid(allergy_engine):
    res = allergy_engine.match_allergens_in_text("peanut butter", ["Peanut"])
    assert res["status"] == "AVOID"
    assert "peanut" in [t.lower() for t in res["matched_terms"]]

def test_groundnut_alias_avoid(allergy_engine):
    res = allergy_engine.match_allergens_in_text("groundnut oil", ["Peanut"])
    assert res["status"] == "AVOID"
    assert "PEANUT" in res["matched_allergens"] or "Peanut" in res["matched_allergens"]

def test_tree_nut_cashew_almond(allergy_engine):
    res_cashew = allergy_engine.match_allergens_in_text("Roasted Cashews", ["Tree nuts"])
    assert res_cashew["status"] == "AVOID"

    res_almond = allergy_engine.match_allergens_in_text("Badam milk with crushed almonds", ["Tree nuts"])
    assert res_almond["status"] == "AVOID"

def test_safe_food_no_allergens(allergy_engine):
    res_rice = allergy_engine.match_allergens_in_text("steamed basmati rice", ["Peanut", "Tree nuts"])
    assert res_rice["status"] == "SAFE"
    assert len(res_rice["matched_terms"]) == 0

    res_dal = allergy_engine.match_allergens_in_text("yellow moong dal", ["Peanut", "Tree nuts"])
    assert res_dal["status"] == "SAFE"

def test_cross_contamination_caution(allergy_engine):
    res = allergy_engine.match_allergens_in_text("may contain traces of peanuts", ["Peanut"])
    assert res["status"] == "CAUTION"
    assert "may contain" in res["reason"].lower() or "traces" in res["reason"].lower()

    res_facility = allergy_engine.match_allergens_in_text("Manufactured in a facility with tree nuts", ["Tree nuts"])
    assert res_facility["status"] == "CAUTION"

def test_unknown_ingredient(allergy_engine):
    res = allergy_engine.match_allergens_in_text("unknown packaged seasoning blend E-999", ["Peanut"])
    assert res["status"] == "UNKNOWN"

def test_normalization_and_punctuation(allergy_engine):
    # Tests punctuation removal, hyphens, caps, extra whitespace
    res = allergy_engine.match_allergens_in_text("  CRUNCHY---PEA-NUT!  BUTTER... ", ["Peanut"])
    assert res["status"] == "AVOID"

def test_empty_string_handling(allergy_engine):
    res = allergy_engine.match_allergens_in_text("", ["Peanut"])
    assert res["status"] == "UNKNOWN"

def test_validate_ingredients_list(allergy_engine):
    clean_list = ["Rice", "Tomato", "Potato", "Spinach"]
    status, reasons, offending = allergy_engine.validate_ingredients_list(clean_list, ["Peanut", "Tree nuts"])
    assert status == "SAFE"
    assert len(offending) == 0

    mixed_list = ["Rice", "Peanut chutney", "Potato"]
    status, reasons, offending = allergy_engine.validate_ingredients_list(mixed_list, ["Peanut"])
    assert status == "AVOID"
    assert "Peanut chutney" in offending
