"use client";

import React from "react";
import { Map, MapPin } from "lucide-react";
import type { SceneLocationSummary } from "@/types/scene";

interface WorldMapProps {
  currentLocation: SceneLocationSummary;
  onSelectLocation?: (locationId: string) => void;
}

export default function WorldMap({
  currentLocation,
  onSelectLocation,
}: WorldMapProps) {
  const connected = currentLocation.connected_locations || [];

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/80 p-4">
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <Map className="h-4 w-4 text-emerald-400" />
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
          World Navigation Map
        </h3>
      </div>

      <div className="relative min-h-[160px] rounded-lg border border-slate-800 bg-slate-950/80 p-4 flex flex-col items-center justify-center gap-4">
        {/* Active Node */}
        <div className="flex items-center gap-2 rounded-full border border-purple-500 bg-purple-950/80 px-4 py-1.5 text-xs font-semibold text-purple-200 shadow-lg shadow-purple-950/50">
          <MapPin className="h-4 w-4 animate-bounce text-purple-400" />
          <span>{currentLocation.name} (Current)</span>
        </div>

        {/* Connected Outlets */}
        {connected.length > 0 && (
          <div className="flex flex-wrap items-center justify-center gap-2">
            {connected.map((locId) => (
              <button
                key={locId}
                onClick={() => onSelectLocation?.(locId)}
                className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-300 hover:border-emerald-500 hover:bg-emerald-950/40 hover:text-emerald-200 transition-colors"
              >
                <MapPin className="h-3 w-3 text-slate-500" />
                <span className="capitalize">{locId.replace(/^loc_/, "").replace(/_/g, " ")}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
