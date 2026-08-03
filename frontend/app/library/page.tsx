"use client";

import React from "react";
import { Image as ImageIcon } from "lucide-react";
import { useHeadcanon } from "@/lib/store";
import MediaGallery from "@/components/media/MediaGallery";

export default function MediaLibraryPage() {
  const { mediaAssets } = useHeadcanon();

  return (
    <div className="flex flex-1 flex-col bg-slate-950 text-slate-100 p-6 lg:p-12 max-w-7xl mx-auto w-full">
      <div className="flex items-center gap-3 border-b border-slate-800 pb-4 mb-8">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-950 text-purple-400 border border-purple-800/50">
          <ImageIcon className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-slate-100">Multimedia Media Library</h1>
          <p className="text-xs text-slate-400">
            Revisit generated scene illustrations, narration audio scripts, and soundscapes.
          </p>
        </div>
      </div>

      <MediaGallery assets={mediaAssets} />
    </div>
  );
}
