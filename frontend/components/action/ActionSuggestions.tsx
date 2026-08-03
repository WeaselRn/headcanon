"use client";

import React from "react";
import { Lightbulb } from "lucide-react";

interface ActionSuggestionsProps {
  suggestions: string[];
  onSelectSuggestion: (actionText: string) => void;
}

export default function ActionSuggestions({
  suggestions,
  onSelectSuggestion,
}: ActionSuggestionsProps) {
  if (!suggestions || suggestions.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="flex items-center gap-1 text-xs text-slate-400 font-medium mr-1">
        <Lightbulb className="h-3.5 w-3.5 text-amber-400" /> Suggested:
      </span>
      {suggestions.map((suggestion, idx) => (
        <button
          key={idx}
          onClick={() => onSelectSuggestion(suggestion)}
          className="rounded-full border border-slate-700/60 bg-slate-900/80 px-3 py-1 text-xs text-slate-300 hover:border-purple-500 hover:bg-purple-950/40 hover:text-purple-200 transition-all shadow-sm"
        >
          {suggestion}
        </button>
      ))}
    </div>
  );
}
