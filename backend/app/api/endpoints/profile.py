import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import UserProfile, Allergy, DietaryPreference, PantryItem, MealPlan
from app.schemas.api_models import ProfileRead, ProfileUpdate, PantryItemRead

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("", response_model=ProfileRead)
def get_user_profile(db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please initialize the application database."
        )

    allergies = [a.name for a in profile.allergies]
    diet = profile.dietary_preferences[0].preference_type if profile.dietary_preferences else "Vegetarian"
    pantry = [
        PantryItemRead(
            id=p.id,
            name=p.name,
            quantity=p.quantity,
            category=p.category,
            added_at=p.added_at
        ) for p in profile.pantry_items
    ]

    return ProfileRead(
        id=profile.id,
        name=profile.name,
        daily_budget=profile.daily_budget,
        max_cooking_time_minutes=profile.max_cooking_time_minutes,
        spice_level=profile.spice_level,
        cuisines=profile.get_cuisines_list(),
        allergies=allergies,
        dietary_preference=diet,
        disliked_ingredients=profile.get_disliked_list(),
        pantry=pantry
    )

@router.put("", response_model=ProfileRead)
def update_user_profile(update_data: ProfileUpdate, db: Session = Depends(get_db)):
    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found to update."
        )

    # Track if allergies changed to trigger meal plan invalidation
    old_allergies = set(a.name.strip().lower() for a in profile.allergies)
    new_allergies = set(a.strip().lower() for a in update_data.allergies)
    allergies_changed = old_allergies != new_allergies

    try:
        # Update scalar fields
        profile.name = update_data.name.strip()
        profile.daily_budget = float(update_data.daily_budget)
        profile.max_cooking_time_minutes = int(update_data.max_cooking_time_minutes)
        profile.spice_level = update_data.spice_level
        profile.cuisines = json.dumps(update_data.cuisines)
        profile.disliked_ingredients = json.dumps(update_data.disliked_ingredients)

        # Update dietary preference
        if profile.dietary_preferences:
            profile.dietary_preferences[0].preference_type = update_data.dietary_preference
        else:
            db.add(DietaryPreference(user_id=profile.id, preference_type=update_data.dietary_preference))

        # Update allergies
        db.query(Allergy).filter(Allergy.user_id == profile.id).delete()
        for a_name in update_data.allergies:
            code = a_name.strip().upper().replace(" ", "_")
            db.add(Allergy(user_id=profile.id, name=a_name.strip(), allergen_code=code, severity="severe"))

        # If allergies changed, invalidate existing meal plans
        if allergies_changed:
            db.query(MealPlan).filter(MealPlan.user_id == profile.id).update({"is_valid": False})

        db.commit()
        db.refresh(profile)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not update profile. Please verify your submitted fields."
        )

    allergies = [a.name for a in profile.allergies]
    diet = profile.dietary_preferences[0].preference_type if profile.dietary_preferences else "Vegetarian"
    pantry = [
        PantryItemRead(
            id=p.id,
            name=p.name,
            quantity=p.quantity,
            category=p.category,
            added_at=p.added_at
        ) for p in profile.pantry_items
    ]

    return ProfileRead(
        id=profile.id,
        name=profile.name,
        daily_budget=profile.daily_budget,
        max_cooking_time_minutes=profile.max_cooking_time_minutes,
        spice_level=profile.spice_level,
        cuisines=profile.get_cuisines_list(),
        allergies=allergies,
        dietary_preference=diet,
        disliked_ingredients=profile.get_disliked_list(),
        pantry=pantry
    )
