"use client";

import React from "react";
import { User, Smile, Heart, MessageSquare } from "lucide-react";
import type { SceneCharacterSummary } from "@/types/scene";

interface CharacterCardProps {
  character: SceneCharacterSummary;
  isSelected?: boolean;
  onSelect?: () => void;
  onTalk?: () => void;
}

export default function CharacterCard({
  character,
  isSelected = false,
  onSelect,
  onTalk,
}: CharacterCardProps) {
  const { name, role, emotion, relationship_score, relationship_label } = character;

  return (
    <div
      onClick={onSelect}
      className={`group relative flex flex-col justify-between rounded-xl border p-4 transition-all cursor-pointer ${
        isSelected
          ? "border-purple-500 bg-purple-950/30 shadow-lg shadow-purple-950/40"
          : "border-slate-800 bg-slate-900/80 hover:border-slate-700 hover:bg-slate-800/60"
      }`}
    >
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-purple-950 text-purple-300 border border-purple-800/50">
          <User className="h-5 w-5" />
        </div>

        <div className="flex flex-col">
          <h4 className="text-sm font-semibold text-slate-100 group-hover:text-purple-300 transition-colors">
            {name}
          </h4>
          <span className="text-xs text-slate-400">{role || "Character"}</span>
        </div>
      </div>

      <div className="mt-4 flex flex-col gap-2 border-t border-slate-800/60 pt-3 text-xs">
        <div className="flex items-center justify-between text-slate-300">
          <span className="flex items-center gap-1 text-slate-400">
            <Smile className="h-3.5 w-3.5 text-amber-400" /> Emotion:
          </span>
          <span className="font-medium text-slate-200 capitalize">{emotion || "Neutral"}</span>
        </div>

        <div className="flex items-center justify-between text-slate-300">
          <span className="flex items-center gap-1 text-slate-400">
            <Heart className="h-3.5 w-3.5 text-rose-400" /> Relationship:
          </span>
          <span className="font-semibold text-purple-300">
            {relationship_score} ({relationship_label || "Neutral"})
          </span>
        </div>
      </div>

      {onTalk && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onTalk();
          }}
          className="mt-3 flex items-center justify-center gap-1.5 w-full rounded-lg bg-purple-900/40 py-1.5 text-xs font-medium text-purple-200 hover:bg-purple-800/60 transition-colors border border-purple-700/40"
        >
          <MessageSquare className="h-3.5 w-3.5" />
          Talk to {name}
        </button>
      )}
    </div>
  );
}
