"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Compass, Sparkles, Plus, Image as ImageIcon, BookOpen, ChevronRight, ShieldCheck } from "lucide-react";
import { listUniverses } from "@/lib/api";
import type { UniverseMetadataResponse } from "@/types/universe";

export default function LandingPage() {
  const [universes, setUniverses] = useState<UniverseMetadataResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUniverses() {
      try {
        const list = await listUniverses();
        setUniverses(list);
      } catch (err) {
        console.error("Failed to load universes:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchUniverses();
  }, []);

  return (
    <div className="flex flex-1 flex-col bg-slate-950 text-slate-100">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-slate-800 bg-gradient-to-b from-purple-950/40 via-slate-950 to-slate-950 py-20 px-6 lg:px-12 text-center">
        <div className="mx-auto max-w-4xl flex flex-col items-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-purple-500/30 bg-purple-950/60 px-4 py-1.5 text-xs font-semibold text-purple-300 backdrop-blur-md mb-6">
            <Sparkles className="h-4 w-4 text-amber-400" />
            <span>Persistent Fictional Universe Simulation Engine</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-tight">
            Step Inside Your Favorite <br />
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-amber-400 bg-clip-text text-transparent">
              Fictional Universes
            </span>
          </h1>

          <p className="mt-6 text-lg text-slate-300 max-w-2xl leading-relaxed">
            Headcanon isn&apos;t a chatbot. It is a persistent world compiler and simulation engine.
            Reconstruct story worlds, explore living locations, and shape timeline consequences.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/import"
              className="inline-flex items-center gap-2 rounded-xl bg-purple-600 px-6 py-3 text-sm font-semibold text-white hover:bg-purple-500 transition-colors shadow-lg shadow-purple-950/50"
            >
              <Plus className="h-4 w-4" />
              Import New Story
            </Link>

            <Link
              href="/library"
              className="inline-flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-900 px-6 py-3 text-sm font-semibold text-slate-200 hover:bg-slate-800 transition-colors"
            >
              <ImageIcon className="h-4 w-4 text-amber-400" />
              Media Library
            </Link>
          </div>
        </div>
      </section>

      {/* Available Universes Section */}
      <section className="py-16 px-6 lg:px-12 max-w-7xl mx-auto w-full">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-8">
          <div>
            <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
              <Compass className="h-5 w-5 text-purple-400" />
              Persistent Universes ({universes.length})
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Select a reconstructed universe to enter interactive simulation.
            </p>
          </div>

          <Link
            href="/import"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-purple-400 hover:text-purple-300 transition-colors"
          >
            <span>Import Story</span>
            <ChevronRight className="h-4 w-4" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-40 rounded-xl border border-slate-800 bg-slate-900/40 animate-pulse" />
            ))}
          </div>
        ) : universes.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {universes.map((u) => (
              <div
                key={u.universe_id}
                className="group flex flex-col justify-between rounded-xl border border-slate-800 bg-slate-900/80 p-6 hover:border-purple-500/60 hover:bg-slate-900 transition-all shadow-xl"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="rounded-md bg-purple-950/80 px-2.5 py-1 text-[11px] font-medium text-purple-300 border border-purple-800/40">
                      ID: {u.universe_id}
                    </span>
                    <ShieldCheck className="h-4 w-4 text-emerald-400" />
                  </div>

                  <h3 className="mt-4 text-lg font-bold text-slate-100 group-hover:text-purple-300 transition-colors">
                    {u.title}
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">Author: {u.author || "Unknown"}</p>
                </div>

                <div className="mt-6 flex items-center justify-between border-t border-slate-800/80 pt-4">
                  <div className="flex items-center gap-3 text-xs text-slate-400">
                    <span>{u.characters_count || 0} Characters</span>
                    <span>•</span>
                    <span>{u.locations_count || 0} Locations</span>
                  </div>

                  <Link
                    href={`/universe/${u.universe_id}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-purple-400 hover:text-purple-300"
                  >
                    <span>Dashboard</span>
                    <ChevronRight className="h-3.5 w-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-12 text-center border border-dashed border-slate-800 rounded-2xl bg-slate-900/20">
            <BookOpen className="h-10 w-10 text-slate-700 mb-3" />
            <h3 className="text-base font-semibold text-slate-300">No Universes Compiled Yet</h3>
            <p className="text-xs text-slate-500 max-w-sm mt-1">
              Import a PDF, EPUB, Plain Text file, or Web URL to reconstruct your first universe.
            </p>
            <Link
              href="/import"
              className="mt-4 rounded-lg bg-purple-600 px-4 py-2 text-xs font-semibold text-white hover:bg-purple-500 transition-colors"
            >
              Import First Story
            </Link>
          </div>
        )}
      </section>
    </div>
  );
}
