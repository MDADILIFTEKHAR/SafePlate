# SafePlate — Open-Source AI & Ollama Integration

SafePlate is built from the ground up to empower users with **open-source, open-weight artificial intelligence**.

---

## 1. Why Open-Source AI for Food Safety?

1. **Medical Privacy**: A person's severe food allergies (like anaphylactic peanut allergies) are sensitive personal health information. Transmitting these profiles over the public internet to commercial AI API providers introduces unacceptable privacy risks.
2. **Local Sovereignty**: SafePlate works fully offline once downloaded. A user in a kitchen with unstable or absent internet can still verify food safety and plan balanced meals.
3. **Transparency & Controllability**: Open weights allow complete auditability and deterministic testing.

---

## 2. The AI Provider Abstraction (`AIProvider`)

The application decouples meal planning logic from any specific AI model through the `AIProvider` abstract base class:

```python
class AIProvider(ABC):
    @abstractmethod
    async def generate_meal_plan_candidate(user_profile, pantry_items, repair_instruction) -> dict: ...
    @abstractmethod
    async def check_availability() -> dict: ...
```

The rest of the system (Allergy Engine, Budget Engine, Pantry Optimizer, Frontend) has zero knowledge of which model is generating candidates.

### Switching Models
You can swap between models simply by setting `MODEL_NAME` in your `.env` file without changing any application code:
```env
# Example with Llama 3.2 3B (Default Recommended)
MODEL_NAME=llama3.2:3b

# Example with Mistral 7B
MODEL_NAME=mistral:7b

# Example with Qwen 2.5 7B
MODEL_NAME=qwen2.5:7b
```

---

## 3. Ollama Setup Guide

1. **Install Ollama**:
   - Download the installer for your OS from [ollama.com](https://ollama.com).
2. **Pull a Model**:
   ```bash
   ollama pull llama3.2:3b
   ```
3. **Verify Ollama is Running**:
   ```bash
   ollama list
   ```
4. **Configure SafePlate**:
   In `.env`:
   ```env
   DEMO_MODE=false
   MODEL_PROVIDER=ollama
   MODEL_NAME=llama3.2:3b
   OLLAMA_BASE_URL=http://localhost:11434
   ```

---

## 4. Deterministic Demo Mode (`DEMO_MODE=true`)

SafePlate includes a production-grade **Deterministic Demo Mode**.
- **Zero Dependencies**: Runs without requiring an Ollama daemon or GPU.
- **Identical Safety Pipeline**: Demo candidates pass through the **EXACT SAME** validation pipeline:
  - Text Normalization
  - Deterministic Allergy Engine
  - Cross-contamination and Trace Warning Detector
  - Vegetarian Diet Validation
  - Deterministic Budget Arithmetic
  - Cooking Time Bounds
  - Final Safety Gate
- **Interactive Testing**: Supports test-hook simulations for budget overruns, unrepairable allergen conflicts, and agent iteration bounds.
