import React, { useState } from 'react';
import { X, Search, ShieldCheck, AlertTriangle, XCircle, HelpCircle, ArrowRight, Sparkles, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import SafetyBadge from './SafetyBadge';

export default function CanIEatModal({ isOpen, onClose, userAllergies = [] }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const quickExamples = [
    { label: '🥜 Peanut butter', query: 'peanut butter' },
    { label: '🍚 Steamed rice', query: 'steamed basmati rice' },
    { label: '🌰 Cashew nuts', query: 'roasted cashew nuts' },
    { label: '⚠️ Trace warning', query: 'may contain traces of peanuts' },
    { label: '❓ Unknown additive', query: 'mystery seasoning blend code E-999' }
  ];

  const handleCheck = async (textToCheck = query) => {
    const text = textToCheck.trim();
    if (!text) return;

    setLoading(true);
    setError(null);
    try {
      const data = await api.checkSafety(text);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to check food safety.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleCheck();
    }
  };

  const handleExampleClick = (exQuery) => {
    setQuery(exQuery);
    handleCheck(exQuery);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div 
        className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-xl w-full overflow-hidden flex flex-col max-h-[90vh]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="can-i-eat-title"
      >
        {/* Header */}
        <div className="p-6 pb-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
              <Search className="w-5 h-5" />
            </div>
            <div>
              <h2 id="can-i-eat-title" className="text-xl font-bold text-slate-900 tracking-tight">Can I Eat This?</h2>
              <p className="text-xs text-slate-500">
                Instant safety validation against your active allergies ({userAllergies.join(', ') || 'None'})
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition-colors"
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-5">
          {/* Input Section */}
          <div className="space-y-2">
            <label htmlFor="food-query-input" className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
              Enter ingredient, dish, or paste packaging label
            </label>
            <div className="relative">
              <textarea
                id="food-query-input"
                rows={3}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="e.g., Peanut butter, steamed rice, or paste 'Manufactured on equipment that processes tree nuts'..."
                className="w-full px-4 py-3 text-sm rounded-2xl border border-slate-300 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 transition-all resize-none text-slate-800"
              />
            </div>

            {/* Quick Test Chips */}
            <div className="flex flex-wrap items-center gap-1.5 pt-1">
              <span className="text-[11px] font-medium text-slate-400 mr-1">Try test:</span>
              {quickExamples.map((ex) => (
                <button
                  key={ex.query}
                  type="button"
                  onClick={() => handleExampleClick(ex.query)}
                  className="px-2.5 py-1 text-xs rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium transition-colors border border-slate-200/80 active:scale-95"
                >
                  {ex.label}
                </button>
              ))}
            </div>
          </div>

          {/* Action Button */}
          <button
            id="run-safety-check-btn"
            onClick={() => handleCheck()}
            disabled={loading || !query.trim()}
            className="w-full py-3 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold text-sm shadow-sm shadow-emerald-600/25 transition-all flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Validating with Safety Engine...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Check Safety Now</span>
              </>
            )}
          </button>

          {/* Error Message */}
          {error && (
            <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-800 text-xs">
              {error}
            </div>
          )}

          {/* Safety Evaluation Result Card */}
          {result && (
            <div className="rounded-2xl border border-slate-200 overflow-hidden bg-slate-50/50 p-5 space-y-4 animate-fade-in">
              <div className="flex items-center justify-between border-b border-slate-200/80 pb-3">
                <span className="text-xs uppercase font-bold tracking-wider text-slate-500">Evaluation Result</span>
                <SafetyBadge status={result.status} size="lg" />
              </div>

              {/* Status Reason & Details */}
              <div className="space-y-2">
                <h4 className="text-sm font-semibold text-slate-900 leading-snug">
                  {result.reason}
                </h4>

                {result.matched_terms?.length > 0 && (
                  <div className="text-xs text-slate-600 flex items-center gap-1.5 flex-wrap">
                    <span className="font-semibold text-slate-700">Matched Term(s):</span>
                    {result.matched_terms.map((t, idx) => (
                      <span key={idx} className="px-2 py-0.5 rounded-md bg-white border border-slate-200 text-rose-700 font-medium">
                        {t}
                      </span>
                    ))}
                  </div>
                )}

                {result.user_allergies_checked?.length > 0 && (
                  <div className="text-xs text-slate-500">
                    Checked against: <span className="font-medium text-slate-700">{result.user_allergies_checked.join(', ')}</span>
                  </div>
                )}
              </div>

              {/* Smart Substitutions if Unsafe */}
              {result.suggested_substitutions?.length > 0 && (
                <div className="p-3.5 rounded-xl bg-white border border-emerald-200 text-xs space-y-1.5">
                  <div className="flex items-center gap-1.5 font-bold text-emerald-800 text-[11px] uppercase tracking-wider">
                    <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Validated Safe Substitutions:</span>
                  </div>
                  <ul className="list-disc pl-4 space-y-1 text-slate-700">
                    {result.suggested_substitutions.map((sub, i) => (
                      <li key={i} className="font-medium">{sub}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Mandatory Medical Disclaimer Notice */}
              <div className="p-3 rounded-xl bg-slate-100 border border-slate-200 text-[11px] text-slate-500 leading-relaxed">
                ℹ️ {result.notice}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
