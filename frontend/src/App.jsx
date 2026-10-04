import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import CanIEatModal from './components/CanIEatModal';
import PantryDrawer from './components/PantryDrawer';
import ProfileModal from './components/ProfileModal';
import AgentInspectorModal from './components/AgentInspectorModal';
import { api } from './services/api';

export default function App() {
  const [profile, setProfile] = useState(null);
  const [mealPlan, setMealPlan] = useState(null);
  const [health, setHealth] = useState(null);
  const [lastRunId, setLastRunId] = useState(null);
  const [loadingPlan, setLoadingPlan] = useState(false);
  const [error, setError] = useState(null);

  // Modals state
  const [canIEatOpen, setCanIEatOpen] = useState(false);
  const [pantryOpen, setPantryOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [agentOpen, setAgentOpen] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [hData, pData, mData] = await Promise.all([
        api.getHealth().catch(e => ({ status: 'error', demo_mode: true, ollama_available: false })),
        api.getProfile().catch(e => null),
        api.getMealPlan().catch(e => null)
      ]);
      setHealth(hData);
      setProfile(pData);
      
      if (mData) {
        setMealPlan(mData);
      } else if (pData) {
        // Auto-generate initial plan if none exists
        generatePlanInternal(false);
      }
    } catch (err) {
      console.error('Error loading initial SafePlate data:', err);
    }
  };

  const generatePlanInternal = async (forcePantry = false) => {
    if (loadingPlan) return;
    setLoadingPlan(true);
    setError(null);
    try {
      const plan = await api.generateMealPlan({ force_pantry: forcePantry });
      setMealPlan(plan);
      if (plan.id) {
        setLastRunId(plan.id);
      }
    } catch (err) {
      console.error('Plan generation failed:', err);
      setError(err.message || 'Could not generate a safe meal plan. Check your constraints.');
    } finally {
      setLoadingPlan(false);
    }
  };

  const handleProfileUpdated = async () => {
    try {
      const updated = await api.getProfile();
      setProfile(updated);
      // Re-fetch meal plan to reflect validity changes
      const plan = await api.getMealPlan();
      setMealPlan(plan);
    } catch (err) {
      console.error('Failed to refresh profile:', err);
    }
  };

  const handlePantryUpdated = async () => {
    try {
      const updated = await api.getProfile();
      setProfile(updated);
    } catch (err) {
      console.error('Failed to refresh pantry:', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
      {/* Navigation */}
      <Navbar
        profile={profile}
        health={health}
        onOpenCanIEat={() => setCanIEatOpen(true)}
        onOpenPantry={() => setPantryOpen(true)}
        onOpenProfile={() => setProfileOpen(true)}
        onOpenAgentInspector={() => setAgentOpen(true)}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 pt-6">
        <HomePage
          profile={profile}
          mealPlan={mealPlan}
          loadingPlan={loadingPlan}
          error={error}
          onGeneratePlan={() => generatePlanInternal(false)}
          onOpenCanIEat={() => setCanIEatOpen(true)}
          onOpenPantry={() => setPantryOpen(true)}
          onOpenProfile={() => setProfileOpen(true)}
          onOpenAgentInspector={() => setAgentOpen(true)}
        />
      </main>

      {/* Footer with Mandatory Disclaimer */}
      <footer className="border-t border-slate-200/80 bg-white py-6 mt-auto">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 text-center text-xs text-slate-500 space-y-2">
          <p className="max-w-2xl mx-auto leading-relaxed">
            <strong>Medical Notice:</strong> SafePlate is an informational food-safety and AI meal planning assistant. Always inspect physical product packaging, verify ingredient labels, and follow direct guidance from your doctor or allergist.
          </p>
          <p className="text-[11px] text-slate-400">
            SafePlate MVP • Local-First Architecture • AI Generates • Rule Engine Validates • Application Decides
          </p>
        </div>
      </footer>

      {/* Interactive Modals and Drawers */}
      <CanIEatModal
        isOpen={canIEatOpen}
        onClose={() => setCanIEatOpen(false)}
        userAllergies={profile?.allergies || []}
      />

      <PantryDrawer
        isOpen={pantryOpen}
        onClose={() => setPantryOpen(false)}
        pantry={profile?.pantry || []}
        onPantryUpdated={handlePantryUpdated}
        onBuildFromPantry={() => generatePlanInternal(true)}
      />

      <ProfileModal
        isOpen={profileOpen}
        onClose={() => setProfileOpen(false)}
        profile={profile}
        onProfileUpdated={handleProfileUpdated}
      />

      <AgentInspectorModal
        isOpen={agentOpen}
        onClose={() => setAgentOpen(false)}
        health={health}
        lastRunId={lastRunId}
      />
    </div>
  );
}
