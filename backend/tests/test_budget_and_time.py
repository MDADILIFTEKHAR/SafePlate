import pytest
from app.services.budget.budget_validator import BudgetValidator
from app.services.meal.time_validator import TimeValidator
from app.services.meal.pantry_engine import PantryEngine

def test_budget_calculation_with_pantry():
    ingredients = [
        {"name": "Rice", "estimated_cost": 15.0, "in_pantry": True},
        {"name": "Dal", "estimated_cost": 20.0, "in_pantry": True},
        {"name": "Fresh Cilantro", "estimated_cost": 5.0, "in_pantry": False},
        {"name": "Cooking Oil", "estimated_cost": 8.0, "in_pantry": False}
    ]
    # Pantry items are 0 additional cost
    cost = BudgetValidator.calculate_meal_cost(ingredients)
    assert cost == 13.0

def test_plan_budget_validation():
    meal_costs = {
        "breakfast": 30.0,
        "lunch": 45.0,
        "snack": 15.0,
        "dinner": 40.0
    }
    # Total = 130 <= 150
    res = BudgetValidator.validate_plan_budget(meal_costs, 150.0)
    assert res["within_budget"] is True
    assert res["amount"] == 130.0
    assert res["remaining"] == 20.0
    assert len(res["violations"]) == 0

    # Over budget scenario: Total = 175 > 150
    meal_costs_over = {
        "breakfast": 40.0,
        "lunch": 60.0,
        "snack": 25.0,
        "dinner": 50.0
    }
    res_over = BudgetValidator.validate_plan_budget(meal_costs_over, 150.0)
    assert res_over["within_budget"] is False
    assert res_over["amount"] == 175.0
    assert res_over["remaining"] == -25.0
    assert len(res_over["violations"]) > 0

def test_cooking_time_validation():
    is_valid, msg = TimeValidator.validate_meal_time(25, 30)
    assert is_valid is True

    is_valid_exceed, msg_exceed = TimeValidator.validate_meal_time(45, 30)
    assert is_valid_exceed is False
    assert "exceeds" in msg_exceed

def test_pantry_engine_matching():
    recipe_ingredients = [
        {"name": "Steamed Rice", "estimated_cost": 12.0},
        {"name": "Boiled Dal Tadka", "estimated_cost": 18.0},
        {"name": "Exotic Saffron", "estimated_cost": 50.0}
    ]
    pantry = ["Rice", "Dal", "Tomato"]
    res = PantryEngine.match_ingredients_with_pantry(recipe_ingredients, pantry)
    
    assert "Steamed Rice" in res["used_ingredients"]
    assert "Boiled Dal Tadka" in res["used_ingredients"]
    assert "Exotic Saffron" in res["missing_ingredients"]
    assert res["estimated_cost"] == 50.0
