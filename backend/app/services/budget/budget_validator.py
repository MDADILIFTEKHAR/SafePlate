from typing import List, Dict, Tuple, Any

class BudgetValidator:
    DEFAULT_SLOT_TARGETS = {
        "breakfast": 0.23,  # ~ ₹35 of ₹150 (23.3%)
        "lunch": 0.33,      # ~ ₹50 of ₹150 (33.3%)
        "snack": 0.14,      # ~ ₹20 of ₹150 (13.3%)
        "dinner": 0.30      # ~ ₹45 of ₹150 (30.0%)
    }

    @staticmethod
    def calculate_meal_cost(ingredients: List[Dict[str, Any]]) -> float:
        """
        Deterministic calculation of single meal cost from ingredients.
        Pantry items count as ₹0 added cost for today's meal.
        """
        total = 0.0
        for item in ingredients:
            # If in pantry, marginal additional cost is 0
            if item.get("in_pantry", False):
                continue
            cost = float(item.get("estimated_cost", 0.0))
            if cost > 0:
                total += cost
        return round(total, 2)

    @staticmethod
    def validate_plan_budget(
        meal_costs: Dict[str, float],
        daily_budget: float
    ) -> Dict[str, Any]:
        """
        Validates total meal plan cost against user's daily budget.
        Returns:
            {
                "within_budget": bool,
                "amount": float,
                "remaining": float,
                "daily_budget": float,
                "violations": list[str],
                "per_meal_analysis": dict
            }
        """
        if daily_budget <= 0:
            raise ValueError("Daily budget must be greater than zero.")

        # Invariant: total amount is exact deterministic sum of meal costs
        total_amount = round(sum(float(c) for c in meal_costs.values()), 2)
        remaining = round(daily_budget - total_amount, 2)
        violations = []
        within_budget = total_amount <= daily_budget

        if not within_budget:
            excess = round(total_amount - daily_budget, 2)
            violations.append(
                f"Total meal plan cost ₹{total_amount} exceeds daily budget of ₹{daily_budget} by ₹{excess}."
            )

        per_meal_analysis = {}
        for slot, cost in meal_costs.items():
            target_pct = BudgetValidator.DEFAULT_SLOT_TARGETS.get(slot.lower(), 0.25)
            target_amount = round(daily_budget * target_pct, 2)
            per_meal_analysis[slot] = {
                "cost": round(cost, 2),
                "target": target_amount,
                "over_target": cost > (target_amount * 1.25)  # 25% tolerance per slot
            }

        return {
            "within_budget": within_budget,
            "amount": total_amount,
            "remaining": remaining,
            "daily_budget": daily_budget,
            "violations": violations,
            "per_meal_analysis": per_meal_analysis
        }

budget_validator = BudgetValidator()
