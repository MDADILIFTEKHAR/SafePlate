import pytest
from app.services.meal.substitution_engine import SubstitutionEngine

@pytest.fixture
def sub_engine():
    return SubstitutionEngine()

def test_peanut_butter_safe_substitution(sub_engine):
    # Aisha has Peanut and Tree nut allergies
    accepted, history = sub_engine.find_safe_substitution(
        unsafe_ingredient="peanut butter",
        user_allergies=["Peanut", "Tree nuts"],
        diet_preference="Vegetarian"
    )
    assert accepted is not None
    # Sunflower seed butter is safe (not a peanut or tree nut)
    assert "sunflower seed butter" in accepted["substitute"].lower()
    assert accepted["is_safe"] is True

def test_unvalidated_or_unsafe_substitution_rejected(sub_engine):
    # If user is also allergic to sunflower seeds or soy
    accepted, history = sub_engine.find_safe_substitution(
        unsafe_ingredient="cow milk",
        user_allergies=["Tree nuts"],
        diet_preference="Vegetarian"
    )
    assert accepted is not None
    # Oat milk should be safe, but almond milk should be rejected!
    for h in history:
        if "almond milk" in h["substitute"].lower():
            assert h["is_safe"] is False
            assert "Allergy conflict" in h["reason"]

def test_max_attempts_bounded(sub_engine):
    # Testing bound constraint: max 3 attempts
    accepted, history = sub_engine.find_safe_substitution(
        unsafe_ingredient="peanut butter",
        user_allergies=["Peanut"],
        max_attempts=2
    )
    assert len(history) <= 2
