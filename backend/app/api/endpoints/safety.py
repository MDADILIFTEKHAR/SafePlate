from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import UserProfile, SafetyCheck
from app.schemas.api_models import (
    SafetyCheckRequest, SafetyCheckResponse,
    SubstitutionRequest, SubstitutionResponse, SubstitutionOption
)
from app.services.safety.allergy_engine import allergy_engine
from app.services.meal.substitution_engine import substitution_engine
import uuid
import json

router = APIRouter(tags=["Safety"])

@router.post("/safety/check", response_model=SafetyCheckResponse)
def check_food_safety(payload: SafetyCheckRequest, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    user_allergies = [a.name for a in profile.allergies] if profile else ["Peanut", "Tree nuts"]
    
    # Run deterministic allergy engine
    result = allergy_engine.match_allergens_in_text(payload.query, user_allergies)
    
    # Check for suggested substitutions if unsafe
    suggested = []
    if result["status"] in ["AVOID", "CAUTION"]:
        diet = profile.dietary_preferences[0].preference_type if (profile and profile.dietary_preferences) else "Vegetarian"
        disliked = profile.get_disliked_list() if profile else []
        for term in result.get("matched_terms", [payload.query]):
            sub, _ = substitution_engine.find_safe_substitution(
                term, user_allergies, diet, disliked
            )
            if sub and sub.get("substitute"):
                suggested.append(f"{sub['substitute']} (safe alternative)")

    # Record check in database for auditing
    try:
        record = SafetyCheck(
            id=f"chk-{uuid.uuid4().hex[:12]}",
            query_text=payload.query,
            normalized_terms=json.dumps(result.get("matched_terms", [])),
            safety_status=result["status"],
            reason=result["reason"],
            matched_allergens=json.dumps(result.get("matched_allergens", [])),
            confidence=result.get("confidence", "high")
        )
        db.add(record)
        db.commit()
    except Exception as e:
        print(f"Error persisting safety check: {e}")

    return SafetyCheckResponse(
        status=result["status"],
        reason=result["reason"],
        matched_terms=result.get("matched_terms", []),
        matched_allergens=result.get("matched_allergens", []),
        user_allergies_checked=user_allergies,
        confidence=result.get("confidence", "high"),
        suggested_substitutions=list(dict.fromkeys(suggested))
    )

@router.post("/meal/substitute", response_model=SubstitutionResponse)
def find_substitutions(payload: SubstitutionRequest, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    user_allergies = [a.name for a in profile.allergies] if profile else ["Peanut", "Tree nuts"]
    diet = profile.dietary_preferences[0].preference_type if (profile and profile.dietary_preferences) else "Vegetarian"
    disliked = profile.get_disliked_list() if profile else []

    accepted, history = substitution_engine.find_safe_substitution(
        unsafe_ingredient=payload.ingredient,
        user_allergies=user_allergies,
        diet_preference=diet,
        disliked_ingredients=disliked,
        max_attempts=3
    )

    options = []
    for h in history:
        options.append(
            SubstitutionOption(
                substitute=h["substitute"],
                flavor_profile=h["flavor_profile"],
                is_safe=h["is_safe"],
                safety_reason=h["reason"],
                estimated_cost_multiplier=h["cost_multiplier"]
            )
        )

    return SubstitutionResponse(
        original_ingredient=payload.ingredient,
        substitutions=options
    )
