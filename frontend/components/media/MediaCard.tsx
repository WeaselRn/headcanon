"use client";

import React from "react";
import Image from "next/image";
import { Image as ImageIcon, Volume2, Calendar } from "lucide-react";
import type { AssetMetadata } from "@/types/media";

interface MediaCardProps {
  asset: AssetMetadata;
}

export default function MediaCard({ asset }: MediaCardProps) {
  return (
    <div className="flex flex-col overflow-hidden rounded-xl border border-slate-800 bg-slate-900 shadow-xl transition-all hover:border-purple-500/50">
      <div className="relative aspect-video w-full bg-slate-950">
        {asset.image_url ? (
          <Image
            src={asset.image_url}
            alt={`Media asset ${asset.asset_id}`}
            fill
            sizes="(max-width: 768px) 100vw, 400px"
            className="object-cover"
          />
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center p-4 text-center">
            <ImageIcon className="h-8 w-8 text-slate-700 mb-2" />
            <span className="text-xs font-medium text-slate-400">Scene Illustration</span>
          </div>
        )}
      </div>

      <div className="flex flex-col gap-2 p-4 text-xs">
        <div className="flex items-center justify-between">
          <span className="font-semibold text-slate-200">{asset.asset_id}</span>
          <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] text-slate-400">
            {asset.model_used}
          </span>
        </div>

        <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
          <Calendar className="h-3 w-3 text-purple-400" />
          <span>{asset.generation_time ? new Date(asset.generation_time).toLocaleDateString() : "Recent"}</span>
        </div>

        {asset.audio_url && (
          <div className="mt-1 flex items-center gap-2 rounded-lg bg-slate-950 p-2 text-slate-300">
            <Volume2 className="h-4 w-4 text-amber-400 shrink-0" />
            <audio controls src={asset.audio_url} className="h-6 w-full" />
          </div>
        )}
      </div>
    </div>
  );
}
