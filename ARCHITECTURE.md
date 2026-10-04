# SafePlate — Technical Architecture & Design Document

## 1. Core Architectural Principle

```
+-------------------------------------------------------------+
| AI GENERATES.   RULE ENGINE VALIDATES.   APPLICATION DECIDES. |
+-------------------------------------------------------------+
```

Under no circumstances is an LLM output trusted as the final authority on food safety. Generative AI models are probabilistic and prone to hallucinations; food allergies can be fatal. SafePlate treats the LLM solely as a candidate generator and relies on a multi-tiered, deterministic, zero-tolerance rule engine to validate, repair, or reject proposals.

---

## 2. End-to-End Pipeline

```
                     USER PROFILE
             [Allergies, Budget, Diet, Pantry]
                           │
                           ▼
                  1. CANDIDATE GENERATION
             (OllamaProvider / DemoProvider)
                           │
                           ▼
                 2. STRUCTURED EXTRACTION
             (Pydantic Schema Validation)
                           │
                           ▼
              3. INGREDIENT NORMALIZATION
         (Lowercase, Punctuation, Alias Expansion)
                           │
                           ▼
               4. ALLERGY KNOWLEDGE ENGINE
       (Direct Allergen Check: SAFE, CAUTION, AVOID, UNKNOWN)
                           │
                           ▼
         5. CROSS-CONTAMINATION & TRACE CHECK
       ("may contain", "shared equipment", facility)
                           │
                           ▼
                  6. DIET VALIDATION
          (Vegetarian, Vegan, Non-Veg, Dislikes)
                           │
                           ▼
                 7. PANTRY OPTIMIZATION
        (Match Pantry Items, Calculate Added Cost)
                           │
                           ▼
                 8. BUDGET VALIDATION
          (Deterministic Sum <= Daily Budget ₹150)
                           │
                           ▼
               9. COOKING TIME VALIDATION
         (Each Meal <= Max Cooking Time 30 mins)
                           │
                           ▼
                10. QUALITY VALIDATION
      (Step counts, Ingredient count, Nutrition tags)
                           │
               ┌───────────┴───────────┐
               ▼                       ▼
          [VIOLATIONS?]           [ALL CLEAR]
               │                       │
               ▼                       ▼
       11. REPAIR SYNTHESIS      12. FINAL SAFETY GATE
     (Synthesize violations &        (Invariant Audit)
      pass to next iteration)          │
               │                       ▼
               ▼                  RETURN PLAN
       Iteration <= MAX (3)
       (Else Failure Action)
```

---

## 3. The Bounded Agent Loop

The agent loop operates with an explicit bound (`MAX_ITERATIONS = 3`).

### Iteration State Structure:
```json
{
  "iteration": 1,
  "candidate_summary": "4-meal plan candidate",
  "violations": [
    "Dinner contains unsafe ingredient: roasted peanut paste",
    "Total plan cost ₹175 exceeds daily budget of ₹150 by ₹25"
  ],
  "repair_instruction": "Previous plan had violations:\n- Remove peanut\n- Lower cost to ₹150",
  "status": "violates_constraints",
  "duration_ms": 124.5
}
```

If iteration count reaches `MAX_ITERATIONS` without meeting all constraints:
1. The system **never fabricates success**.
2. It returns status `FAILED_MAX_ITERATIONS`.
3. It exposes structured alternative actions:
   - `Relax Budget`
   - `Increase Cooking Time`
   - `Use Pantry`
   - `Try Again`

---

## 4. Deterministic Allergy Knowledge Engine

The allergy engine operates on normalized taxonomy:
- **Taxonomy Source**: `data/allergens.json`
- **Aliases Source**: `data/ingredient_aliases.json`
- **Normalization**:
  - Lowercase transformation
  - Compound hyphen resolution (`pea-nut` $\rightarrow$ `peanut`)
  - Boundary-aware regex patterns (`\bpeanut\b` to avoid substring collision)
  - Synonyms resolution (`groundnut` $\rightarrow$ `peanut`, `kaju` $\rightarrow$ `cashew`, `badam` $\rightarrow$ `almond`)

### Priority Decision Matrix:
| Trigger Condition | Result State | Explanation |
| :--- | :--- | :--- |
| Contains declared allergen keyword or alias | **`AVOID`** | Direct medical danger. Strictly prohibited. |
| Contains shared facility / trace advisory | **`CAUTION`** | Cross-contamination hazard. Requires consumer alert. |
| Contains unverified, cryptic, or unlabeled code | **`UNKNOWN`** | Insufficient data to verify safety. Never assume safe. |
| Zero allergen matches & clean food components | **`SAFE`** | Passed all deterministic verification rules. |

---

## 5. Smart Substitution Loop

When an ingredient violates an allergy (e.g., peanut butter in a snack recipe):
1. The **Substitution Engine** queries culinary alternative candidates from `data/substitutions.json`.
2. Candidate 1 (e.g. *sunflower seed butter*) is routed through:
   - Deterministic allergy validation
   - Diet validation (e.g. Vegetarian)
3. If safe, it is accepted and assigned a cost multiplier.
4. If candidate 1 has a conflict, candidate 2 (e.g. *tahini*) is evaluated.
5. Bound: Maximum 3 substitution attempts.
6. **Invariant**: An unvalidated substitution can **NEVER** become final.

---

## 6. Database Schema (SQLite & SQLAlchemy 2.0)

- **`user_profiles`**: Id, Name, Daily Budget, Max Cooking Time, Spice Level, Cuisines, Dislikes.
- **`allergies`**: Id, User ID (FK), Name, Allergen Code, Severity.
- **`dietary_preferences`**: Id, User ID (FK), Preference Type (`Vegetarian`, `Vegan`, `Non-Vegetarian`).
- **`pantry_items`**: Id, User ID (FK), Name, Quantity, Category, Added At.
- **`meal_plans`**: Id, User ID (FK), Date, Total Cost, Target Budget, Is Valid (`BOOLEAN`).
- **`meals`**: Id, Meal Plan ID (FK), Slot (`breakfast`, `lunch`, `snack`, `dinner`), Name, Description, Cooking Time, Cost, Dietary Tags, Safety Status, Nutrition, Steps.
- **`meal_ingredients`**: Id, Meal ID (FK), Name, Quantity, Estimated Cost, In Pantry (`BOOLEAN`), Safety Status.
- **`safety_checks`**: Id, Query Text, Normalized Terms, Safety Status, Reason, Matched Allergens, Confidence, Timestamp.
- **`agent_runs`**: Id, User ID, Prompt Type, Iteration Count, Final Status, Violations, Repair Actions, Execution Time (ms), Steps Data.

---

## 7. AI Provider Architecture

SafePlate defines an abstract interface `AIProvider`:
```python
class AIProvider(ABC):
    @abstractmethod
    async def generate_meal_plan_candidate(user_profile, pantry_items, repair_instruction) -> dict: ...
    @abstractmethod
    async def check_availability() -> dict: ...
```

Implementations:
1. **`OllamaProvider`**: Communicates with local open-weight models over HTTP (`localhost:11434`). Enforces JSON mode, connection timeouts, and 3-stage failure recovery (Attempt 1: structured parse, Attempt 2: correction prompt, Attempt 3: fallback generator).
2. **`DemoProvider`**: High-fidelity deterministic provider that generates realistic Indian and international recipes from verified seed profiles, perfectly demonstrating repair loops and invariant checks without requiring an external daemon.
