import json
import httpx
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.ai.base import AIProvider
from app.services.ai.local_ai_provider import local_ai_provider

class OllamaProvider(AIProvider):
    def __init__(
        self,
        base_url: str = settings.OLLAMA_BASE_URL,
        model_name: str = settings.MODEL_NAME,
        timeout_seconds: int = settings.LLM_TIMEOUT_SECONDS
    ):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    async def check_availability(self) -> Dict[str, Any]:
        """
        Pings Ollama `/api/tags` to verify connectivity and list models.
        """
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    model_present = any(self.model_name in m for m in models)
                    return {
                        "status": "ok",
                        "provider": "ollama",
                        "available": True,
                        "base_url": self.base_url,
                        "configured_model": self.model_name,
                        "available_models": models,
                        "model_ready": model_present
                    }
                return {
                    "status": "error",
                    "provider": "ollama",
                    "available": False,
                    "error": f"Ollama HTTP {res.status_code}"
                }
        except Exception as e:
            return {
                "status": "offline",
                "provider": "ollama",
                "available": False,
                "error": str(e)
            }

    def _build_prompt(
        self,
        user_profile: Dict[str, Any],
        pantry_items: list[str],
        repair_instruction: Optional[str] = None
    ) -> str:
        prompt = f"""You are SafePlate AI, an allergy-safe culinary assistant.
Generate a strictly formatted JSON daily meal plan with 4 meals: breakfast, lunch, snack, dinner.

CRITICAL CONSTRAINTS:
1. User Name: {user_profile.get('name', 'User')}
2. ALLERGIES (STRICTLY PROHIBITED - DO NOT USE ANY DERIVATIVES): {', '.join(user_profile.get('allergies', []))}
3. Diet: {user_profile.get('dietary_preference', 'Vegetarian')}
4. Cuisines: {', '.join(user_profile.get('cuisines', ['Indian']))}
5. Max cooking time: {user_profile.get('max_cooking_time_minutes', 30)} minutes per meal.
6. Daily Budget: ₹{user_profile.get('daily_budget', 150)} total for all 4 meals.
7. Available Pantry Items (Prioritize these to save cost): {', '.join(pantry_items)}
"""
        if repair_instruction:
            prompt += f"\nREPAIR REQUIRED FROM PREVIOUS ATTEMPT:\n{repair_instruction}\nYou must fix these exact violations!\n"

        prompt += """
RESPONSE FORMAT: Return ONLY valid JSON matching this schema:
{
  "breakfast": {
    "name": "...",
    "slot": "breakfast",
    "description": "...",
    "cooking_time_minutes": 15,
    "estimated_cost": 30.0,
    "ingredients": [{"name": "...", "quantity": "...", "estimated_cost": 10.0, "in_pantry": true}],
    "steps": ["Step 1", "Step 2"],
    "dietary_tags": ["Vegetarian", "Nut-Free"],
    "why_recommended": "..."
  },
  "lunch": { ... },
  "snack": { ... },
  "dinner": { ... },
  "total_cost": 120.0,
  "summary": "..."
}
"""
        return prompt

    async def generate_meal_plan_candidate(
        self,
        user_profile: Dict[str, Any],
        pantry_items: list[str],
        repair_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calls Ollama with 3-attempt recovery strategy:
        Attempt 1: Structured generation
        Attempt 2: Correction prompt if malformed/unresponsive
        Attempt 3: Fallback deterministic generator
        """
        prompt = self._build_prompt(user_profile, pantry_items, repair_instruction)

        # Attempt 1
        try:
            raw_json = await self._call_ollama(prompt)
            parsed = self._extract_json(raw_json)
            if self._validate_structure(parsed):
                return parsed
        except Exception as e:
            print(f"[Ollama Attempt 1 Failed]: {e}")

        # Attempt 2: Correction prompt
        try:
            correction_prompt = f"The previous output was malformed or missing keys. Return strictly valid JSON with keys: breakfast, lunch, snack, dinner, total_cost, summary. Context:\n{prompt}"
            raw_json_2 = await self._call_ollama(correction_prompt)
            parsed_2 = self._extract_json(raw_json_2)
            if self._validate_structure(parsed_2):
                return parsed_2
        except Exception as e:
            print(f"[Ollama Attempt 2 Failed]: {e}")

        # Attempt 3: Fallback deterministic meal generator
        print("[Ollama Fallback]: Generating deterministic safe plan via real-time local engine.")
        fallback = await local_ai_provider.generate_meal_plan_candidate(user_profile, pantry_items, repair_instruction)
        return fallback

    async def _call_ollama(self, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.3
                }
            }
            res = await client.post(f"{self.base_url}/api/generate", json=payload)
            if res.status_code != 200:
                raise RuntimeError(f"Ollama returned HTTP {res.status_code}: {res.text}")
            data = res.json()
            return data.get("response", "")

    def _extract_json(self, text: str) -> Dict[str, Any]:
        # Handle markdown blocks if any
        clean = text.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        return json.loads(clean.strip())

    def _validate_structure(self, data: Any) -> bool:
        if not isinstance(data, dict):
            return False
        required_slots = ["breakfast", "lunch", "snack", "dinner"]
        for s in required_slots:
            if s not in data or not isinstance(data[s], dict):
                return False
            if "name" not in data[s] or "ingredients" not in data[s]:
                return False
        return True
