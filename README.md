# SafePlate 🛡️🍽️

> **"AI meal planning built around what YOU can safely eat."**

SafePlate is a local-first, privacy-respecting, allergy-safe meal planning application and food safety checker. It is built for anyone managing serious food allergies (such as peanuts or tree nuts), strict dietary preferences (like vegetarianism), daily financial constraints (e.g. ₹150/day), and busy schedules (under 30 minutes cooking time).

Unlike generic chatbots or thin AI wrappers, SafePlate enforces a strict non-negotiable architectural invariant:
**AI GENERATES. RULE ENGINE VALIDATES. APPLICATION DECIDES.**

---

## 🌟 Key Features

1. **Deterministic Food Safety Knowledge Engine**:
   - Classifies every food item into **`SAFE`**, **`CAUTION`**, **`AVOID`**, or **`UNKNOWN`**.
   - Handles allergen synonyms, culinary terms (e.g., groundnut vs peanut, badam vs almond, dahi vs curd).
   - Normalizes text, stripping punctuation, hyphens, and whitespace variations.
   - Detects cross-contamination and shared manufacturing facility warnings (*"may contain traces of peanuts"* $\rightarrow$ **`CAUTION`**).
   - Unknown and unverified packaged additives trigger **`UNKNOWN`**, never hallucinated as safe.

2. **"Can I Eat This?" Instant Safety Validator**:
   - Check raw ingredients, dish names, or paste packaged grocery product labels.
   - Immediate deterministic verdict with clear rationale, matched terms, user allergy comparison, and healthcare guidance disclaimer.
   - Provides validated safe substitutions on direct allergen conflicts.

3. **Smart Ingredient Substitution Loop**:
   - When an unsafe ingredient is identified (e.g. peanut butter), automatically attempts up to 3 culinary substitutes (e.g. sunflower seed butter).
   - Strict validation gate: an unvalidated substitution can **NEVER** become final.

4. **Pantry-Aware Budget Optimization**:
   - Automatically prioritizes what is already in your kitchen (Rice, Dal, Potato, Tomato, Onion, Curd, Spinach).
   - Ingredients in your pantry count as ₹0 added grocery expense for today's plan.
   - Deterministic budget validation guarantees the total cost never exceeds your daily budget (e.g. ₹150).

5. **Bounded Agentic Repair Loop**:
   - Multi-layer constraint checking: Normalization $\rightarrow$ Allergy Engine $\rightarrow$ Contamination Warnings $\rightarrow$ Diet Validation $\rightarrow$ Budget Validation $\rightarrow$ Cooking-time Validation $\rightarrow$ Quality Gate.
   - Bounded to `MAX_ITERATIONS = 3`. If constraints cannot be met, provides honest, actionable recovery options (Relax Budget, Increase Time, Use Pantry).
   - Never hallucinates success or bypasses safety validation.

6. **Local-First & Open-Source AI**:
   - Powered by **Ollama** running open-weight models (such as Llama 3.2, Mistral, Qwen).
   - Your medical allergy profile and pantry inventory never leave your machine.
   - Built-in zero-dependency **Deterministic Demo Mode** for offline demonstrations, judge reviews, or environments without Ollama.

7. **Automatic Allergy Invalidation**:
   - Editing allergies immediately invalidates previous meal plans so obsolete recommendations are never consumed.

---

## 🏗️ Architecture

```
User / Browser (React 19 + Tailwind CSS + Framer Motion)
                      ↓  ↑
        FastAPI Local REST API (Python 3.13)
                      ↓  ↑
           SQLite Database (SQLAlchemy 2.0)
                      ↓  ↑
       Deterministic Safety & Validation Pipeline
  [Allergy Engine] [Diet Validator] [Budget & Pantry Engine]
                      ↓  ↑
          Bounded Agent Repair Loop (Max 3)
                      ↓  ↑
   AI Provider Abstraction (OllamaProvider / DemoProvider)
                      ↓  ↑
      Local Open-Weight Model (http://localhost:11434)
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.11+ (tested on Python 3.13)
- **Node.js**: 18+ (tested on Node v22.19)
- **Git**
- *(Optional)* **Ollama**: For live open-weight LLM generation. (Demo mode works out of the box without Ollama).

---

### 1. Installation

Clone or open the repository:
```bash
git clone <repo-url>
cd Roommate
```

Set up the Python backend:
```bash
# Windows PowerShell:
python -m venv .venv
.\.venv\Scripts\pip install -r backend/requirements.txt

# macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

Set up the React frontend:
```bash
cd frontend
npm install
cd ..
```

---

### 2. Configuration (`.env`)

Copy the template configuration:
```bash
cp .env.example .env
```
Default configuration values:
- `DEMO_MODE=true` (Runs high-fidelity deterministic AI simulation without Ollama)
- `MODEL_PROVIDER=ollama`
- `MODEL_NAME=llama3.2:3b`
- `OLLAMA_BASE_URL=http://localhost:11434`
- `DATABASE_URL=sqlite:///./safeplate.db`
- `MAX_AGENT_ITERATIONS=3`

---

### 3. Running Locally

#### Terminal 1: Backend API
```bash
# Windows PowerShell:
$env:PYTHONPATH='backend'
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# macOS/Linux:
PYTHONPATH=backend .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### Terminal 2: Frontend Client
```bash
cd frontend
npm run dev
```
Open your browser at: [http://localhost:5173/](http://localhost:5173/)

---

### 4. Running With Ollama (Live Open-Weight Model)

1. Ensure Ollama is installed from [ollama.com](https://ollama.com).
2. Pull your chosen model:
   ```bash
   ollama pull llama3.2:3b
   ```
3. Start the Ollama daemon:
   ```bash
   ollama serve
   ```
4. In `.env`, set:
   ```env
   DEMO_MODE=false
   MODEL_PROVIDER=ollama
   MODEL_NAME=llama3.2:3b
   ```
5. Restart the backend. The UI badge will automatically display **"Ollama (llama3.2:3b)"**.

---

## 🧪 Testing Strategy

SafePlate includes complete multi-tier test suites:
- **Unit Tests**: Allergy engine, normalization, budget calculation, cooking time, substitutions.
- **Invariant Tests**: Property-based tests enforcing safety guarantees.
- **Integration Tests**: API endpoints, concurrency locks, database persistence, invalidation.
- **Frontend Tests**: Component rendering, modal state, accessibility.
- **End-to-End Tests**: Playwright browser flow testing the complete user journey.

### Run Backend Unit & Integration Tests (Pytest)
```bash
# Windows:
$env:PYTHONPATH='backend'
.\.venv\Scripts\pytest backend/tests -v

# macOS/Linux:
PYTHONPATH=backend .venv/bin/pytest backend/tests -v
```

### Run Frontend Unit Tests (Vitest)
```bash
cd frontend
npm run test
```

### Run Playwright E2E Tests
```bash
npx playwright test
```

---

## 🛡️ Medical & Safety Disclaimer
*SafePlate is an informational food-safety and AI meal planning assistant. It is not a medical device. Always inspect physical product packaging, verify ingredient labels, and consult with a qualified allergist or medical healthcare professional before consuming any food.*
