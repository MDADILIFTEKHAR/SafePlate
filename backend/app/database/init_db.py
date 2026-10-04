import json
from sqlalchemy.orm import Session
from app.database.session import Base, engine, SessionLocal
from app.models.entities import UserProfile, Allergy, DietaryPreference, PantryItem

def init_db(db: Session = None):
    """
    Idempotent database initialization:
    - Creates tables if they don't exist
    - Seeds default profile for Aisha if not already present
    - Does NOT duplicate records if run multiple times
    """
    Base.metadata.create_all(bind=engine)
    
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        existing_profile = db.query(UserProfile).first()
        if not existing_profile:
            # Seed Aisha's profile
            aisha = UserProfile(
                name="Aisha",
                daily_budget=150.0,
                max_cooking_time_minutes=30,
                spice_level="Low/medium",
                cuisines=json.dumps(["Indian"]),
                disliked_ingredients=json.dumps([])
            )
            db.add(aisha)
            db.flush()

            # Seed Allergies
            db.add(Allergy(user_id=aisha.id, name="Peanut", allergen_code="PEANUT", severity="severe"))
            db.add(Allergy(user_id=aisha.id, name="Tree nuts", allergen_code="TREE_NUT", severity="severe"))

            # Seed Dietary Preference
            db.add(DietaryPreference(user_id=aisha.id, preference_type="Vegetarian"))

            # Seed Pantry Items
            pantry_items = [
                ("Rice", "1 kg", "Grains"),
                ("Dal", "500 g", "Legumes"),
                ("Potato", "4 medium", "Vegetables"),
                ("Tomato", "3 medium", "Vegetables"),
                ("Onion", "2 medium", "Vegetables"),
                ("Curd", "500 g", "Dairy"),
                ("Spinach", "1 bunch", "Vegetables")
            ]
            for name, qty, cat in pantry_items:
                db.add(PantryItem(user_id=aisha.id, name=name, quantity=qty, category=cat))

            db.commit()
            print("Database initialized and Aisha persona seeded successfully.")
        else:
            print("Database already contains user profile. Skipping seed.")
    finally:
        if close_session:
            db.close()

if __name__ == "__main__":
    init_db()
