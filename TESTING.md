# SafePlate — Testing Strategy & Verification Report

SafePlate enforces a comprehensive testing regime consisting of **Unit Tests**, **Property-Style Invariant Tests**, **Integration Tests**, **Frontend Component Tests**, and **End-to-End Browser Automation Tests**.

---

## 1. Test Summary

| Test Suite | Framework | Target / Focus | Status |
| :--- | :--- | :--- | :--- |
| **Allergy Engine** | Pytest | Exact keywords, synonyms, compound words, cross-contamination, unknown indicators | **26 PASSED** |
| **Invariants** | Pytest | Direct allergen exclusion, mathematical budget sum, substitution safety, loop bounds | **PASSED** |
| **Budget & Time** | Pytest | Deterministic arithmetic, pantry cost reduction, time validation limits | **PASSED** |
| **Substitutions** | Pytest | Multi-attempt substitution loop, allergen rejection, bounded attempts | **PASSED** |
| **API Endpoints** | Pytest + Starlette TestClient | `/health`, `/profile`, `/pantry`, `/meal-plan`, `/safety/check`, invalidation | **PASSED** |
| **Frontend Components** | Vitest + React Testing Library | `SafetyBadge`, `BudgetTracker`, `MealCard`, expandability, accessibility | **8 PASSED** |
| **End-to-End Acceptance** | Playwright (Chromium) | Complete user journey: Aisha persona, 4 meals, Can I Eat, Pantry add, invalidation | **1 PASSED (100%)** |
| **Visual QA Verification** | Browser Subagent | Real DOM inspection, click interactions, modal lifecycle, responsive layout | **VERIFIED** |

---

## 2. Invariant Property Verification

The following formal invariants are verified programmatically on every test run:

1. **Safety Invariant 1**: If a meal contains a declared direct allergen (e.g. peanut or tree nuts for Aisha), the final status **MUST NOT** be `SAFE`.
2. **Safety Invariant 2**: If the final safety status is `SAFE`, **NO** deterministic allergy conflict can exist.
3. **Loop Bound Invariant**: The agent repair loop **MUST NEVER** exceed `MAX_ITERATIONS` (3).
4. **Budget Arithmetic Invariant**: The reported total cost **MUST EQUAL** the deterministic sum of individual meal expenses.
5. **Substitution Invariant**: An unvalidated substitution can **NEVER** become final.
6. **LLM Gate Invariant**: Generative model output **CANNOT** bypass the final safety validation gate.

---

## 3. How to Run All Test Suites

### Backend Unit, Invariant, and Integration Tests
```bash
# Windows PowerShell:
$env:PYTHONPATH='backend'
.\.venv\Scripts\pytest backend/tests -v

# macOS/Linux:
PYTHONPATH=backend .venv/bin/pytest backend/tests -v
```

### Frontend Component Tests
```bash
cd frontend
npm run test
```

### End-to-End Playwright Tests
Ensure the backend and frontend are ready or allow Playwright's `webServer` to launch them automatically:
```bash
npx playwright test
```

---

## 4. Failure Injection Scenarios Tested

- **Ollama Offline**: System gracefully falls back to deterministic local mode without crashing.
- **Malformed LLM Output**: Automatic recovery through correction prompt and deterministic fallback.
- **Unrepairable Conflict**: Agent executes bounded iterations and halts at `MAX_ITERATIONS = 3`, offering actionable recovery alternatives.
- **Profile Invalidation**: When user changes declared allergies, previously active meal plans are instantly flagged as invalid (`is_valid: false`).
- **Concurrent Generation Protection**: Mutex prevents race conditions and duplicate generation requests if user repeatedly clicks "Generate".
