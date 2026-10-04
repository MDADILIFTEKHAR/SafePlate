import React, { useState, useEffect } from 'react';
import { X, User, ShieldAlert, AlertTriangle, Save, Plus } from 'lucide-react';
import { api } from '../services/api';

export default function ProfileModal({ isOpen, onClose, profile, onProfileUpdated }) {
  const [formData, setFormData] = useState({
    name: '',
    daily_budget: 150,
    max_cooking_time_minutes: 30,
    spice_level: 'Low/medium',
    dietary_preference: 'Vegetarian',
    allergies: [],
    cuisines: ['Indian'],
    disliked_ingredients: []
  });

  const [newAllergy, setNewAllergy] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const commonAllergens = [
    'Peanut', 'Tree nuts', 'Dairy / Milk', 'Egg', 'Wheat / Gluten',
    'Soy', 'Fish', 'Shellfish', 'Sesame', 'Mustard'
  ];

  useEffect(() => {
    if (profile) {
      setFormData({
        name: profile.name || 'Aisha',
        daily_budget: profile.daily_budget || 150,
        max_cooking_time_minutes: profile.max_cooking_time_minutes || 30,
        spice_level: profile.spice_level || 'Low/medium',
        dietary_preference: profile.dietary_preference || 'Vegetarian',
        allergies: profile.allergies ? [...profile.allergies] : ['Peanut', 'Tree nuts'],
        cuisines: profile.cuisines || ['Indian'],
        disliked_ingredients: profile.disliked_ingredients || []
      });
    }
  }, [profile, isOpen]);

  if (!isOpen) return null;

  const handleToggleAllergy = (allergen) => {
    const exists = formData.allergies.some(a => a.toLowerCase() === allergen.toLowerCase());
    if (exists) {
      setFormData({
        ...formData,
        allergies: formData.allergies.filter(a => a.toLowerCase() !== allergen.toLowerCase())
      });
    } else {
      setFormData({
        ...formData,
        allergies: [...formData.allergies, allergen]
      });
    }
  };

  const handleAddCustomAllergy = (e) => {
    e.preventDefault();
    const clean = newAllergy.trim();
    if (!clean) return;
    if (!formData.allergies.some(a => a.toLowerCase() === clean.toLowerCase())) {
      setFormData({
        ...formData,
        allergies: [...formData.allergies, clean]
      });
    }
    setNewAllergy('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.updateProfile(formData);
      if (onProfileUpdated) onProfileUpdated();
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to update profile.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div 
        className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-xl w-full overflow-hidden flex flex-col max-h-[90vh]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="profile-title"
      >
        {/* Header */}
        <div className="p-6 pb-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-brand-100 text-brand-700 flex items-center justify-center font-bold">
              <User className="w-5 h-5" />
            </div>
            <div>
              <h2 id="profile-title" className="text-xl font-bold text-slate-900 tracking-tight">Your Food Profile</h2>
              <p className="text-xs text-slate-500">Configure your safety constraints, budget, and culinary tastes</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-6">
          {/* Invalidation Alert */}
          <div className="p-3.5 rounded-2xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <p className="leading-relaxed">
              <strong>Food Safety Rule:</strong> Updating your declared allergies automatically invalidates previously generated meal plans to guarantee strict allergy safety.
            </p>
          </div>

          {/* Name & Diet */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Your Name</label>
              <input
                id="profile-name-input"
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-slate-800 text-sm"
                required
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Dietary Preference</label>
              <select
                id="profile-diet-select"
                value={formData.dietary_preference}
                onChange={(e) => setFormData({ ...formData, dietary_preference: e.target.value })}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 text-slate-800 text-sm"
              >
                <option value="Vegetarian">Vegetarian</option>
                <option value="Vegan">Vegan</option>
                <option value="Non-Vegetarian">Non-Vegetarian</option>
              </select>
            </div>
          </div>

          {/* Allergies Section */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-bold text-slate-900 uppercase tracking-wider">
                Strict Food Allergies ({formData.allergies.length})
              </label>
              <span className="text-[11px] text-rose-600 font-medium flex items-center gap-1">
                <ShieldAlert className="w-3.5 h-3.5" /> Direct Exclusion
              </span>
            </div>

            {/* Common Allergen Chips */}
            <div className="flex flex-wrap gap-1.5">
              {commonAllergens.map((alg) => {
                const active = formData.allergies.some(a => a.toLowerCase() === alg.toLowerCase());
                return (
                  <button
                    key={alg}
                    type="button"
                    onClick={() => handleToggleAllergy(alg)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                      active
                        ? 'bg-rose-100 text-rose-800 border-2 border-rose-400 shadow-xs'
                        : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200'
                    }`}
                  >
                    {active ? `✕ ${alg}` : `+ ${alg}`}
                  </button>
                );
              })}
            </div>

            {/* Custom Allergy Input */}
            <div className="flex gap-2 pt-1">
              <input
                id="custom-allergy-input"
                type="text"
                value={newAllergy}
                onChange={(e) => setNewAllergy(e.target.value)}
                placeholder="Add other allergen (e.g. Pine nuts)..."
                className="flex-1 px-3.5 py-2 rounded-xl border border-slate-300 text-xs focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
              />
              <button
                type="button"
                onClick={handleAddCustomAllergy}
                className="px-3 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add</span>
              </button>
            </div>
          </div>

          {/* Budget & Cooking Time Sliders */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 pt-2 border-t border-slate-100 text-xs">
            <div>
              <div className="flex justify-between font-semibold text-slate-700 mb-1">
                <span>Daily Budget (₹)</span>
                <span className="text-slate-900 font-bold text-sm">₹{formData.daily_budget}</span>
              </div>
              <input
                id="profile-budget-slider"
                type="range"
                min="50"
                max="500"
                step="10"
                value={formData.daily_budget}
                onChange={(e) => setFormData({ ...formData, daily_budget: Number(e.target.value) })}
                className="w-full accent-brand-600"
              />
            </div>

            <div>
              <div className="flex justify-between font-semibold text-slate-700 mb-1">
                <span>Max Cooking Time</span>
                <span className="text-slate-900 font-bold text-sm">{formData.max_cooking_time_minutes} mins</span>
              </div>
              <input
                id="profile-cooking-time-slider"
                type="range"
                min="10"
                max="60"
                step="5"
                value={formData.max_cooking_time_minutes}
                onChange={(e) => setFormData({ ...formData, max_cooking_time_minutes: Number(e.target.value) })}
                className="w-full accent-brand-600"
              />
            </div>
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">
              {error}
            </div>
          )}

          {/* Action Footer */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl border border-slate-300 text-slate-700 hover:bg-slate-50 font-medium text-xs transition-colors"
            >
              Cancel
            </button>
            <button
              id="save-profile-btn"
              type="submit"
              disabled={submitting}
              className="px-5 py-2.5 rounded-xl bg-brand-700 hover:bg-brand-800 disabled:opacity-50 text-white font-semibold text-xs shadow-sm flex items-center gap-1.5 transition-colors"
            >
              <Save className="w-4 h-4" />
              <span>{submitting ? 'Saving...' : 'Save Profile'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
