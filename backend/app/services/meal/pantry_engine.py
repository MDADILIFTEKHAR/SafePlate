import re
from typing import List, Dict, Any, Tuple
from app.services.safety.allergy_engine import allergy_engine

class PantryEngine:
    @staticmethod
    def match_ingredients_with_pantry(
        recipe_ingredients: List[Dict[str, Any]],
        pantry_items: List[str]
    ) -> Dict[str, Any]:
        """
        Compares recipe ingredients against available pantry items.
        Marks in_pantry=True/False and computes:
        - used_ingredients (items found in pantry)
        - missing_ingredients (items user needs to acquire)
        - estimated_cost (marginal cost considering pantry items as 0 added cost)
        """
        normalized_pantry = [allergy_engine.normalize_text(p) for p in pantry_items if p]
        
        used_ingredients = []
        missing_ingredients = []
        updated_ingredients = []
        total_additional_cost = 0.0

        for item in recipe_ingredients:
            name = item.get("name", "")
            norm_name = allergy_engine.normalize_text(name)
            base_cost = float(item.get("estimated_cost", 0.0))
            
            # Match against pantry items (e.g. "poha (flattened rice)" vs "poha", "tomato" in "1 tomato diced")
            in_pantry = False
            for p_norm in normalized_pantry:
                pattern = r"(?:^|\s|\b)" + re.escape(p_norm) + r"(?:$|\s|\b)"
                if re.search(pattern, norm_name) or p_norm in norm_name:
                    in_pantry = True
                    break

            item_copy = dict(item)
            item_copy["in_pantry"] = in_pantry

            if in_pantry:
                used_ingredients.append(name)
                # In pantry means ₹0 added shopping expense for today
                item_copy["effective_cost"] = 0.0
            else:
                missing_ingredients.append(name)
                item_copy["effective_cost"] = base_cost
                total_additional_cost += base_cost

            updated_ingredients.append(item_copy)

        return {
            "ingredients": updated_ingredients,
            "used_ingredients": used_ingredients,
            "missing_ingredients": missing_ingredients,
            "estimated_cost": round(total_additional_cost, 2)
        }

pantry_engine = PantryEngine()
