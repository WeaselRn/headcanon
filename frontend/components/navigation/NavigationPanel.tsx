"use client";

import React from "react";
import { Compass, Navigation as NavIcon, ChevronRight } from "lucide-react";
import type { SceneLocationSummary } from "@/types/scene";

interface NavigationPanelProps {
  location: SceneLocationSummary;
  universeTitle?: string;
  onTravel?: (locationId: string) => void;
  disabled?: boolean;
}

export default function NavigationPanel({
  location,
  universeTitle = "Universe",
  onTravel,
  disabled = false,
}: NavigationPanelProps) {
  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/80 p-4">
      {/* Breadcrumb Path */}
      <div className="flex items-center gap-1.5 text-xs text-slate-400">
        <span>{universeTitle}</span>
        <ChevronRight className="h-3 w-3 text-slate-600" />
        <span className="font-semibold text-purple-300">{location.name}</span>
      </div>

      <div className="flex items-center justify-between border-t border-slate-800/80 pt-2">
        <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Compass className="h-3.5 w-3.5 text-blue-400" /> Connected Destinations
        </h4>
      </div>

      {location.connected_locations && location.connected_locations.length > 0 ? (
        <div className="flex flex-col gap-2">
          {location.connected_locations.map((destId) => (
            <button
              key={destId}
              onClick={() => onTravel?.(destId)}
              disabled={disabled}
              className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/60 px-3.5 py-2 text-xs font-medium text-slate-200 hover:border-blue-500/60 hover:bg-blue-950/30 hover:text-blue-200 transition-colors disabled:opacity-50"
            >
              <span className="capitalize">{destId.replace(/^loc_/, "").replace(/_/g, " ")}</span>
              <NavIcon className="h-3.5 w-3.5 text-slate-500" />
            </button>
          ))}
        </div>
      ) : (
        <p className="text-xs text-slate-500 italic">No connected exits found.</p>
      )}
    </div>
  );
}
