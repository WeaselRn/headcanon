"use client";

import React, { useState, FormEvent } from "react";
import { Send, MessageSquare, Eye, Navigation, Search, Clock, Package } from "lucide-react";

interface ActionBarProps {
  onExecuteAction: (userInput: string) => void;
  disabled?: boolean;
}

export default function ActionBar({
  onExecuteAction,
  disabled = false,
}: ActionBarProps) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onExecuteAction(input.trim());
    setInput("");
  };

  const handleQuickAction = (prefix: string) => {
    if (disabled) return;
    onExecuteAction(prefix);
  };

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/90 p-4 backdrop-blur-md shadow-2xl">
      {/* Category Action Pills */}
      <div className="flex flex-wrap gap-2 text-xs">
        <button
          type="button"
          onClick={() => handleQuickAction("Talk to someone")}
          disabled={disabled}
          className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-800/60 px-3 py-1.5 text-slate-300 hover:border-purple-500 hover:bg-purple-950/30 transition-colors disabled:opacity-50"
        >
          <MessageSquare className="h-3.5 w-3.5 text-purple-400" />
          Talk
        </button>

        <button
          type="button"
          onClick={() => handleQuickAction("Observe surrounding area")}
          disabled={disabled}
          className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-800/60 px-3 py-1.5 text-slate-300 hover:border-blue-500 hover:bg-blue-950/30 transition-colors disabled:opacity-50"
        >
          <Eye className="h-3.5 w-3.5 text-blue-400" />
          Observe
        </button>

        <button
          type="button"
          onClick={() => handleQuickAction("Inspect items nearby")}
          disabled={disabled}
          className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-800/60 px-3 py-1.5 text-slate-300 hover:border-emerald-500 hover:bg-emerald-950/30 transition-colors disabled:opacity-50"
        >
          <Search className="h-3.5 w-3.5 text-emerald-400" />
          Inspect
        </button>

        <button
          type="button"
          onClick={() => handleQuickAction("Wait for time to pass")}
          disabled={disabled}
          className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-800/60 px-3 py-1.5 text-slate-300 hover:border-amber-500 hover:bg-amber-950/30 transition-colors disabled:opacity-50"
        >
          <Clock className="h-3.5 w-3.5 text-amber-400" />
          Wait
        </button>
      </div>

      {/* Main Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="What do you want to do? (e.g. Ask Hermione about Snape, Look around...)"
          disabled={disabled}
          className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500 disabled:opacity-50"
        />

        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className="inline-flex items-center gap-2 rounded-lg bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg hover:bg-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50 transition-colors"
        >
          <span>Act</span>
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}
