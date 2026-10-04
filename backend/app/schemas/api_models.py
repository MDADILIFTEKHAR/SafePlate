from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime

# --- ALLERGY & DIET SCHEMAS ---
class AllergyItem(BaseModel):
    name: str = Field(..., min_length=1, description="Allergy name, e.g. Peanut")
    severity: str = Field(default="severe", description="mild, moderate, or severe")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Allergy name cannot be empty")
        return v

class AllergyRead(AllergyItem):
    id: int
    allergen_code: str

# --- PANTRY SCHEMAS ---
class PantryItemCreate(BaseModel):
    name: str = Field(..., min_length=1)
    quantity: str = Field(default="1 unit")
    category: str = Field(default="General")

    @field_validator("name")
    @classmethod
    def validate_pantry_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Pantry item name cannot be empty")
        return v

class PantryItemRead(PantryItemCreate):
    id: int
    added_at: Optional[datetime] = None

# --- PROFILE SCHEMAS ---
class ProfileUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    daily_budget: float = Field(..., gt=0, description="Daily budget must be greater than zero")
    max_cooking_time_minutes: int = Field(..., gt=0, description="Cooking time must be greater than zero")
    spice_level: str = Field(default="Low/medium")
    cuisines: List[str] = Field(default_factory=lambda: ["Indian"])
    allergies: List[str] = Field(default_factory=list)
    dietary_preference: str = Field(default="Vegetarian")
    disliked_ingredients: List[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("allergies")
    @classmethod
    def clean_allergies(cls, v: List[str]) -> List[str]:
        # Normalize and remove empty or duplicate allergies
        cleaned = []
        seen = set()
        for item in v:
            item_clean = item.strip()
            if item_clean and item_clean.lower() not in seen:
                seen.add(item_clean.lower())
                cleaned.append(item_clean)
        return cleaned

class ProfileRead(BaseModel):
    id: int
    name: str
    daily_budget: float
    max_cooking_time_minutes: int
    spice_level: str
    cuisines: List[str]
    allergies: List[str]
    dietary_preference: str
    disliked_ingredients: List[str]
    pantry: List[PantryItemRead]

# --- SAFETY ENGINE SCHEMAS ---
class SafetyCheckRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Food name, ingredient, ingredient list, or label text")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Query cannot be blank")
        return v

class SafetyCheckResponse(BaseModel):
    status: str = Field(..., description="SAFE, CAUTION, AVOID, UNKNOWN")
    reason: str
    matched_terms: List[str] = Field(default_factory=list)
    matched_allergens: List[str] = Field(default_factory=list)
    user_allergies_checked: List[str] = Field(default_factory=list)
    confidence: str = Field(default="high")
    suggested_substitutions: List[str] = Field(default_factory=list)
    notice: str = "This is an informational food-safety assistant. Always verify product labels and follow guidance from your healthcare professional."

# --- MEAL INGREDIENT & RECIPE SCHEMAS ---
class MealIngredientCandidate(BaseModel):
    name: str = Field(..., min_length=1)
    quantity: str = Field(default="1 serving")
    estimated_cost: float = Field(default=0.0, ge=0)
    in_pantry: bool = Field(default=False)
    safety_status: str = Field(default="SAFE")

class MealCandidate(BaseModel):
    name: str = Field(..., min_length=1)
    slot: str = Field(default="lunch")
    description: str = Field(default="")
    ingredients: List[MealIngredientCandidate] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    cooking_time_minutes: int = Field(default=20, ge=1)
    estimated_cost: float = Field(default=0.0, ge=0)
    dietary_tags: List[str] = Field(default_factory=list)
    why_recommended: str = Field(default="")
    safety_status: str = Field(default="SAFE")
    safety_reason: str = Field(default="")
    nutrition: Dict[str, Any] = Field(default_factory=dict)

class MealPlanCandidate(BaseModel):
    breakfast: MealCandidate
    lunch: MealCandidate
    snack: MealCandidate
    dinner: MealCandidate
    total_cost: float = Field(default=0.0, ge=0)
    summary: str = Field(default="")

class MealRead(BaseModel):
    id: str
    slot: str
    name: str
    description: str
    cooking_time_minutes: int
    estimated_cost: float
    dietary_tags: List[str]
    safety_status: str
    safety_reason: str
    nutrition: Dict[str, Any]
    why_recommended: str
    steps: List[str]
    ingredients: List[MealIngredientCandidate]

class MealPlanRead(BaseModel):
    id: str
    date: str
    total_estimated_cost: float
    target_budget: float
    is_valid: bool
    meals: List[MealRead]
    explainability: List[str] = Field(default_factory=list)

# --- AGENT SCHEMAS ---
class AgentStepRecord(BaseModel):
    iteration: int
    candidate_summary: str
    violations: List[str]
    repair_instruction: Optional[str] = None
    status: str
    timestamp: str

class AgentRunRecord(BaseModel):
    id: str
    prompt_type: str
    iteration_count: int
    final_status: str
    violations: List[str]
    repair_actions: List[str]
    execution_time_ms: float
    steps_data: List[AgentStepRecord] = Field(default_factory=list)
    created_at: datetime

class MealGenerateRequest(BaseModel):
    force_pantry: bool = False
    requested_slot: Optional[str] = None  # None for full day 4-meal plan

class SubstitutionRequest(BaseModel):
    ingredient: str = Field(..., min_length=1)
    recipe_context: Optional[str] = ""

class SubstitutionOption(BaseModel):
    substitute: str
    flavor_profile: str
    is_safe: bool
    safety_reason: str
    estimated_cost_multiplier: float

class SubstitutionResponse(BaseModel):
    original_ingredient: str
    substitutions: List[SubstitutionOption]
    notice: str = "Always verify product labels for cross-contamination."
