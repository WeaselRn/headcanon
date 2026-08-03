"use client";

import React from "react";
import { Sparkles, Clock, Compass } from "lucide-react";
import type { Scene } from "@/types/scene";

interface SceneNarrationProps {
  scene: Scene;
}

export default function SceneNarration({ scene }: SceneNarrationProps) {
  const { narration, environment, location } = scene;

  return (
    <div className="flex flex-col gap-4 rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-md">
      {/* Location & Environment Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-purple-400">
          <Compass className="h-4 w-4" />
          <span>{location.name}</span>
          <span className="text-xs text-slate-500">({location.category})</span>
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-400">
          <div className="flex items-center gap-1">
            <Clock className="h-3.5 w-3.5 text-amber-400" />
            <span>
              Day {environment.time.day}, {environment.time.hour.toString().padStart(2, "0")}:
              {environment.time.minute.toString().padStart(2, "0")}
            </span>
          </div>
          {environment.atmosphere && (
            <span className="rounded-full bg-purple-950/80 px-2.5 py-0.5 text-purple-300 border border-purple-800/40">
              {environment.atmosphere}
            </span>
          )}
        </div>
      </div>

      {/* Main Narration Body */}
      <div className="prose prose-invert max-w-none text-slate-200 leading-relaxed">
        <p className="text-base sm:text-lg font-serif italic text-slate-300">
          &ldquo;{narration}&rdquo;
        </p>
      </div>

      {/* Sensory Details */}
      {environment.sensory_details && environment.sensory_details.length > 0 && (
        <div className="flex flex-wrap gap-2 pt-2">
          {environment.sensory_details.map((detail, idx) => (
            <span
              key={idx}
              className="inline-flex items-center gap-1.5 rounded-md bg-slate-800/70 px-2.5 py-1 text-xs text-slate-300 border border-slate-700/50"
            >
              <Sparkles className="h-3 w-3 text-amber-400" />
              {detail}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
