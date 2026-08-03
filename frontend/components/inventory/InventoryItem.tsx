"use client";

import React from "react";
import { Package, Eye, ArrowRightLeft, Hand } from "lucide-react";

interface InventoryItemProps {
  itemId: string;
  onUse?: (itemId: string) => void;
  onInspect?: (itemId: string) => void;
  onGive?: (itemId: string) => void;
}

export default function InventoryItem({
  itemId,
  onUse,
  onInspect,
  onGive,
}: InventoryItemProps) {
  const name = itemId.replace(/^item_|^obj_/, "").replace(/_/g, " ");

  return (
    <div className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/90 p-3 hover:border-slate-700 transition-colors">
      <div className="flex items-center gap-2.5">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-slate-800 text-amber-400 border border-slate-700">
          <Package className="h-4 w-4" />
        </div>
        <span className="text-xs font-semibold text-slate-200 capitalize">{name}</span>
      </div>

      <div className="flex items-center gap-1">
        {onInspect && (
          <button
            onClick={() => onInspect(itemId)}
            title="Inspect"
            className="rounded p-1.5 text-slate-400 hover:bg-slate-800 hover:text-slate-200 transition-colors"
          >
            <Eye className="h-3.5 w-3.5" />
          </button>
        )}
        {onUse && (
          <button
            onClick={() => onUse(itemId)}
            title="Use"
            className="rounded p-1.5 text-emerald-400 hover:bg-emerald-950/40 hover:text-emerald-300 transition-colors"
          >
            <Hand className="h-3.5 w-3.5" />
          </button>
        )}
        {onGive && (
          <button
            onClick={() => onGive(itemId)}
            title="Give"
            className="rounded p-1.5 text-purple-400 hover:bg-purple-950/40 hover:text-purple-300 transition-colors"
          >
            <ArrowRightLeft className="h-3.5 w-3.5" />
          </button>
        )}
      </div>
    </div>
  );
}
