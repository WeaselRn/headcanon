"use client";

import React, { useState } from "react";
import Image from "next/image";
import { Image as ImageIcon, Sparkles, RefreshCw } from "lucide-react";
import type { SceneMediaAssets } from "@/types/scene";

interface SceneImageProps {
  media?: SceneMediaAssets;
  locationName: string;
  onGenerateMedia?: () => void;
}

export default function SceneImage({
  media,
  locationName,
  onGenerateMedia,
}: SceneImageProps) {
  const [imageError, setImageError] = useState(false);
  const illustrationUrl = media?.illustration_url;

  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-xl border border-slate-800 bg-slate-900 shadow-xl group">
      {illustrationUrl && !imageError ? (
        <Image
          src={illustrationUrl}
          alt={`Illustration of ${locationName}`}
          fill
          sizes="(max-width: 1200px) 100vw, 800px"
          className="object-cover transition-transform duration-700 group-hover:scale-105"
          onError={() => setImageError(true)}
          priority
        />
      ) : (
        <div className="flex h-full w-full flex-col items-center justify-center p-6 text-center bg-gradient-to-br from-slate-900 via-purple-950/20 to-slate-900">
          <ImageIcon className="h-12 w-12 text-slate-700 mb-3" />
          <p className="text-sm font-medium text-slate-400">
            {locationName} Illustration
          </p>
          <p className="text-xs text-slate-500 max-w-xs mt-1">
            Visual ambiance for this scene has not been generated yet.
          </p>

          {onGenerateMedia && (
            <button
              onClick={onGenerateMedia}
              className="mt-4 inline-flex items-center gap-2 rounded-lg border border-purple-600/50 bg-purple-950/40 px-3.5 py-1.5 text-xs font-medium text-purple-300 hover:bg-purple-900/60 transition-colors shadow-lg"
            >
              <Sparkles className="h-3.5 w-3.5 text-amber-400" />
              Generate Scene Illustration
            </button>
          )}
        </div>
      )}

      {/* Overlay Ambient Tags */}
      {media?.ambient_audio_tags && media.ambient_audio_tags.length > 0 && (
        <div className="absolute bottom-3 left-3 flex flex-wrap gap-1.5 z-10">
          {media.ambient_audio_tags.map((tag, idx) => (
            <span
              key={idx}
              className="rounded-full bg-slate-950/80 backdrop-blur-sm px-2.5 py-0.5 text-[10px] font-medium text-slate-300 border border-slate-700/60"
            >
              🔊 {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
