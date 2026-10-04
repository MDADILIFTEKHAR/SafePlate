import pytest
from app.services.safety.allergy_engine import AllergyEngine
from app.services.budget.budget_validator import BudgetValidator
from app.services.meal.substitution_engine import SubstitutionEngine
from app.services.agent.agent_loop import AgentLoop
from app.services.ai.demo_provider import DemoProvider

def test_invariant_direct_allergen_never_safe():
    """INVARIANT: If meal contains a declared direct allergen, final status MUST NOT be SAFE."""
    engine = AllergyEngine()
    test_cases = [
        ("peanut butter spread", ["Peanut"]),
        ("crushed groundnuts", ["Peanut"]),
        ("kaju katli with cashew nuts", ["Tree nuts"]),
        ("roasted almond milk", ["Tree nuts"])
    ]
    for text, allergies in test_cases:
        res = engine.match_allergens_in_text(text, allergies)
        assert res["status"] != "SAFE", f"Failed for {text}: marked as SAFE despite direct allergen!"

def test_invariant_safe_means_no_deterministic_conflict():
    """INVARIANT: If final status is SAFE, no deterministic allergy conflict can exist."""
    engine = AllergyEngine()
    test_foods = [
        "steamed white rice",
        "boiled potatoes",
        "tomato soup",
        "fresh spinach puree",
        "lentil dal tadka"
    ]
    user_allergies = ["Peanut", "Tree nuts"]
    for food in test_foods:
        res = engine.match_allergens_in_text(food, user_allergies)
        if res["status"] == "SAFE":
            assert len(res["matched_terms"]) == 0
            assert len(res["matched_allergens"]) == 0

def test_invariant_budget_is_exact_sum():
    """INVARIANT: Final budget MUST equal the deterministic sum of meal costs."""
    costs = {"breakfast": 25.50, "lunch": 42.75, "snack": 12.25, "dinner": 39.50}
    res = BudgetValidator.validate_plan_budget(costs, 150.0)
    expected_sum = round(25.50 + 42.75 + 12.25 + 39.50, 2)
    assert res["amount"] == expected_sum

def test_invariant_unvalidated_substitution_never_final():
    """INVARIANT: An unvalidated substitution MUST NEVER become final."""
    sub_engine = SubstitutionEngine()
    # Cashew is a tree nut. If user is allergic to tree nuts, cashew must NOT be accepted!
    user_allergies = ["Tree nuts", "Peanut"]
    accepted, history = sub_engine.find_safe_substitution("almond", user_allergies, "Vegetarian")
    
    if accepted:
        # Verify the accepted item itself is not an allergen
        allergy_check = AllergyEngine().match_allergens_in_text(accepted["substitute"], user_allergies)
        assert allergy_check["status"] == "SAFE"

@pytest.mark.asyncio
async def test_invariant_agent_iterations_never_exceed_max():
    """INVARIANT: Agent iterations MUST NEVER exceed MAX_ITERATIONS."""
    provider = DemoProvider()
    # Force an impossible conflict to trigger repeated iteration failures
    provider.force_unsafe_ingredient = "permanently_unsafe_peanut_ingredient"
    provider.unrepairable_failure = True
    
    loop = AgentLoop(max_iterations=3, ai_provider=provider)
    profile = {
        "id": 1,
        "name": "Aisha",
        "allergies": ["Peanut"],
        "dietary_preference": "Vegetarian",
        "daily_budget": 150.0,
        "max_cooking_time_minutes": 30
    }
    
    result = await loop.execute_plan_generation(profile, ["Rice", "Dal"])
    assert result["iterations"] <= 3
    assert result["success"] is False
    assert result["status"] == "FAILED_MAX_ITERATIONS"
