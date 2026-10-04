import React, { useState } from 'react';
import { X, Plus, Trash2, Package, Sparkles, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function PantryDrawer({ isOpen, onClose, pantry = [], onPantryUpdated, onBuildFromPantry }) {
  const [name, setName] = useState('');
  const [quantity, setQuantity] = useState('1 unit');
  const [category, setCategory] = useState('Vegetables');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleAddItem = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;

    setSubmitting(true);
    setError(null);
    try {
      await api.addPantryItem({
        name: name.trim(),
        quantity: quantity.trim(),
        category: category.trim()
      });
      setName('');
      setQuantity('1 unit');
      if (onPantryUpdated) onPantryUpdated();
    } catch (err) {
      setError(err.message || 'Failed to add pantry item.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteItem = async (id) => {
    try {
      await api.deletePantryItem(id);
      if (onPantryUpdated) onPantryUpdated();
    } catch (err) {
      setError(err.message || 'Failed to delete pantry item.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div 
        className="bg-white w-full max-w-md h-full shadow-2xl flex flex-col overflow-hidden"
        role="dialog"
        aria-modal="true"
        aria-labelledby="pantry-title"
      >
        {/* Drawer Header */}
        <div className="p-5 border-b border-slate-200 flex items-center justify-between bg-slate-50/70">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-brand-100 text-brand-700">
              <Package className="w-5 h-5" />
            </div>
            <div>
              <h2 id="pantry-title" className="font-bold text-slate-900 text-lg">My Pantry</h2>
              <p className="text-xs text-slate-500">{pantry.length} items in your kitchen inventory</p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-200/50 rounded-xl transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 overflow-y-auto flex-1 space-y-6">
          {/* Build From Pantry Banner */}
          <div className="p-4 rounded-2xl bg-gradient-to-br from-brand-50 to-teal-50 border border-brand-200 text-xs text-brand-900 space-y-3">
            <div className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-brand-700">
              <Sparkles className="w-4 h-4 text-brand-600" />
              <span>Budget Optimizer</span>
            </div>
            <p className="leading-relaxed">
              SafePlate prioritizes recipes using ingredients already in your pantry, saving you shopping expenses and keeping daily costs below budget!
            </p>
            <button
              id="build-pantry-plan-btn"
              onClick={() => {
                onClose();
                if (onBuildFromPantry) onBuildFromPantry();
              }}
              className="w-full py-2.5 px-3 rounded-xl bg-brand-700 hover:bg-brand-800 text-white font-semibold text-xs transition-colors flex items-center justify-center gap-2 shadow-xs"
            >
              <span>Build Plan From My Pantry</span>
            </button>
          </div>

          {/* Add Pantry Item Form */}
          <form onSubmit={handleAddItem} className="space-y-3 p-4 rounded-2xl bg-slate-50 border border-slate-200">
            <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider">Add Ingredient</h3>
            
            <div className="space-y-2 text-xs">
              <div>
                <label className="block font-medium text-slate-600 mb-1">Item Name</label>
                <input
                  id="pantry-item-name-input"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Tomato, Rice, Dal..."
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 bg-white"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block font-medium text-slate-600 mb-1">Quantity</label>
                  <input
                    type="text"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    placeholder="e.g. 500g, 2 units"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 bg-white"
                  />
                </div>
                <div>
                  <label className="block font-medium text-slate-600 mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 bg-white"
                  >
                    <option value="Vegetables">Vegetables</option>
                    <option value="Grains">Grains</option>
                    <option value="Legumes">Legumes</option>
                    <option value="Dairy">Dairy</option>
                    <option value="Spices">Spices</option>
                    <option value="General">General</option>
                  </select>
                </div>
              </div>

              <button
                id="add-pantry-item-btn"
                type="submit"
                disabled={submitting || !name.trim()}
                className="w-full mt-2 py-2 px-3 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:opacity-50 text-white font-medium text-xs flex items-center justify-center gap-1.5 transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>Add to Pantry</span>
              </button>
            </div>
          </form>

          {error && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">
              {error}
            </div>
          )}

          {/* Current Inventory List */}
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              Current Stock ({pantry.length})
            </h3>
            {pantry.length === 0 ? (
              <p className="text-xs text-slate-400 py-4 text-center">Your pantry is empty. Add your kitchen staples above!</p>
            ) : (
              <div className="space-y-2">
                {pantry.map((item) => (
                  <div
                    key={item.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-white border border-slate-200/90 shadow-xs hover:border-slate-300 transition-colors"
                  >
                    <div>
                      <h4 className="text-xs font-semibold text-slate-900">{item.name}</h4>
                      <p className="text-[11px] text-slate-500">{item.quantity} • {item.category}</p>
                    </div>
                    <button
                      onClick={() => handleDeleteItem(item.id)}
                      className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                      title="Remove from pantry"
                      aria-label={`Remove ${item.name}`}
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
