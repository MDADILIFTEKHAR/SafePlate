import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from app.core.config import settings
from app.services.safety.allergy_engine import allergy_engine
from app.services.safety.diet_validator import diet_validator

class SubstitutionEngine:
    def __init__(self, data_path: Optional[Path] = None):
        path = data_path or settings.DATA_PATH
        self.substitutions_file = path / "substitutions.json"
        self.substitutions_data: Dict[str, List[Dict[str, Any]]] = {}
        self._load_data()

    def _load_data(self):
        if self.substitutions_file.exists():
            try:
                with open(self.substitutions_file, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    self.substitutions_data = raw.get("substitutions", {})
            except Exception as e:
                print(f"Error loading substitutions: {e}")

    def find_safe_substitution(
        self,
        unsafe_ingredient: str,
        user_allergies: List[str],
        diet_preference: str = "Vegetarian",
        disliked_ingredients: Optional[List[str]] = None,
        max_attempts: int = 3
    ) -> Tuple[Optional[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Runs the smart substitution loop:
        Tries substitutions one-by-one up to max_attempts (default 3).
        Validates:
        1. Allergy validation
        2. Diet validation
        Returns (accepted_substitution, history_of_attempts)
        Invariant: Never accepts an unvalidated substitution.
        """
        norm_unsafe = allergy_engine.normalize_text(unsafe_ingredient)
        options = []

        # Find matching key in substitutions data
        for key, candidate_list in self.substitutions_data.items():
            norm_key = allergy_engine.normalize_text(key)
            if norm_key in norm_unsafe or norm_unsafe in norm_key:
                options = candidate_list
                break

        if not options:
            return None, []

        history = []
        accepted = None
        attempts = 0

        for candidate in options:
            if attempts >= max_attempts:
                break
            attempts += 1

            sub_name = candidate["substitute"]
            
            # Step 1: Deterministic Allergy Validation
            allergy_res = allergy_engine.match_allergens_in_text(sub_name, user_allergies)
            is_allergy_safe = allergy_res["status"] == "SAFE"

            # Step 2: Deterministic Diet Validation
            diet_safe, diet_violations = diet_validator.validate_diet(
                [sub_name],
                diet_preference=diet_preference,
                disliked_ingredients=disliked_ingredients
            )

            is_valid = is_allergy_safe and diet_safe
            reason = ""
            if not is_allergy_safe:
                reason = f"Allergy conflict: {allergy_res['reason']}"
            elif not diet_safe:
                reason = f"Diet conflict: {', '.join(diet_violations)}"
            else:
                reason = "Verified safe for your allergy and diet profile."

            attempt_record = {
                "attempt": attempts,
                "substitute": sub_name,
                "category": candidate.get("category", "General"),
                "flavor_profile": candidate.get("flavor_profile", ""),
                "is_safe": is_valid,
                "reason": reason,
                "cost_multiplier": candidate.get("cost_multiplier", 1.0)
            }
            history.append(attempt_record)

            if is_valid and accepted is None:
                accepted = attempt_record
                # Continue loop only if we want to record all or stop here:
                # We can return immediately once accepted, but having history is great for explainability!
                break

        return accepted, history

substitution_engine = SubstitutionEngine()
