import re
import json
from pathlib import Path
from typing import List, Tuple, Optional
from app.core.config import settings

class DietValidator:
    def __init__(self, data_path: Optional[Path] = None):
        path = data_path or settings.DATA_PATH
        self.aliases_file = path / "ingredient_aliases.json"
        self.non_veg_keywords = [
            "chicken", "mutton", "lamb", "beef", "pork", "bacon", "ham",
            "veal", "turkey", "duck", "fish", "salmon", "tuna", "prawn",
            "prawns", "shrimp", "crab", "lobster", "seafood", "meat",
            "gelatin", "bone broth", "lard", "tallow"
        ]
        self.egg_keywords = ["egg", "eggs", "anda", "albumen", "mayonnaise"]
        self.dairy_keywords = [
            "milk", "cream", "butter", "cheese", "paneer", "curd",
            "dahi", "ghee", "yogurt", "yoghurt", "whey", "casein"
        ]
        self._load_data()

    def _load_data(self):
        if self.aliases_file.exists():
            try:
                with open(self.aliases_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    nv = data.get("non_vegetarian_keywords", [])
                    if nv:
                        self.non_veg_keywords = list(set(self.non_veg_keywords + [x.lower() for x in nv]))
            except Exception as e:
                print(f"Error loading diet aliases: {e}")

    def validate_diet(
        self,
        ingredient_names: List[str],
        diet_preference: str = "Vegetarian",
        disliked_ingredients: Optional[List[str]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validates a list of ingredients against the dietary preference and disliked items.
        Returns: (is_valid, list of violation messages)
        """
        violations = []
        diet_norm = (diet_preference or "").strip().lower()
        disliked = [d.strip().lower() for d in (disliked_ingredients or []) if d.strip()]

        for raw_ing in ingredient_names:
            ing = raw_ing.lower()

            # Check disliked ingredients
            for dis in disliked:
                pattern = r"(?:^|\s|\b)" + re.escape(dis) + r"(?:$|\s|\b)"
                if re.search(pattern, ing):
                    violations.append(f"Contains disliked ingredient '{raw_ing}' (matched: {dis}).")

            # Check Vegetarian diet
            if "veg" in diet_norm and "non" not in diet_norm:
                for meat in self.non_veg_keywords:
                    pattern = r"(?:^|\s|\b)" + re.escape(meat) + r"(?:$|\s|\b)"
                    if re.search(pattern, ing):
                        violations.append(f"Non-vegetarian ingredient '{raw_ing}' violates Vegetarian diet.")
                        break

            # Check Vegan diet
            if "vegan" in diet_norm:
                for meat in self.non_veg_keywords + self.dairy_keywords + self.egg_keywords + ["honey"]:
                    pattern = r"(?:^|\s|\b)" + re.escape(meat) + r"(?:$|\s|\b)"
                    if re.search(pattern, ing):
                        violations.append(f"Animal-derived ingredient '{raw_ing}' violates Vegan diet.")
                        break

        is_valid = len(violations) == 0
        return is_valid, violations

diet_validator = DietValidator()
