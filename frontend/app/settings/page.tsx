"use client";

import React, { useState } from "react";
import { Settings as SettingsIcon, Save, Volume2, Eye, Cpu } from "lucide-react";

export default function SettingsPage() {
  const [apiUrl, setApiUrl] = useState(
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
  );
  const [autoMedia, setAutoMedia] = useState(false);
  const [highContrast, setHighContrast] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="flex flex-1 flex-col bg-slate-950 text-slate-100 p-6 lg:p-12 max-w-4xl mx-auto w-full">
      <div className="flex items-center gap-3 border-b border-slate-800 pb-4 mb-8">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-950 text-purple-400 border border-purple-800/50">
          <SettingsIcon className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-100">Application Settings</h1>
          <p className="text-xs text-slate-400">
            Configure Headcanon backend connectivity, media generation, and accessibility options.
          </p>
        </div>
      </div>

      {saved && (
        <div className="mb-6 rounded-lg bg-emerald-950/80 border border-emerald-800 p-3 text-xs text-emerald-200">
          Settings saved successfully!
        </div>
      )}

      <form onSubmit={handleSave} className="flex flex-col gap-8">
        {/* Backend Connectivity */}
        <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/80 p-6">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Cpu className="h-4 w-4 text-purple-400" /> Backend API Server URL
          </h3>
          <input
            type="url"
            value={apiUrl}
            onChange={(e) => setApiUrl(e.target.value)}
            required
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 focus:border-purple-500 focus:outline-none"
          />
          <p className="text-xs text-slate-500">
            URL of the Python FastAPI simulation engine backend.
          </p>
        </div>

        {/* Media Generation Preferences */}
        <div className="flex flex-col gap-4 rounded-xl border border-slate-800 bg-slate-900/80 p-6">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Volume2 className="h-4 w-4 text-amber-400" /> Media Generation Preferences
          </h3>
          <label className="flex items-center justify-between cursor-pointer">
            <span className="text-xs text-slate-200">
              Auto-generate scene illustrations on location travel
            </span>
            <input
              type="checkbox"
              checked={autoMedia}
              onChange={(e) => setAutoMedia(e.target.checked)}
              className="h-4 w-4 rounded border-slate-700 bg-slate-950 text-purple-600 focus:ring-purple-500"
            />
          </label>
        </div>

        {/* Accessibility & Visuals */}
        <div className="flex flex-col gap-4 rounded-xl border border-slate-800 bg-slate-900/80 p-6">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Eye className="h-4 w-4 text-blue-400" /> Accessibility & Motion
          </h3>
          <label className="flex items-center justify-between cursor-pointer">
            <span className="text-xs text-slate-200">High Contrast Mode</span>
            <input
              type="checkbox"
              checked={highContrast}
              onChange={(e) => setHighContrast(e.target.checked)}
              className="h-4 w-4 rounded border-slate-700 bg-slate-950 text-purple-600 focus:ring-purple-500"
            />
          </label>

          <label className="flex items-center justify-between cursor-pointer">
            <span className="text-xs text-slate-200">Reduced Motion & Transitions</span>
            <input
              type="checkbox"
              checked={reducedMotion}
              onChange={(e) => setReducedMotion(e.target.checked)}
              className="h-4 w-4 rounded border-slate-700 bg-slate-950 text-purple-600 focus:ring-purple-500"
            />
          </label>
        </div>

        <button
          type="submit"
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-purple-600 px-6 py-3 text-sm font-semibold text-white hover:bg-purple-500 transition-colors shadow-lg"
        >
          <Save className="h-4 w-4" /> Save Settings
        </button>
      </form>
    </div>
  );
}
