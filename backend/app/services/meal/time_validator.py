from typing import Dict, List, Tuple

class TimeValidator:
    @staticmethod
    def validate_meal_time(cooking_time_minutes: int, max_time_minutes: int) -> Tuple[bool, str]:
        if max_time_minutes <= 0:
            raise ValueError("Maximum cooking time must be greater than zero.")
            
        if cooking_time_minutes > max_time_minutes:
            excess = cooking_time_minutes - max_time_minutes
            return False, f"Cooking time ({cooking_time_minutes} mins) exceeds your limit of {max_time_minutes} mins by {excess} mins."
        return True, f"Cooking time ({cooking_time_minutes} mins) is within your limit ({max_time_minutes} mins)."

    @staticmethod
    def validate_plan_times(meals: List[Dict], max_time_minutes: int) -> Tuple[bool, List[str]]:
        violations = []
        for meal in meals:
            time_mins = int(meal.get("cooking_time_minutes", 0))
            is_valid, msg = TimeValidator.validate_meal_time(time_mins, max_time_minutes)
            if not is_valid:
                violations.append(f"{meal.get('name', 'Meal')}: {msg}")
        return len(violations) == 0, violations

time_validator = TimeValidator()
