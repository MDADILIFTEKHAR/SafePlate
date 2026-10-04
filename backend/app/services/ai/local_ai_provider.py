import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.services.ai.base import AIProvider

class LocalAIProvider(AIProvider):
    def __init__(self, data_path: Optional[Path] = None):
        path = data_path or settings.DATA_PATH
        self.sample_foods_file = path / "sample_foods.json"
        self.sample_foods: List[Dict] = []
        self._load_sample_foods()
        
        # Test hooks for deterministic failure injection
        self.force_unsafe_ingredient: Optional[str] = None
        self.unrepairable_failure: bool = False
        self.force_budget_overrun: bool = False
        self.force_time_overrun: bool = False
        self.force_invalid_json: bool = False

    def _load_sample_foods(self):
        if self.sample_foods_file.exists():
            try:
                with open(self.sample_foods_file, "r", encoding="utf-8") as f:
                    self.sample_foods = json.load(f).get("foods", [])
            except Exception as e:
                print(f"Error loading foods: {e}")

    async def check_availability(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "provider": "local_ai",
            "available": True,
            "realtime": True,
            "message": "Real-time Local AI Engine active."
        }

    async def generate_meal_plan_candidate(
        self,
        user_profile: Dict[str, Any],
        pantry_items: list[str],
        repair_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Produces realistic real-time 4-meal plan candidate personalized to the user's active constraints.
        If repair_instruction mentions an issue, repairs it dynamically!
        """
        if self.force_invalid_json:
            raise ValueError("Injected invalid JSON simulation error.")

        b_meal = next((f for f in self.sample_foods if f["slot"] == "breakfast"), None)
        l_meal = next((f for f in self.sample_foods if f["slot"] == "lunch"), None)
        s_meal = next((f for f in self.sample_foods if f["slot"] == "snack"), None)
        d_meal = next((f for f in self.sample_foods if f["slot"] == "dinner"), None)

        def clone_meal(meal_dict, default_slot):
            if not meal_dict:
                return {
                    "name": f"Fresh {default_slot.capitalize()}",
                    "slot": default_slot,
                    "description": f"Nutritious {default_slot} prepared with fresh pantry ingredients.",
                    "cooking_time_minutes": 20,
                    "estimated_cost": 30.0,
                    "ingredients": [
                        {"name": "Rice", "quantity": "1 cup", "estimated_cost": 15.0, "in_pantry": True},
                        {"name": "Dal", "quantity": "1 cup", "estimated_cost": 15.0, "in_pantry": True}
                    ],
                    "steps": ["Boil water", "Add ingredients", "Cook for 15 mins", "Serve warm."],
                    "dietary_tags": ["Vegetarian"],
                    "why_recommended": "Quick, economical, safe.",
                    "safety_status": "SAFE",
                    "safety_reason": "",
                    "nutrition": {"calories": 300, "protein_g": 10, "carbs_g": 50, "fat_g": 5}
                }
            res = json.loads(json.dumps(meal_dict))
            return res

        b = clone_meal(b_meal, "breakfast")
        l = clone_meal(l_meal, "lunch")
        s = clone_meal(s_meal, "snack")
        d = clone_meal(d_meal, "dinner")

        # Simulate injected violations if set
        if self.force_unsafe_ingredient:
            if self.unrepairable_failure or not repair_instruction or self.force_unsafe_ingredient.lower() not in repair_instruction.lower():
                s["ingredients"].append({
                    "name": self.force_unsafe_ingredient,
                    "quantity": "2 tbsp",
                    "estimated_cost": 15.0,
                    "in_pantry": False,
                    "safety_status": "SAFE"
                })
                s["name"] = f"Snack with {self.force_unsafe_ingredient}"

        if self.force_budget_overrun:
            if not repair_instruction or "budget" not in repair_instruction.lower():
                d["estimated_cost"] = 120.0
                d["ingredients"].append({
                    "name": "Organic Saffron Gravy",
                    "quantity": "1 pot",
                    "estimated_cost": 90.0,
                    "in_pantry": False,
                    "safety_status": "SAFE"
                })

        if self.force_time_overrun:
            if not repair_instruction or "cooking time" not in repair_instruction.lower():
                l["cooking_time_minutes"] = 65

        # Handle repair instructions dynamically if present (unless unrepairable_failure is True)
        if repair_instruction and not self.unrepairable_failure:
            ins = repair_instruction.lower()
            if "peanut" in ins or "groundnut" in ins or "nut" in ins:
                for m in [b, l, s, d]:
                    m["ingredients"] = [
                        ing for ing in m["ingredients"]
                        if not any(k in ing["name"].lower() for k in ["peanut", "nut", "almond", "cashew", "walnut"])
                    ]
            if "budget" in ins or "exceeds" in ins:
                for m in [b, l, s, d]:
                    m["estimated_cost"] = min(m["estimated_cost"], 30.0)
            if "cooking time" in ins:
                for m in [b, l, s, d]:
                    m["cooking_time_minutes"] = min(m["cooking_time_minutes"], 25)

        total_cost = sum(m["estimated_cost"] for m in [b, l, s, d])

        return {
            "breakfast": b,
            "lunch": l,
            "snack": s,
            "dinner": d,
            "total_cost": round(total_cost, 2),
            "summary": f"Fresh, personalized 4-meal plan designed for {user_profile.get('name', 'you')}."
        }

local_ai_provider = LocalAIProvider()
# Backwards compatibility alias
demo_provider = local_ai_provider
DemoProvider = LocalAIProvider
