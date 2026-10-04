import React, { useState, useEffect } from 'react';
import { X, Cpu, CheckCircle2, AlertTriangle, ShieldCheck, Clock, RefreshCw, Terminal } from 'lucide-react';
import { api } from '../services/api';

export default function AgentInspectorModal({ isOpen, onClose, health, lastRunId }) {
  const [runDetails, setRunDetails] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && lastRunId) {
      loadRunDetails(lastRunId);
    }
  }, [isOpen, lastRunId]);

  const loadRunDetails = async (runId) => {
    setLoading(true);
    try {
      const data = await api.getAgentRun(runId);
      setRunDetails(data);
    } catch (e) {
      console.log('No previous run details:', e);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div 
        className="bg-white rounded-3xl border border-slate-200 shadow-2xl max-w-2xl w-full overflow-hidden flex flex-col max-h-[90vh]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="agent-inspector-title"
      >
        {/* Header */}
        <div className="p-6 pb-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold">
              <Cpu className="w-5 h-5" />
            </div>
            <div>
              <h2 id="agent-inspector-title" className="text-xl font-bold text-slate-900 tracking-tight">Agent & AI Engine Inspector</h2>
              <p className="text-xs text-slate-500">Autonomous repair loops, safety validation gates, and local AI state</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6">
          {/* Architecture Pipeline Banner */}
          <div className="p-4 rounded-2xl bg-slate-900 text-slate-100 space-y-3 font-mono text-xs shadow-inner">
            <div className="flex items-center justify-between text-[11px] text-slate-400 border-b border-slate-800 pb-2">
              <span className="flex items-center gap-1.5 text-teal-400 font-semibold">
                <Terminal className="w-3.5 h-3.5" /> Core Product Architecture
              </span>
              <span>AI Generates → Rule Engine Validates → App Decides</span>
            </div>
            <div className="text-[11px] text-slate-300 leading-relaxed font-sans">
              <span className="text-emerald-400 font-semibold">Safety Invariant:</span> No meal plan recommendation can bypass the deterministic rule validation layer. If an allergen is detected, it is immediately routed to the repair loop or rejected.
            </div>
          </div>

          {/* System Environment Status Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-400 text-[10px] uppercase font-bold">Execution Mode</span>
              <p className="font-semibold text-slate-800 mt-0.5">
                {health?.demo_mode ? 'Deterministic Demo' : 'Live Local AI'}
              </p>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-400 text-[10px] uppercase font-bold">Ollama Status</span>
              <p className={`font-semibold mt-0.5 flex items-center gap-1.5 ${health?.ollama_available ? 'text-emerald-600' : 'text-slate-500'}`}>
                <span className={`w-2 h-2 rounded-full ${health?.ollama_available ? 'bg-emerald-500' : 'bg-slate-400'}`} />
                {health?.ollama_available ? 'Connected' : 'Offline'}
              </p>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-400 text-[10px] uppercase font-bold">Model</span>
              <p className="font-semibold text-slate-800 mt-0.5 truncate" title={health?.model_name}>
                {health?.model_name || 'Llama 3.2'}
              </p>
            </div>
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-400 text-[10px] uppercase font-bold">Max Iterations</span>
              <p className="font-semibold text-slate-800 mt-0.5">3 (Bounded)</p>
            </div>
          </div>

          {/* Last Agent Run Trace */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center justify-between">
              <span>Agent Iteration Trace</span>
              {runDetails && (
                <span className="text-[11px] font-normal text-slate-500">
                  Execution time: {runDetails.execution_time_ms}ms
                </span>
              )}
            </h3>

            {loading ? (
              <div className="py-8 text-center text-xs text-slate-500 flex items-center justify-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin text-slate-400" />
                <span>Loading agent execution trace...</span>
              </div>
            ) : runDetails && runDetails.steps_data?.length > 0 ? (
              <div className="space-y-3">
                {runDetails.steps_data.map((step) => (
                  <div key={step.iteration} className="p-4 rounded-2xl bg-white border border-slate-200 text-xs space-y-2 shadow-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-slate-800 flex items-center gap-2">
                        <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-700 flex items-center justify-center text-[11px]">
                          {step.iteration}
                        </span>
                        Iteration {step.iteration}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                        step.status === 'valid'
                          ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                          : 'bg-amber-50 text-amber-700 border border-amber-200'
                      }`}>
                        {step.status === 'valid' ? 'Passed Validation Gate' : 'Constraint Violations'}
                      </span>
                    </div>

                    <p className="text-slate-600 text-[11px]">{step.candidate_summary}</p>

                    {step.violations?.length > 0 && (
                      <div className="p-2.5 rounded-xl bg-rose-50 border border-rose-200 text-[11px] text-rose-800 space-y-1">
                        <span className="font-bold block">Violations Flagged:</span>
                        <ul className="list-disc pl-4 space-y-0.5">
                          {step.violations.map((v, i) => (
                            <li key={i}>{v}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {step.repair_instruction && (
                      <div className="p-2.5 rounded-xl bg-indigo-50 border border-indigo-200 text-[11px] text-indigo-900 space-y-1">
                        <span className="font-bold block">Synthesized Repair Instruction:</span>
                        <p className="whitespace-pre-line text-slate-700 font-mono text-[10px]">{step.repair_instruction}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200 text-center text-xs text-slate-500 space-y-2">
                <CheckCircle2 className="w-6 h-6 text-emerald-500 mx-auto" />
                <p className="font-medium text-slate-700">Clean Agent Execution</p>
                <p className="text-[11px] text-slate-400">
                  Generate a meal plan to inspect live multi-step repair loops, constraint validation, and execution timings.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
