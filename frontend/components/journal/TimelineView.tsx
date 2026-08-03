"use client";

import React from "react";
import { History, GitCommit } from "lucide-react";
import type { InteractionResult } from "@/types/interaction";

interface TimelineViewProps {
  history: InteractionResult[];
}

export default function TimelineView({ history }: TimelineViewProps) {
  if (!history || history.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-6 text-center border border-dashed border-slate-800 rounded-xl bg-slate-900/30">
        <History className="h-8 w-8 text-slate-600 mb-2" />
        <p className="text-xs text-slate-400">No interaction events recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
        <History className="h-3.5 w-3.5 text-purple-400" /> Chronological Timeline ({history.length})
      </h3>

      <div className="relative border-l-2 border-slate-800 ml-3 pl-4 space-y-4 max-h-[300px] overflow-y-auto pr-1">
        {history.map((item, idx) => (
          <div key={item.interaction_id || idx} className="relative">
            <div className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-purple-500 ring-4 ring-slate-950" />
            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 text-xs">
              <div className="flex items-center justify-between font-semibold text-purple-300 mb-1">
                <span className="capitalize">{item.action}</span>
                {item.target && (
                  <span className="text-slate-400 font-normal">→ {item.target}</span>
                )}
              </div>
              <p className="text-slate-300 italic">&ldquo;{item.narration}&rdquo;</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
