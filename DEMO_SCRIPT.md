# SafePlate — Demonstration & Judging Script 🎙️

Use this script to walk judges or a friend through the SafePlate experience in under 5 minutes.

---

## 🎭 Persona Introduction
- **User**: Aisha
- **Allergies**: Peanut, Tree nuts (Strict medical exclusion)
- **Diet**: Vegetarian
- **Cuisine**: Indian
- **Daily Budget**: ₹150 (Breakfast ~₹35, Lunch ~₹50, Snack ~₹20, Dinner ~₹45)
- **Max Cooking Time**: 30 minutes
- **Available Pantry**: Rice, Dal, Potato, Tomato, Onion, Curd, Spinach

---

## 🎬 Step-by-Step Live Demo

### Step 1: The First Impression (30 seconds)
1. Open the application at `http://localhost:5173`.
2. Point out:
   - Header with active **"Demo Mode"** or **"Ollama"** pill.
   - Persona greeting: *"Good evening, Aisha 👋"*
   - Active protection tag: *Allergies: Peanut, Tree nuts*.
   - **Daily Financial Safety Tracker**: Shows total cost and budget breakdown (e.g., ₹82 / ₹150 used).
   - **Today's 4-Meal Plan**: Breakfast, Lunch, Snack, Dinner.
   - Expand the lunch card (*Dal Tadka with Steamed Rice*) to show how pantry items reduce added cost to ₹0.

---

### Step 2: "Can I Eat This?" — Deterministic Safety Engine (90 seconds)
1. Click the green **`[ Can I Eat This? ]`** CTA button in the hero or navbar.
2. **Action A: Direct Peanut Allergen**
   - Click the test chip `🥜 Peanut butter` (or type it).
   - Click **`Check Safety Now`**.
   - **Result**: Immediate **`AVOID`** badge appears in red!
   - Highlight: *"Direct allergen conflict: Contains 'peanut butter', which violates your declared Peanut allergy."*
   - Point out the **Validated Safe Substitution**: *"sunflower seed butter"*.
3. **Action B: Safe Pantry Food**
   - Click the test chip `🍚 Steamed rice`.
   - Click **`Check Safety Now`**.
   - **Result**: Bright green **`SAFE`** badge appears with 100% confidence.
4. **Action C: Hidden Tree Nut (Cashew)**
   - Click `🌰 Cashew nuts`.
   - Click **`Check Safety Now`**.
   - **Result**: **`AVOID`** badge triggered because Cashew is a tree nut!
5. **Action D: Cross-Contamination & Trace Warning**
   - Click `⚠️ Trace warning` (*"may contain traces of peanuts"*).
   - Click **`Check Safety Now`**.
   - **Result**: **`CAUTION`** badge in amber, flagging shared equipment risk.
6. Close the modal.

---

### Step 3: Pantry Optimization (45 seconds)
1. Click the **`Pantry`** button in the navbar.
2. View Aisha's stock: Rice, Dal, Potato, Tomato, Onion, Curd, Spinach.
3. Type *"Fresh Coriander"*, quantity *"1 bunch"*, category *"Vegetables"*.
4. Click **`Add to Pantry`** $\rightarrow$ Observe instant inventory update.
5. Click **`Build Plan From My Pantry`**. SafePlate re-optimizes the daily plan to use available kitchen stock.

---

### Step 4: The Agent Loop & Safety Gate (60 seconds)
1. Click the **CPU icon** in the navbar to open the **Agent & AI Engine Inspector**.
2. Show judges:
   - The core principle: **AI GENERATES $\rightarrow$ RULE ENGINE VALIDATES $\rightarrow$ APP DECIDES**.
   - The bounded iteration trace (`Iteration 1`, `Iteration 2`).
   - How violations (e.g. over-budget or allergen inclusion) automatically generate targeted repair instructions.
   - How the **Final Safety Gate** guarantees that unvalidated suggestions never reach the user.

---

### Step 5: Profile Invalidation Protection (45 seconds)
1. Click Aisha's profile pill in the top right.
2. In the profile modal, toggle off *Tree nuts* or add *Sesame*.
3. Click **`Save Profile`**.
4. Return to the dashboard:
   - Notice the prominent amber warning banner:
     **`"Safety Invalidation Warning: Your declared profile allergies changed. Previous meal recommendations may no longer be safe."`**
   - Click **`Regenerate Safe Plan`** to see SafePlate immediately rebuild a verified plan matching the new constraints!
