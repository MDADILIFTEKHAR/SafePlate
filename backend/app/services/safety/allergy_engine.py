import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from app.core.config import settings

class AllergyEngine:
    def __init__(self, data_path: Optional[Path] = None):
        path = data_path or settings.DATA_PATH
        self.allergens_file = path / "allergens.json"
        self.aliases_file = path / "ingredient_aliases.json"
        
        self.allergens_data: Dict = {}
        self.cross_contamination_triggers: List[str] = []
        self.aliases_data: Dict[str, str] = {}
        
        self._load_data()

    def _load_data(self):
        try:
            if self.allergens_file.exists():
                with open(self.allergens_file, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    self.allergens_data = raw.get("allergens", {})
                    self.cross_contamination_triggers = [
                        t.lower() for t in raw.get("cross_contamination_triggers", [])
                    ]
            if self.aliases_file.exists():
                with open(self.aliases_file, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    self.aliases_data = {k.lower(): v.lower() for k, v in raw.get("aliases", {}).items()}
        except Exception as e:
            print(f"Error loading allergy data: {e}")

    def normalize_text(self, text: str) -> str:
        """
        Normalize text: lowercase, remove punctuation, collapse whitespace.
        Also handles hyphenated compound words like pea-nut -> peanut.
        """
        if not text:
            return ""
        # Lowercase
        cleaned = text.lower()
        # Handle hyphenated compounds (e.g., pea-nut -> peanut, ground-nut -> groundnut)
        cleaned = re.sub(r"(\w+)-(\w+)", r"\1\2 \1 \2", cleaned)
        # Replace remaining slashes and punctuation with space
        cleaned = re.sub(r"[/_]", " ", cleaned)
        cleaned = re.sub(r"[^\w\s]", " ", cleaned)
        # Collapse multiple spaces
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def check_cross_contamination(self, text_normalized: str) -> Tuple[bool, Optional[str]]:
        for trigger in self.cross_contamination_triggers:
            trigger_norm = self.normalize_text(trigger)
            if trigger_norm and trigger_norm in text_normalized:
                return True, trigger
        return False, None

    def match_allergens_in_text(self, text: str, user_allergens: List[str]) -> Dict:
        """
        Deterministic allergy evaluation:
        Returns:
            {
                "status": "SAFE" | "CAUTION" | "AVOID" | "UNKNOWN",
                "reason": str,
                "matched_terms": list,
                "matched_allergens": list,
                "confidence": "high" | "medium"
            }
        """
        if not text or not text.strip():
            return {
                "status": "UNKNOWN",
                "reason": "Empty or blank food query provided.",
                "matched_terms": [],
                "matched_allergens": [],
                "confidence": "low"
            }

        norm_text = self.normalize_text(text)
        
        # Check for unknown / unverified flags
        unknown_indicators = [
            "unknown", "unlabeled", "mystery", "unspecified ingredient",
            "proprietary blend", "artificial flavour code", "e-number", "unverified"
        ]
        is_unknown_flagged = any(u in norm_text for u in unknown_indicators)

        # Normalize user active allergens
        user_allergen_codes = set()
        user_allergen_map = {}  # code -> display name
        
        for a in user_allergens:
            a_norm = a.strip().upper()
            # Map friendly names to codes
            if "PEANUT" in a_norm or "GROUNDNUT" in a_norm:
                user_allergen_codes.add("PEANUT")
                user_allergen_map["PEANUT"] = "Peanut"
            elif "TREE" in a_norm or "NUT" in a_norm or "ALMOND" in a_norm or "CASHEW" in a_norm or "WALNUT" in a_norm or "PISTACHIO" in a_norm:
                user_allergen_codes.add("TREE_NUT")
                user_allergen_map["TREE_NUT"] = "Tree Nuts"
            elif "MILK" in a_norm or "DAIRY" in a_norm or "LACTOSE" in a_norm:
                user_allergen_codes.add("MILK")
                user_allergen_map["MILK"] = "Dairy"
            elif "EGG" in a_norm:
                user_allergen_codes.add("EGG")
                user_allergen_map["EGG"] = "Egg"
            elif "WHEAT" in a_norm or "GLUTEN" in a_norm:
                user_allergen_codes.add("WHEAT")
                user_allergen_map["WHEAT"] = "Wheat / Gluten"
            elif "SOY" in a_norm:
                user_allergen_codes.add("SOY")
                user_allergen_map["SOY"] = "Soy"
            elif "FISH" in a_norm:
                user_allergen_codes.add("FISH")
                user_allergen_map["FISH"] = "Fish"
            elif "SHELLFISH" in a_norm or "CRUSTACEAN" in a_norm or "PRAWN" in a_norm or "SHRIMP" in a_norm:
                user_allergen_codes.add("SHELLFISH")
                user_allergen_map["SHELLFISH"] = "Shellfish"
            elif "SESAME" in a_norm:
                user_allergen_codes.add("SESAME")
                user_allergen_map["SESAME"] = "Sesame"
            elif "MUSTARD" in a_norm:
                user_allergen_codes.add("MUSTARD")
                user_allergen_map["MUSTARD"] = "Mustard"
            else:
                user_allergen_codes.add(a_norm)
                user_allergen_map[a_norm] = a

        # Check for cross-contamination warning first
        is_cross_contaminated, trigger_found = self.check_cross_contamination(norm_text)

        direct_matches = []
        matched_allergens = set()

        # Check each allergen code against keywords and aliases
        for code, details in self.allergens_data.items():
            if code not in user_allergen_codes:
                continue

            keywords = details.get("keywords", [])
            for kw in keywords:
                kw_norm = self.normalize_text(kw)
                # Word boundary match to avoid false substrings (e.g. 'nut' in 'minute')
                pattern = r"(?:^|\s|\b)" + re.escape(kw_norm) + r"(?:$|\s|\b)"
                if re.search(pattern, norm_text):
                    direct_matches.append(kw)
                    matched_allergens.add(code)

        # Check aliases
        for alias, canonical in self.aliases_data.items():
            alias_norm = self.normalize_text(alias)
            pattern = r"(?:^|\s|\b)" + re.escape(alias_norm) + r"(?:$|\s|\b)"
            if re.search(pattern, norm_text):
                # See if canonical is an allergen
                for code, details in self.allergens_data.items():
                    if code not in user_allergen_codes:
                        continue
                    if canonical in [self.normalize_text(k) for k in details.get("keywords", [])]:
                        direct_matches.append(alias)
                        matched_allergens.add(code)

        direct_matches = list(dict.fromkeys(direct_matches))
        matched_allergens_list = list(matched_allergens)

        # 1. DIRECT ALLERGEN -> AVOID
        # Even if cross-contamination phrase is present, if it directly specifies the allergen,
        # but if the WHOLE text is purely a trace warning like "may contain traces of peanuts",
        # let's distinguish:
        if direct_matches:
            if is_cross_contaminated and (len(norm_text.split()) <= 10 or norm_text.startswith("may contain") or "traces" in norm_text or "facility" in norm_text or "equipment" in norm_text):
                # Pure trace warning: return CAUTION
                allergen_names = [user_allergen_map.get(c, c) for c in matched_allergens_list]
                return {
                    "status": "CAUTION",
                    "reason": f"Facility or trace warning detected ({trigger_found}) mentioning {', '.join(direct_matches)}. Potential cross-contact risk for {', '.join(allergen_names)}.",
                    "matched_terms": direct_matches,
                    "matched_allergens": allergen_names,
                    "confidence": "medium"
                }
            else:
                # Direct allergen present -> AVOID
                allergen_names = [user_allergen_map.get(c, c) for c in matched_allergens_list]
                return {
                    "status": "AVOID",
                    "reason": f"Direct allergen conflict: Contains '{', '.join(direct_matches)}', which violates your declared {', '.join(allergen_names)} allergy.",
                    "matched_terms": direct_matches,
                    "matched_allergens": allergen_names,
                    "confidence": "high"
                }

        # 2. Cross-contamination warning without specific matched user allergen
        if is_cross_contaminated:
            return {
                "status": "CAUTION",
                "reason": f"Label contains shared manufacturing advisory ('{trigger_found}'). Exercise caution and review full packaging.",
                "matched_terms": [trigger_found],
                "matched_allergens": [],
                "confidence": "medium"
            }

        # 3. Unknown indicator
        if is_unknown_flagged:
            return {
                "status": "UNKNOWN",
                "reason": "Contains unspecified, unverified or ambiguous ingredient text. SafePlate cannot verify safety without label clarity.",
                "matched_terms": ["unverified ingredient"],
                "matched_allergens": [],
                "confidence": "low"
            }

        # 4. No conflict detected -> SAFE
        return {
            "status": "SAFE",
            "reason": f"No declared allergen conflicts detected for your profile ({', '.join(user_allergens) if user_allergens else 'No allergies declared'}).",
            "matched_terms": [],
            "matched_allergens": [],
            "confidence": "high"
        }

    def validate_ingredients_list(self, ingredients: List[str], user_allergens: List[str]) -> Tuple[str, List[str], List[str]]:
        """
        Evaluates a list of ingredients.
        Returns: (overall_status, reasons, offending_ingredients)
        Invariants:
        - If any ingredient is AVOID -> overall status is AVOID.
        - Else if any is CAUTION -> overall status is CAUTION.
        - Else if any is UNKNOWN -> overall status is UNKNOWN.
        - Else SAFE.
        """
        worst_status = "SAFE"
        status_priority = {"AVOID": 4, "CAUTION": 3, "UNKNOWN": 2, "SAFE": 1}
        reasons = []
        offending = []

        for ing in ingredients:
            res = self.match_allergens_in_text(ing, user_allergens)
            st = res["status"]
            if status_priority[st] > status_priority[worst_status]:
                worst_status = st
            if st != "SAFE":
                reasons.append(f"{ing}: {res['reason']}")
                offending.append(ing)

        if not reasons:
            reasons.append("All listed ingredients verified safe against active allergy profile.")

        return worst_status, reasons, offending

allergy_engine = AllergyEngine()
