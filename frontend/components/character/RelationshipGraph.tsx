"use client";

import React from "react";
import { Heart, Users } from "lucide-react";
import type { SceneCharacterSummary } from "@/types/scene";

interface RelationshipGraphProps {
  characters: SceneCharacterSummary[];
}

export default function RelationshipGraph({ characters }: RelationshipGraphProps) {
  if (!characters || characters.length === 0) {
    return (
      <div className="p-4 text-center text-xs text-slate-500 italic border border-slate-800 rounded-xl bg-slate-900/40">
        No character relationships in range.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/80 p-4">
      <div className="flex items-center gap-1.5 border-b border-slate-800 pb-2">
        <Heart className="h-4 w-4 text-rose-400" />
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
          Relationship Matrix
        </h3>
      </div>

      <div className="flex flex-col gap-3">
        {characters.map((char) => (
          <div key={char.character_id} className="flex flex-col gap-1 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-200">{char.name}</span>
              <span className="text-purple-300 font-medium">
                {char.relationship_score}/100 ({char.relationship_label || "Neutral"})
              </span>
            </div>

            {/* Meter Bar */}
            <div className="h-2 w-full overflow-hidden rounded-full bg-slate-800">
              <div
                className="h-full rounded-full bg-gradient-to-r from-purple-600 to-rose-500 transition-all duration-500"
                style={{ width: `${Math.min(100, Math.max(0, char.relationship_score))}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
