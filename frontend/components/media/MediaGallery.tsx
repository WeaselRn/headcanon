"use client";

import React from "react";
import { Image as ImageIcon } from "lucide-react";
import type { AssetMetadata } from "@/types/media";
import MediaCard from "./MediaCard";

interface MediaGalleryProps {
  assets: AssetMetadata[];
}

export default function MediaGallery({ assets }: MediaGalleryProps) {
  if (!assets || assets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-slate-800 rounded-2xl bg-slate-900/30">
        <ImageIcon className="h-12 w-12 text-slate-700 mb-3" />
        <h3 className="text-base font-semibold text-slate-300">Media Gallery Empty</h3>
        <p className="text-xs text-slate-500 max-w-sm mt-1">
          No generated illustrations, narration audio, or ambient media assets found yet.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {assets.map((asset) => (
        <MediaCard key={asset.asset_id} asset={asset} />
      ))}
    </div>
  );
}
