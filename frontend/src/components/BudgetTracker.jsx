import React from 'react';
import { IndianRupee, PieChart, CheckCircle2, AlertCircle } from 'lucide-react';

export default function BudgetTracker({ targetBudget = 150, currentCost = 0, meals = [] }) {
  const target = Number(targetBudget) || 150;
  const used = Number(currentCost) || 0;
  const remaining = Math.max(0, target - used);
  const percentUsed = Math.min(100, Math.round((used / target) * 100));
  const isOverBudget = used > target;

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 p-5 shadow-xs transition-all hover:border-slate-300">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Daily Financial Safety</span>
          <div className="flex items-baseline gap-2 mt-0.5">
            <h3 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center">
              ₹{used.toFixed(0)}
              <span className="text-sm font-medium text-slate-500 ml-1.5">/ ₹{target.toFixed(0)}</span>
            </h3>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
              isOverBudget 
                ? 'bg-rose-50 text-rose-700 border border-rose-200' 
                : 'bg-emerald-50 text-emerald-700 border border-emerald-200'
            }`}>
              {isOverBudget ? `₹${(used - target).toFixed(0)} over budget` : `₹${remaining.toFixed(0)} left`}
            </span>
          </div>
        </div>

        {/* Breakdown tags */}
        <div className="flex flex-wrap gap-2 text-xs">
          {meals.map((m) => (
            <div key={m.id || m.slot} className="px-2.5 py-1 rounded-lg bg-slate-50 border border-slate-200 text-slate-600 flex items-center gap-1.5">
              <span className="capitalize font-medium text-slate-800">{m.slot}:</span>
              <span className="font-semibold text-slate-900">₹{m.estimated_cost?.toFixed(0) || 0}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-1.5">
        <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden flex">
          <div
            className={`h-full transition-all duration-500 rounded-full ${
              isOverBudget 
                ? 'bg-rose-500' 
                : percentUsed > 85 
                ? 'bg-amber-500' 
                : 'bg-emerald-500'
            }`}
            style={{ width: `${Math.min(100, (used / target) * 100)}%` }}
          />
        </div>
        <div className="flex justify-between items-center text-[11px] text-slate-500">
          <span>₹0</span>
          <span>50% (₹{(target / 2).toFixed(0)})</span>
          <span>Target: ₹{target.toFixed(0)}</span>
        </div>
      </div>
    </div>
  );
}
