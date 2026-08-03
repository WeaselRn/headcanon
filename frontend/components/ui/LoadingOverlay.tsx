"use client";

import React from "react";
import { Loader2 } from "lucide-react";

interface LoadingOverlayProps {
  isLoading: boolean;
  message?: string;
}

export default function LoadingOverlay({
  isLoading,
  message = "Updating universe simulation...",
}: LoadingOverlayProps) {
  if (!isLoading) return null;

  return (
    <div
      aria-live="polite"
      aria-busy={isLoading}
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-slate-950/80 backdrop-blur-sm transition-opacity"
    >
      <div className="flex flex-col items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/90 p-8 shadow-2xl">
        <Loader2 className="h-10 w-10 animate-spin text-purple-500" />
        <p className="text-sm font-medium text-slate-200">{message}</p>
      </div>
    </div>
  );
}
