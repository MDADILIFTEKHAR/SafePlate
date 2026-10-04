import json
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.session import Base

def utc_now():
    return datetime.now(timezone.utc)

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    daily_budget = Column(Float, nullable=False, default=150.0)
    max_cooking_time_minutes = Column(Integer, nullable=False, default=30)
    spice_level = Column(String(50), default="Low/medium")
    cuisines = Column(Text, default="[\"Indian\"]")  # JSON encoded list
    disliked_ingredients = Column(Text, default="[]")  # JSON encoded list
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    allergies = relationship("Allergy", back_populates="user", cascade="all, delete-orphan")
    dietary_preferences = relationship("DietaryPreference", back_populates="user", cascade="all, delete-orphan")
    pantry_items = relationship("PantryItem", back_populates="user", cascade="all, delete-orphan")
    meal_plans = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")

    def get_cuisines_list(self) -> list[str]:
        try:
            return json.loads(self.cuisines)
        except Exception:
            return ["Indian"]

    def get_disliked_list(self) -> list[str]:
        try:
            return json.loads(self.disliked_ingredients)
        except Exception:
            return []


class Allergy(Base):
    __tablename__ = "allergies"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    allergen_code = Column(String(50), nullable=False)
    severity = Column(String(50), default="severe")

    user = relationship("UserProfile", back_populates="allergies")


class DietaryPreference(Base):
    __tablename__ = "dietary_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    preference_type = Column(String(50), nullable=False, default="Vegetarian")

    user = relationship("UserProfile", back_populates="dietary_preferences")


class PantryItem(Base):
    __tablename__ = "pantry_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    quantity = Column(String(100), default="1 unit")
    category = Column(String(50), default="General")
    added_at = Column(DateTime, default=utc_now)

    user = relationship("UserProfile", back_populates="pantry_items")


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    date = Column(String(20), nullable=False)
    total_estimated_cost = Column(Float, nullable=False, default=0.0)
    target_budget = Column(Float, nullable=False, default=150.0)
    is_valid = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

    user = relationship("UserProfile", back_populates="meal_plans")
    meals = relationship("Meal", back_populates="meal_plan", cascade="all, delete-orphan")


class Meal(Base):
    __tablename__ = "meals"

    id = Column(String(64), primary_key=True, index=True)
    meal_plan_id = Column(String(64), ForeignKey("meal_plans.id", ondelete="CASCADE"), nullable=False)
    slot = Column(String(30), nullable=False)  # breakfast, lunch, snack, dinner
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    cooking_time_minutes = Column(Integer, nullable=False, default=20)
    estimated_cost = Column(Float, nullable=False, default=0.0)
    dietary_tags = Column(Text, default="[]")  # JSON list
    safety_status = Column(String(30), default="SAFE")  # SAFE, CAUTION, AVOID, UNKNOWN
    safety_reason = Column(Text, default="")
    nutrition = Column(Text, default="{}")  # JSON object
    why_recommended = Column(Text, default="")
    steps = Column(Text, default="[]")  # JSON list

    meal_plan = relationship("MealPlan", back_populates="meals")
    ingredients = relationship("MealIngredient", back_populates="meal", cascade="all, delete-orphan")

    def get_dietary_tags(self) -> list[str]:
        try:
            return json.loads(self.dietary_tags)
        except Exception:
            return []

    def get_nutrition_dict(self) -> dict:
        try:
            return json.loads(self.nutrition)
        except Exception:
            return {}

    def get_steps_list(self) -> list[str]:
        try:
            return json.loads(self.steps)
        except Exception:
            return []


class MealIngredient(Base):
    __tablename__ = "meal_ingredients"

    id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(String(64), ForeignKey("meals.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    quantity = Column(String(50), default="1 serving")
    estimated_cost = Column(Float, default=0.0)
    in_pantry = Column(Boolean, default=False)
    safety_status = Column(String(30), default="SAFE")

    meal = relationship("Meal", back_populates="ingredients")


class SafetyCheck(Base):
    __tablename__ = "safety_checks"

    id = Column(String(64), primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    normalized_terms = Column(Text, default="[]")
    safety_status = Column(String(30), nullable=False)  # SAFE, CAUTION, AVOID, UNKNOWN
    reason = Column(Text, nullable=False)
    matched_allergens = Column(Text, default="[]")  # JSON list
    confidence = Column(String(30), default="high")
    created_at = Column(DateTime, default=utc_now)


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    prompt_type = Column(String(50), default="meal_plan_generation")
    iteration_count = Column(Integer, default=1)
    final_status = Column(String(50), default="SUCCESS")  # SUCCESS, REPAIRED, FAILED_MAX_ITERATIONS
    violations = Column(Text, default="[]")  # JSON list
    repair_actions = Column(Text, default="[]")  # JSON list
    execution_time_ms = Column(Float, default=0.0)
    steps_data = Column(Text, default="[]")  # JSON list of iteration details
    created_at = Column(DateTime, default=utc_now)

    def get_violations(self) -> list:
        try:
            return json.loads(self.violations)
        except Exception:
            return []

    def get_repair_actions(self) -> list:
        try:
            return json.loads(self.repair_actions)
        except Exception:
            return []

    def get_steps_data(self) -> list:
        try:
            return json.loads(self.steps_data)
        except Exception:
            return []
