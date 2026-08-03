"use client";

import React, { useState } from "react";
import { Package, Search } from "lucide-react";
import InventoryItem from "./InventoryItem";

interface InventoryPanelProps {
  items: string[];
  onUseItem?: (itemId: string) => void;
  onInspectItem?: (itemId: string) => void;
  onGiveItem?: (itemId: string) => void;
}

export default function InventoryPanel({
  items,
  onUseItem,
  onInspectItem,
  onGiveItem,
}: InventoryPanelProps) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredItems = (items || []).filter((item) =>
    item.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/80 p-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
          <Package className="h-3.5 w-3.5 text-amber-400" /> Inventory ({items?.length || 0})
        </h3>
      </div>

      {items && items.length > 3 && (
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-500" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search items..."
            className="w-full rounded-lg border border-slate-800 bg-slate-950 pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:border-purple-500 focus:outline-none"
          />
        </div>
      )}

      {filteredItems.length > 0 ? (
        <div className="flex flex-col gap-2 max-h-[220px] overflow-y-auto pr-1">
          {filteredItems.map((item) => (
            <InventoryItem
              key={item}
              itemId={item}
              onUse={onUseItem}
              onInspect={onInspectItem}
              onGive={onGiveItem}
            />
          ))}
        </div>
      ) : (
        <p className="text-xs text-slate-500 italic p-2 text-center">
          {searchTerm ? "No matching items." : "Inventory is empty."}
        </p>
      )}
    </div>
  );
}
