import React from 'react';
import { Sparkles, Search, Package, RefreshCw, AlertTriangle, CheckCircle2, ShieldCheck } from 'lucide-react';
import BudgetTracker from '../components/BudgetTracker';
import MealCard from '../components/MealCard';

export default function HomePage({
  profile,
  mealPlan,
  loadingPlan,
  error,
  onGeneratePlan,
  onOpenCanIEat,
  onOpenPantry,
  onOpenProfile,
  onOpenAgentInspector
}) {
  const userName = profile?.name || 'Aisha';
  const targetBudget = profile?.daily_budget || 150;
  const currentCost = mealPlan?.total_estimated_cost || 0;
  const meals = mealPlan?.meals || [];
  const isPlanValid = mealPlan?.is_valid !== false;

  // Determine time of day greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="space-y-8 animate-fade-in pb-16">
      {/* Top Hero Section */}
      <section className="bg-gradient-to-b from-white to-slate-50/50 rounded-3xl border border-slate-200/80 p-6 sm:p-8 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-brand-700 bg-brand-50 px-3 py-1 rounded-full border border-brand-200/60 inline-flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-brand-600" />
                <span>Allergy-Protected Daily Plan</span>
              </span>
              {profile?.allergies && profile.allergies.length > 0 && (
                <span className="text-xs text-rose-700 bg-rose-50 px-2.5 py-1 rounded-full border border-rose-200 font-medium">
                  Allergies: {profile.allergies.join(', ')}
                </span>
              )}
            </div>

            <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
              {getGreeting()}, {userName} 👋
            </h1>
            <p className="text-sm text-slate-600 max-w-xl leading-relaxed">
              SafePlate verified your meals against active allergens, dietary rules, and your ₹{targetBudget} daily budget.
            </p>
          </div>

          {/* Primary Action Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            <button
              id="hero-can-i-eat-btn"
              onClick={onOpenCanIEat}
              className="px-5 py-3 rounded-2xl bg-emerald-600 hover:bg-emerald-700 active:scale-98 text-white font-semibold text-sm shadow-sm shadow-emerald-600/25 transition-all flex items-center gap-2"
            >
              <Search className="w-4 h-4" />
              <span>Can I Eat This?</span>
            </button>

            <button
              id="hero-pantry-btn"
              onClick={onOpenPantry}
              className="px-4 py-3 rounded-2xl bg-white hover:bg-slate-50 active:scale-98 text-slate-800 border border-slate-300 font-semibold text-sm shadow-xs transition-all flex items-center gap-2"
            >
              <Package className="w-4 h-4 text-slate-600" />
              <span>Build From My Pantry</span>
            </button>

            <button
              id="hero-generate-btn"
              onClick={onGeneratePlan}
              disabled={loadingPlan}
              className="px-4 py-3 rounded-2xl bg-brand-700 hover:bg-brand-800 disabled:opacity-50 text-white font-semibold text-sm shadow-sm shadow-brand-700/25 transition-all flex items-center gap-2"
              title="Generate a fresh safe meal plan"
            >
              <RefreshCw className={`w-4 h-4 ${loadingPlan ? 'animate-spin' : ''}`} />
              <span>{loadingPlan ? 'Creating Plan...' : 'Generate New Plan'}</span>
            </button>
          </div>
        </div>

        {/* Explainability Tags */}
        {mealPlan?.explainability && mealPlan.explainability.length > 0 && (
          <div className="mt-6 pt-5 border-t border-slate-200/80 flex flex-wrap gap-2 text-xs">
            {mealPlan.explainability.map((exp, idx) => (
              <span
                key={idx}
                className={`px-3 py-1 rounded-xl font-medium border ${
                  exp.startsWith('⚠️')
                    ? 'bg-amber-50 text-amber-800 border-amber-200'
                    : 'bg-emerald-50 text-emerald-800 border-emerald-200'
                }`}
              >
                {exp}
              </span>
            ))}
          </div>
        )}
      </section>

      {/* Plan Invalidation Warning Banner if allergies changed */}
      {!isPlanValid && (
        <div className="p-5 rounded-3xl bg-amber-50 border-2 border-amber-300 text-amber-900 text-xs sm:text-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-fade-in">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-6 h-6 text-amber-600 shrink-0" />
            <div>
              <h3 className="font-bold text-amber-950">Safety Invalidation Warning</h3>
              <p className="text-amber-800 mt-0.5">
                Your declared profile allergies changed. Previous meal recommendations may no longer be safe.
              </p>
            </div>
          </div>
          <button
            onClick={onGeneratePlan}
            disabled={loadingPlan}
            className="px-4 py-2 rounded-xl bg-amber-700 hover:bg-amber-800 text-white font-semibold text-xs whitespace-nowrap transition-colors self-start sm:self-center"
          >
            Regenerate Safe Plan
          </button>
        </div>
      )}

      {/* Error UX */}
      {error && (
        <div className="p-5 rounded-3xl bg-rose-50 border border-rose-200 text-rose-900 text-xs sm:text-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
            <div>
              <h4 className="font-bold">Something went wrong while generating your meal plan.</h4>
              <p className="text-rose-700 text-xs mt-0.5">{error}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={onGeneratePlan}
              className="px-3.5 py-2 rounded-xl bg-rose-700 hover:bg-rose-800 text-white font-semibold text-xs transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* Daily Financial Safety Tracker */}
      <BudgetTracker
        targetBudget={targetBudget}
        currentCost={currentCost}
        meals={meals}
      />

      {/* Today's 4-Meal Plan Grid */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Today's Meals</h2>
            <p className="text-xs text-slate-500">4 daily meal slots optimized for your pantry and schedule</p>
          </div>
          <span className="text-xs font-medium text-slate-500">
            {meals.length} meals planned
          </span>
        </div>

        {loadingPlan ? (
          <div className="p-16 rounded-3xl bg-white border border-slate-200 text-center space-y-4 shadow-xs">
            <RefreshCw className="w-8 h-8 text-brand-600 animate-spin mx-auto" />
            <div className="space-y-1">
              <h3 className="text-base font-bold text-slate-900">Creating your safe meal plan...</h3>
              <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
                The agent loop is checking ingredients against your allergies ({profile?.allergies?.join(', ') || 'Peanut, Tree nuts'}), running budget arithmetic, and prioritizing your pantry items.
              </p>
            </div>
          </div>
        ) : meals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {meals.map((meal) => (
              <MealCard key={meal.id || meal.slot} meal={meal} slotLabel={meal.slot} />
            ))}
          </div>
        ) : (
          <div className="p-12 rounded-3xl bg-white border border-slate-200 text-center space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-brand-50 text-brand-600 flex items-center justify-center mx-auto">
              <Sparkles className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-bold text-slate-900">No active meal plan found</h3>
              <p className="text-xs text-slate-500 max-w-sm mx-auto">
                Click below to generate a tailored 4-meal plan based on your current pantry and budget.
              </p>
            </div>
            <button
              onClick={onGeneratePlan}
              className="px-5 py-2.5 rounded-xl bg-brand-700 hover:bg-brand-800 text-white font-semibold text-xs transition-colors"
            >
              Generate First Plan
            </button>
          </div>
        )}
      </section>
    </div>
  );
}
