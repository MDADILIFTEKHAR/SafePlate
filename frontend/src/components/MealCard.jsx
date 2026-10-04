import React, { useState } from 'react';
import { Clock, IndianRupee, ChevronDown, ChevronUp, Check, Info, Sparkles, ChefHat } from 'lucide-react';
import SafetyBadge from './SafetyBadge';

export default function MealCard({ meal, slotLabel }) {
  const [expanded, setExpanded] = useState(false);

  const slotIcons = {
    breakfast: '🌅',
    lunch: '☀️',
    snack: '🍵',
    dinner: '🌙'
  };

  const slotColor = {
    breakfast: 'text-amber-700 bg-amber-50 border-amber-200',
    lunch: 'text-orange-700 bg-orange-50 border-orange-200',
    snack: 'text-teal-700 bg-teal-50 border-teal-200',
    dinner: 'text-indigo-700 bg-indigo-50 border-indigo-200'
  };

  const slot = (meal.slot || slotLabel || 'lunch').toLowerCase();

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs hover:shadow-md hover:border-slate-300 transition-all overflow-hidden flex flex-col">
      {/* Top Header Card */}
      <div className="p-5 pb-4 flex-1">
        <div className="flex items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xl" role="img" aria-label={slot}>{slotIcons[slot] || '🍽️'}</span>
            <span className={`text-xs uppercase tracking-wider font-semibold px-2 py-0.5 rounded-md border ${slotColor[slot] || 'text-slate-700 bg-slate-100'}`}>
              {slot}
            </span>
          </div>
          <SafetyBadge status={meal.safety_status} size="sm" />
        </div>

        <h3 className="font-bold text-slate-900 text-lg leading-snug tracking-tight mb-1.5">
          {meal.name}
        </h3>
        <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed mb-4">
          {meal.description || 'Delicious, balanced meal tailored to your allergy profile and budget.'}
        </p>

        {/* Quick Badges: Time & Cost */}
        <div className="flex items-center gap-3 text-xs font-medium text-slate-600">
          <span className="flex items-center gap-1 bg-slate-50 px-2.5 py-1 rounded-lg border border-slate-200">
            <Clock className="w-3.5 h-3.5 text-slate-500" />
            <span>{meal.cooking_time_minutes} mins</span>
          </span>
          <span className="flex items-center gap-1 bg-slate-50 px-2.5 py-1 rounded-lg border border-slate-200">
            <IndianRupee className="w-3.5 h-3.5 text-slate-500" />
            <span>₹{meal.estimated_cost?.toFixed(0) || 0}</span>
          </span>
          {meal.dietary_tags && meal.dietary_tags.length > 0 && (
            <span className="hidden sm:inline-block text-[11px] text-brand-700 bg-brand-50 px-2 py-0.5 rounded-md border border-brand-200 truncate max-w-[120px]">
              {meal.dietary_tags[0]}
            </span>
          )}
        </div>
      </div>

      {/* Expand / Details Toggle Button */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-5 py-2.5 bg-slate-50/70 hover:bg-slate-100/90 border-t border-slate-100 text-slate-700 text-xs font-semibold flex items-center justify-between transition-colors focus:ring-inset"
        aria-expanded={expanded}
      >
        <span className="flex items-center gap-1.5 text-brand-700">
          <ChefHat className="w-3.5 h-3.5" />
          <span>{expanded ? 'Hide Recipe & Safety Details' : 'View Ingredients & Steps'}</span>
        </span>
        {expanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
      </button>

      {/* Expanded Accordion Body */}
      {expanded && (
        <div className="p-5 bg-slate-50/50 border-t border-slate-100 space-y-4 text-xs">
          {/* Why this meal */}
          {meal.why_recommended && (
            <div className="p-3 rounded-xl bg-brand-50/60 border border-brand-200/80 text-brand-900">
              <div className="flex items-center gap-1.5 font-semibold text-[11px] uppercase tracking-wider text-brand-700 mb-1">
                <Sparkles className="w-3.5 h-3.5 text-brand-600" />
                <span>Why SafePlate Recommended This</span>
              </div>
              <p className="text-xs text-brand-800 leading-relaxed">{meal.why_recommended}</p>
            </div>
          )}

          {/* Safety Reason Note if any */}
          {meal.safety_reason && (
            <div className="p-3 rounded-xl bg-white border border-slate-200">
              <span className="font-semibold text-slate-700 block mb-0.5">Safety Engine Audit:</span>
              <span className="text-slate-600">{meal.safety_reason}</span>
            </div>
          )}

          {/* Ingredients list */}
          <div>
            <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider mb-2 text-slate-500">
              Ingredients ({meal.ingredients?.length || 0})
            </h4>
            <div className="space-y-1.5">
              {meal.ingredients?.map((ing, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2 rounded-lg bg-white border border-slate-200/80 text-xs"
                >
                  <div className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                    <span className="font-medium text-slate-800">{ing.name}</span>
                    <span className="text-slate-400">({ing.quantity})</span>
                  </div>
                  <div className="flex items-center gap-2">
                    {ing.in_pantry ? (
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                        In Pantry (₹0)
                      </span>
                    ) : (
                      <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">
                        ₹{ing.estimated_cost?.toFixed(0) || 0}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Cooking Steps */}
          {meal.steps && meal.steps.length > 0 && (
            <div>
              <h4 className="font-bold text-slate-900 uppercase text-[11px] tracking-wider mb-2 text-slate-500">
                Instructions
              </h4>
              <ol className="space-y-2 pl-4 list-decimal text-slate-700">
                {meal.steps.map((st, i) => (
                  <li key={i} className="pl-1 leading-relaxed">{st}</li>
                ))}
              </ol>
            </div>
          )}

          {/* Nutrition summary */}
          {meal.nutrition && Object.keys(meal.nutrition).length > 0 && (
            <div className="pt-2 border-t border-slate-200 flex flex-wrap gap-3 text-[11px] text-slate-500 font-medium">
              {meal.nutrition.calories && <span>⚡ {meal.nutrition.calories} kcal</span>}
              {meal.nutrition.protein_g && <span>💪 {meal.nutrition.protein_g}g Protein</span>}
              {meal.nutrition.carbs_g && <span>🌾 {meal.nutrition.carbs_g}g Carbs</span>}
              {meal.nutrition.fat_g && <span>🥑 {meal.nutrition.fat_g}g Fat</span>}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
