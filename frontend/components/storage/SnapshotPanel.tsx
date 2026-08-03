"use client";

import React, { useState } from "react";
import { Save, RotateCcw, Clock, Plus } from "lucide-react";
import type { Snapshot } from "@/types/world";

interface SnapshotPanelProps {
  snapshots: Snapshot[];
  onCreateSnapshot: (description: string) => void;
  onRestoreSnapshot: (snapshotId: string) => void;
  disabled?: boolean;
}

export default function SnapshotPanel({
  snapshots,
  onCreateSnapshot,
  onRestoreSnapshot,
  disabled = false,
}: SnapshotPanelProps) {
  const [desc, setDesc] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (disabled) return;
    onCreateSnapshot(desc.trim() || "Manual Snapshot");
    setDesc("");
    setIsCreating(false);
  };

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/80 p-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
          <Save className="h-3.5 w-3.5 text-blue-400" /> Save Snapshots ({snapshots?.length || 0})
        </h3>

        <button
          onClick={() => setIsCreating(!isCreating)}
          disabled={disabled}
          className="flex items-center gap-1 rounded bg-purple-900/40 px-2 py-1 text-[11px] font-medium text-purple-200 hover:bg-purple-800/60 border border-purple-700/40 transition-colors disabled:opacity-50"
        >
          <Plus className="h-3 w-3" /> Save Point
        </button>
      </div>

      {isCreating && (
        <form onSubmit={handleCreate} className="flex gap-2">
          <input
            type="text"
            value={desc}
            onChange={(e) => setDesc(e.target.value)}
            placeholder="Snapshot description..."
            className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-xs text-slate-100 placeholder-slate-500 focus:border-purple-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={disabled}
            className="rounded-lg bg-purple-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-purple-500 transition-colors"
          >
            Save
          </button>
        </form>
      )}

      {snapshots && snapshots.length > 0 ? (
        <div className="flex flex-col gap-2 max-h-[200px] overflow-y-auto pr-1">
          {snapshots.map((snap) => (
            <div
              key={snap.snapshot_id}
              className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950 p-2.5 text-xs"
            >
              <div className="flex flex-col">
                <span className="font-semibold text-slate-200">
                  {snap.metadata.description || snap.snapshot_id}
                </span>
                <span className="flex items-center gap-1 text-[10px] text-slate-400 mt-0.5">
                  <Clock className="h-3 w-3 text-amber-400" />
                  {snap.metadata.created_at ? new Date(snap.metadata.created_at).toLocaleString() : "Recent"}
                </span>
              </div>

              <button
                onClick={() => onRestoreSnapshot(snap.snapshot_id)}
                disabled={disabled}
                title="Restore Snapshot"
                className="flex items-center gap-1 rounded bg-slate-800 px-2 py-1 text-[11px] font-medium text-slate-300 hover:bg-slate-700 transition-colors disabled:opacity-50"
              >
                <RotateCcw className="h-3 w-3 text-purple-400" />
                Restore
              </button>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-xs text-slate-500 italic p-2 text-center">No snapshots saved yet.</p>
      )}
    </div>
  );
}
