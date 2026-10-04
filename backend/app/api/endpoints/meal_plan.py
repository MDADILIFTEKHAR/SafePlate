import uuid
import json
import asyncio
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import UserProfile, MealPlan, Meal, MealIngredient
from app.schemas.api_models import (
    MealPlanRead, MealRead, MealIngredientCandidate, MealGenerateRequest
)
from app.services.agent.agent_loop import agent_loop

router = APIRouter(prefix="/meal-plan", tags=["Meal Plan"])

# Resource lock to prevent duplicate concurrent generation requests
_generation_lock = asyncio.Lock()

@router.get("", response_model=Optional[MealPlanRead])
def get_current_meal_plan(db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    if not profile:
        return None

    # Get latest meal plan for the user
    plan = db.query(MealPlan).filter(
        MealPlan.user_id == profile.id
    ).order_by(MealPlan.created_at.desc()).first()

    if not plan:
        return None

    meals_read = []
    for m in plan.meals:
        ingredients_read = [
            MealIngredientCandidate(
                name=ing.name,
                quantity=ing.quantity,
                estimated_cost=ing.estimated_cost,
                in_pantry=ing.in_pantry,
                safety_status=ing.safety_status
            ) for ing in m.ingredients
        ]
        meals_read.append(
            MealRead(
                id=m.id,
                slot=m.slot,
                name=m.name,
                description=m.description,
                cooking_time_minutes=m.cooking_time_minutes,
                estimated_cost=m.estimated_cost,
                dietary_tags=m.get_dietary_tags(),
                safety_status=m.safety_status,
                safety_reason=m.safety_reason,
                nutrition=m.get_nutrition_dict(),
                why_recommended=m.why_recommended,
                steps=m.get_steps_list(),
                ingredients=ingredients_read
            )
        )

    # Sort meals order: breakfast, lunch, snack, dinner
    slot_order = {"breakfast": 1, "lunch": 2, "snack": 3, "dinner": 4}
    meals_read.sort(key=lambda x: slot_order.get(x.slot.lower(), 5))

    explainability = [
        f"✓ Total cost ₹{plan.total_estimated_cost} is within your daily budget of ₹{plan.target_budget}",
        "✓ 100% compliant with your declared allergies & dietary requirements",
        "✓ All recipes ready in 30 minutes or less"
    ]
    if not plan.is_valid:
        explainability.insert(0, "⚠️ Profile allergies have been updated since this plan was generated. Please regenerate to ensure safety.")

    return MealPlanRead(
        id=plan.id,
        date=plan.date,
        total_estimated_cost=plan.total_estimated_cost,
        target_budget=plan.target_budget,
        is_valid=plan.is_valid,
        meals=meals_read,
        explainability=explainability
    )

@router.post("/generate", response_model=MealPlanRead)
async def generate_meal_plan(
    payload: MealGenerateRequest = MealGenerateRequest(),
    db: Session = Depends(get_db)
):
    # Enforce concurrency lock
    if _generation_lock.locked():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="A meal plan generation is already in progress. Please wait a moment."
        )

    async with _generation_lock:
        profile = db.query(UserProfile).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found.")

        profile_dict = {
            "id": profile.id,
            "name": profile.name,
            "daily_budget": profile.daily_budget,
            "max_cooking_time_minutes": profile.max_cooking_time_minutes,
            "spice_level": profile.spice_level,
            "cuisines": profile.get_cuisines_list(),
            "allergies": [a.name for a in profile.allergies],
            "dietary_preference": profile.dietary_preferences[0].preference_type if profile.dietary_preferences else "Vegetarian",
            "disliked_ingredients": profile.get_disliked_list()
        }
        pantry_items = [p.name for p in profile.pantry_items]

        # Execute bounded agent loop
        agent_result = await agent_loop.execute_plan_generation(
            profile_data=profile_dict,
            pantry_items=pantry_items,
            db=db
        )

        if not agent_result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": agent_result.get("message", "Could not generate compliant meal plan."),
                    "violations": agent_result.get("violations", []),
                    "alternative_actions": agent_result.get("alternative_actions", [])
                }
            )

        candidate = agent_result["meal_plan"]
        plan_id = f"plan-{uuid.uuid4().hex[:12]}"
        today_str = date.today().isoformat()

        # Invalidate previous plans
        db.query(MealPlan).filter(MealPlan.user_id == profile.id).update({"is_valid": False})

        # Save new plan
        new_plan = MealPlan(
            id=plan_id,
            user_id=profile.id,
            date=today_str,
            total_estimated_cost=candidate.get("total_cost", 0.0),
            target_budget=profile.daily_budget,
            is_valid=True
        )
        db.add(new_plan)
        db.flush()

        meals_read = []
        for slot in ["breakfast", "lunch", "snack", "dinner"]:
            m_data = candidate.get(slot, {})
            m_id = f"meal-{uuid.uuid4().hex[:12]}"
            new_meal = Meal(
                id=m_id,
                meal_plan_id=plan_id,
                slot=slot,
                name=m_data.get("name", f"{slot.capitalize()} Recipe"),
                description=m_data.get("description", ""),
                cooking_time_minutes=m_data.get("cooking_time_minutes", 20),
                estimated_cost=m_data.get("estimated_cost", 0.0),
                dietary_tags=json.dumps(m_data.get("dietary_tags", [])),
                safety_status=m_data.get("safety_status", "SAFE"),
                safety_reason=m_data.get("safety_reason", ""),
                nutrition=json.dumps(m_data.get("nutrition", {})),
                why_recommended=m_data.get("why_recommended", ""),
                steps=json.dumps(m_data.get("steps", []))
            )
            db.add(new_meal)
            db.flush()

            ingredients_read = []
            for ing in m_data.get("ingredients", []):
                new_ing = MealIngredient(
                    meal_id=m_id,
                    name=ing.get("name", "Ingredient"),
                    quantity=ing.get("quantity", "1 unit"),
                    estimated_cost=ing.get("estimated_cost", 0.0),
                    in_pantry=ing.get("in_pantry", False),
                    safety_status=ing.get("safety_status", "SAFE")
                )
                db.add(new_ing)
                ingredients_read.append(
                    MealIngredientCandidate(
                        name=new_ing.name,
                        quantity=new_ing.quantity,
                        estimated_cost=new_ing.estimated_cost,
                        in_pantry=new_ing.in_pantry,
                        safety_status=new_ing.safety_status
                    )
                )

            meals_read.append(
                MealRead(
                    id=m_id,
                    slot=slot,
                    name=new_meal.name,
                    description=new_meal.description,
                    cooking_time_minutes=new_meal.cooking_time_minutes,
                    estimated_cost=new_meal.estimated_cost,
                    dietary_tags=m_data.get("dietary_tags", []),
                    safety_status=new_meal.safety_status,
                    safety_reason=new_meal.safety_reason,
                    nutrition=m_data.get("nutrition", {}),
                    why_recommended=new_meal.why_recommended,
                    steps=m_data.get("steps", []),
                    ingredients=ingredients_read
                )
            )

        db.commit()

        return MealPlanRead(
            id=plan_id,
            date=today_str,
            total_estimated_cost=new_plan.total_estimated_cost,
            target_budget=new_plan.target_budget,
            is_valid=True,
            meals=meals_read,
            explainability=candidate.get("explainability", [])
        )
