from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AIProvider(ABC):
    @abstractmethod
    async def generate_meal_plan_candidate(
        self,
        user_profile: Dict[str, Any],
        pantry_items: list[str],
        repair_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates candidate 4-meal plan matching structured schema.
        Must return a dictionary conforming to MealPlanCandidate schema.
        """
        pass

    @abstractmethod
    async def check_availability(self) -> Dict[str, Any]:
        """
        Checks if the provider is responsive and operational.
        """
        pass
