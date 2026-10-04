import time
import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.ai.base import AIProvider
from app.services.ai.provider_factory import provider_factory
from app.services.safety.allergy_engine import allergy_engine
from app.services.safety.diet_validator import diet_validator
from app.services.budget.budget_validator import budget_validator
from app.services.meal.time_validator import time_validator
from app.services.meal.pantry_engine import pantry_engine
from app.models.entities import AgentRun

class AgentLoop:
    def __init__(
        self,
        max_iterations: int = settings.MAX_AGENT_ITERATIONS,
        ai_provider: Optional[AIProvider] = None
    ):
        self.max_iterations = max_iterations
        self.ai_provider = ai_provider or provider_factory.get_provider()

    async def execute_plan_generation(
        self,
        profile_data: Dict[str, Any],
        pantry_items: List[str],
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Executes bounded agent loop (max iterations = 3) to generate safe meal plan.
        """
        start_time = time.time()
        run_id = f"run-{uuid.uuid4().hex[:12]}"
        user_id = profile_data.get("id", 1)
        user_allergies = profile_data.get("allergies", [])
        diet_preference = profile_data.get("dietary_preference", "Vegetarian")
        disliked_items = profile_data.get("disliked_ingredients", [])
        daily_budget = float(profile_data.get("daily_budget", 150.0))
        max_cooking_time = int(profile_data.get("max_cooking_time_minutes", 30))

        steps_records = []
        all_violations = []
        all_repairs = []
        final_candidate = None
        repair_instruction = None
        success = False

        for iteration in range(1, self.max_iterations + 1):
            iter_start = time.time()
            
            # Step 1: AI generates candidate
            candidate = await self.ai_provider.generate_meal_plan_candidate(
                user_profile=profile_data,
                pantry_items=pantry_items,
                repair_instruction=repair_instruction
            )
            
            # Step 2: Validate Candidate across all safety and constraint layers
            is_valid, violations, processed_candidate, explainability = self._validate_and_enrich_candidate(
                candidate=candidate,
                user_allergies=user_allergies,
                diet_preference=diet_preference,
                disliked_items=disliked_items,
                daily_budget=daily_budget,
                max_cooking_time=max_cooking_time,
                pantry_items=pantry_items
            )

            all_violations.extend(violations)
            step_record = {
                "iteration": iteration,
                "candidate_summary": processed_candidate.get("summary", "4-meal plan candidate"),
                "violations": list(violations),
                "repair_instruction": repair_instruction,
                "status": "valid" if is_valid else "violates_constraints",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "duration_ms": round((time.time() - iter_start) * 1000, 2)
            }
            steps_records.append(step_record)

            if is_valid:
                # FINAL SAFETY GATE
                final_gate_passed, gate_reason = self._final_safety_gate(processed_candidate, user_allergies)
                if final_gate_passed:
                    success = True
                    final_candidate = processed_candidate
                    final_candidate["explainability"] = explainability
                    break
                else:
                    violations.append(f"Final safety gate rejected candidate: {gate_reason}")

            # If invalid and not at max iterations, formulate targeted repair instructions
            if iteration < self.max_iterations:
                repair_instruction = self._build_repair_instructions(violations, daily_budget, max_cooking_time)
                all_repairs.append(repair_instruction)

        total_duration = round((time.time() - start_time) * 1000, 2)
        final_status = "SUCCESS" if (success and len(steps_records) == 1) else ("REPAIRED" if success else "FAILED_MAX_ITERATIONS")

        # Persist AgentRun record in database
        if db:
            try:
                db_record = AgentRun(
                    id=run_id,
                    user_id=user_id,
                    prompt_type="meal_plan_generation",
                    iteration_count=len(steps_records),
                    final_status=final_status,
                    violations=json.dumps(all_violations),
                    repair_actions=json.dumps(all_repairs),
                    execution_time_ms=total_duration,
                    steps_data=json.dumps(steps_records)
                )
                db.add(db_record)
                db.commit()
            except Exception as e:
                print(f"Error persisting agent run: {e}")

        if success and final_candidate:
            return {
                "success": True,
                "run_id": run_id,
                "status": final_status,
                "iterations": len(steps_records),
                "execution_time_ms": total_duration,
                "meal_plan": final_candidate,
                "steps": steps_records
            }
        else:
            return {
                "success": False,
                "run_id": run_id,
                "status": "FAILED_MAX_ITERATIONS",
                "iterations": len(steps_records),
                "execution_time_ms": total_duration,
                "message": "SafePlate couldn't generate a meal satisfying all constraints. Try increasing your budget, cooking time, or available ingredients.",
                "violations": all_violations[-4:] if all_violations else ["Exceeded maximum iteration budget."],
                "steps": steps_records,
                "alternative_actions": [
                    {"label": "Relax Budget", "action": "increase_budget", "suggested_value": daily_budget + 40},
                    {"label": "Increase Cooking Time", "action": "increase_time", "suggested_value": max_cooking_time + 15},
                    {"label": "Use Pantry", "action": "force_pantry"},
                    {"label": "Try Again", "action": "retry"}
                ]
            }

    def _validate_and_enrich_candidate(
        self,
        candidate: Dict[str, Any],
        user_allergies: List[str],
        diet_preference: str,
        disliked_items: List[str],
        daily_budget: float,
        max_cooking_time: int,
        pantry_items: List[str]
    ) -> Tuple[bool, List[str], Dict[str, Any], List[str]]:
        violations = []
        explainability = []
        slots = ["breakfast", "lunch", "snack", "dinner"]
        enriched_candidate = dict(candidate)
        meal_costs = {}

        pantry_items_used = 0
        total_ingredients_count = 0

        for slot in slots:
            meal = candidate.get(slot, {})
            name = meal.get("name", f"Unnamed {slot}")
            raw_ingredients = meal.get("ingredients", [])
            cooking_time = int(meal.get("cooking_time_minutes", 20))

            # Quality validation: Minimum ingredient and step counts
            if not raw_ingredients or len(raw_ingredients) < 1:
                violations.append(f"{slot.capitalize()} ({name}) has no ingredients.")
            
            # Step-by-step pantry matching & cost enrichment
            pantry_match = pantry_engine.match_ingredients_with_pantry(raw_ingredients, pantry_items)
            enriched_ingredients = pantry_match["ingredients"]
            meal["ingredients"] = enriched_ingredients
            pantry_items_used += len(pantry_match["used_ingredients"])
            total_ingredients_count += len(enriched_ingredients)

            # Deterministic cost calculation
            calculated_cost = budget_validator.calculate_meal_cost(enriched_ingredients)
            meal["estimated_cost"] = calculated_cost
            meal_costs[slot] = calculated_cost

            # Step 1: Allergy Validation
            ingredient_names = [ing.get("name", "") for ing in enriched_ingredients]
            status, reasons, offending = allergy_engine.validate_ingredients_list(ingredient_names, user_allergies)
            meal["safety_status"] = status
            meal["safety_reason"] = "; ".join(reasons)

            if status != "SAFE":
                violations.append(f"{slot.capitalize()} contains unsafe/unverified ingredients: {', '.join(offending)} ({meal['safety_reason']}).")

            # Step 2: Diet & Dislike Validation
            is_diet_valid, diet_violations = diet_validator.validate_diet(
                ingredient_names=ingredient_names,
                diet_preference=diet_preference,
                disliked_ingredients=disliked_items
            )
            if not is_diet_valid:
                violations.extend([f"{slot.capitalize()}: {v}" for v in diet_violations])

            # Step 3: Cooking Time Validation
            is_time_valid, time_msg = time_validator.validate_meal_time(cooking_time, max_cooking_time)
            if not is_time_valid:
                violations.append(f"{slot.capitalize()}: {time_msg}")

            enriched_candidate[slot] = meal

        # Step 4: Deterministic Budget Validation across whole day
        budget_res = budget_validator.validate_plan_budget(meal_costs, daily_budget)
        enriched_candidate["total_cost"] = budget_res["amount"]

        if not budget_res["within_budget"]:
            violations.extend(budget_res["violations"])

        # Explainability points
        if not violations:
            explainability.append(f"✓ Within daily budget (₹{budget_res['amount']} / ₹{daily_budget})")
            explainability.append(f"✓ All meals prepare under {max_cooking_time} minutes")
            explainability.append(f"✓ 100% compliant with {diet_preference} diet")
            explainability.append(f"✓ No declared allergens detected ({', '.join(user_allergies) if user_allergies else 'None'})")
            if pantry_items_used > 0:
                explainability.append(f"✓ Uses {pantry_items_used} ingredients directly from your pantry")

        is_valid = len(violations) == 0
        return is_valid, violations, enriched_candidate, explainability

    def _final_safety_gate(self, candidate: Dict[str, Any], user_allergies: List[str]) -> Tuple[bool, str]:
        """
        Final safety gate:
        Invariant: If meal contains a declared direct allergen, status MUST NOT be SAFE.
        Invariant: If final status is SAFE, no deterministic allergy conflict can exist.
        """
        for slot in ["breakfast", "lunch", "snack", "dinner"]:
            meal = candidate.get(slot, {})
            if meal.get("safety_status") != "SAFE":
                return False, f"{slot} safety status is {meal.get('safety_status')}"
            
            # Double check all ingredients directly against allergy engine
            for ing in meal.get("ingredients", []):
                res = allergy_engine.match_allergens_in_text(ing.get("name", ""), user_allergies)
                if res["status"] != "SAFE":
                    return False, f"Ingredient {ing.get('name')} triggered {res['status']}: {res['reason']}"

        return True, "All meals passed final safety gate."

    def _build_repair_instructions(self, violations: List[str], daily_budget: float, max_cooking_time: int) -> str:
        instructions = ["Previous plan had the following constraint violations:"]
        for v in violations:
            instructions.append(f"- {v}")
        instructions.append(f"Ensure total cost is <= ₹{daily_budget} and every meal takes <= {max_cooking_time} minutes.")
        instructions.append("Remove all conflicting allergens and substitute with safe pantry items.")
        return "\n".join(instructions)

agent_loop = AgentLoop()
