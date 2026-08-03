"use client";

import React, { useState } from "react";
import { BookOpen, History, Info } from "lucide-react";
import TimelineView from "./TimelineView";
import type { InteractionResult } from "@/types/interaction";

interface JournalPanelProps {
  history: InteractionResult[];
  knownInformation?: string[];
}

export default function JournalPanel({
  history,
  knownInformation = [],
}: JournalPanelProps) {
  const [activeTab, setActiveTab] = useState<"history" | "facts">("history");

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/80 p-4">
      {/* Tabs */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("history")}
            className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition-colors ${
              activeTab === "history"
                ? "bg-purple-950 text-purple-300 border border-purple-800/60"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <History className="h-3.5 w-3.5" />
            History ({history.length})
          </button>
          <button
            onClick={() => setActiveTab("facts")}
            className={`flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-lg transition-colors ${
              activeTab === "facts"
                ? "bg-purple-950 text-purple-300 border border-purple-800/60"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <BookOpen className="h-3.5 w-3.5" />
            Journal Facts ({knownInformation.length})
          </button>
        </div>
      </div>

      {activeTab === "history" ? (
        <TimelineView history={history} />
      ) : (
        <div className="flex flex-col gap-2 max-h-[260px] overflow-y-auto">
          {knownInformation.length > 0 ? (
            knownInformation.map((fact, idx) => (
              <div
                key={idx}
                className="flex items-start gap-2 rounded-lg border border-slate-800 bg-slate-950 p-2.5 text-xs text-slate-300"
              >
                <Info className="h-4 w-4 shrink-0 text-blue-400 mt-0.5" />
                <span>{fact}</span>
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-500 italic p-2 text-center">
              No journal facts recorded yet.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
