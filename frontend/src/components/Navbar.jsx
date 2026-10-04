import React from 'react';
import { Shield, Sparkles, User, Package, Search, Cpu } from 'lucide-react';

export default function Navbar({
  profile,
  health,
  onOpenCanIEat,
  onOpenPantry,
  onOpenProfile,
  onOpenAgentInspector
}) {
  const isDemo = health?.demo_mode;
  const isOllamaOnline = health?.ollama_available;

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200/80 transition-all">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        {/* SafePlate Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-teal-400 flex items-center justify-center text-white shadow-sm shadow-brand-500/20">
            <Shield className="w-6 h-6 stroke-[2.2]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg text-slate-900 tracking-tight">SafePlate</span>
              {/* AI Mode Indicator */}
              <button
                onClick={onOpenAgentInspector}
                className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium border transition-colors ${
                  isDemo
                    ? 'bg-amber-50 text-amber-800 border-amber-200 hover:bg-amber-100'
                    : isOllamaOnline
                    ? 'bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100'
                    : 'bg-rose-50 text-rose-800 border-rose-200 hover:bg-rose-100'
                }`}
                title="Click to inspect AI Agent Loop and system status"
              >
                <span className={`w-1.5 h-1.5 rounded-full ${isDemo ? 'bg-amber-500' : isOllamaOnline ? 'bg-emerald-500' : 'bg-rose-500'}`} />
                {isDemo ? 'Demo Mode' : isOllamaOnline ? `Ollama (${health?.model_name || 'Active'})` : 'Ollama Offline'}
              </button>
            </div>
            <p className="text-[11px] text-slate-500 hidden sm:block">AI meal planning built around what YOU can safely eat</p>
          </div>
        </div>

        {/* Action Controls & Navigation */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Can I Eat CTA */}
          <button
            id="nav-can-i-eat-btn"
            onClick={onOpenCanIEat}
            className="inline-flex items-center gap-2 px-3.5 py-2 text-xs sm:text-sm font-semibold rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm shadow-emerald-600/25 transition-all transform active:scale-98"
          >
            <Search className="w-4 h-4" />
            <span>Can I Eat This?</span>
          </button>

          {/* Pantry Button */}
          <button
            id="nav-pantry-btn"
            onClick={onOpenPantry}
            className="inline-flex items-center gap-1.5 px-3 py-2 text-xs sm:text-sm font-medium rounded-xl text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-200/80 transition-colors"
          >
            <Package className="w-4 h-4 text-slate-600" />
            <span className="hidden md:inline">Pantry</span>
            <span className="text-[11px] bg-white text-slate-700 font-semibold px-1.5 py-0.5 rounded-md border border-slate-200">
              {profile?.pantry?.length || 0}
            </span>
          </button>

          {/* Agent Inspector */}
          <button
            id="nav-agent-btn"
            onClick={onOpenAgentInspector}
            className="p-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-xl transition-colors border border-transparent hover:border-slate-200"
            title="Inspect Agent & AI Iterations"
            aria-label="Agent Inspector"
          >
            <Cpu className="w-4 h-4" />
          </button>

          {/* User Profile Pill */}
          <button
            id="nav-profile-btn"
            onClick={onOpenProfile}
            className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-xl border border-slate-200 hover:border-slate-300 bg-white hover:bg-slate-50 transition-colors"
          >
            <div className="w-6 h-6 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center font-bold text-xs">
              {profile?.name ? profile.name[0].toUpperCase() : 'A'}
            </div>
            <span className="text-xs sm:text-sm font-medium text-slate-800">{profile?.name || 'Aisha'}</span>
          </button>
        </div>
      </div>
    </header>
  );
}
