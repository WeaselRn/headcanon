"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { Compass, Users, MapPin, ShieldCheck, Play, Trash2, Calendar, Loader2 } from "lucide-react";
import { getUniverse, deleteUniverse } from "@/lib/api";
import type { UniverseMetadataResponse } from "@/types/universe";

export default function UniverseDashboardPage() {
  const params = useParams();
  const router = useRouter();
  const universeId = params?.id as string;

  const [universe, setUniverse] = useState<UniverseMetadataResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      if (!universeId) return;
      try {
        const u = await getUniverse(universeId);
        setUniverse(u);
      } catch (err: unknown) {
        console.error("Failed to load universe dashboard:", err);
        const e = err as { response?: { data?: { detail?: string } } };
        setError(e?.response?.data?.detail || "Universe not found.");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [universeId]);

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete universe '${universeId}'?`)) return;
    try {
      await deleteUniverse(universeId);
      router.push("/");
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center p-12 bg-slate-950">
        <Loader2 className="h-10 w-10 animate-spin text-purple-500" />
      </div>
    );
  }

  if (error || !universe) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center p-8 text-center bg-slate-950">
        <h2 className="text-xl font-bold text-red-400">Universe Not Found</h2>
        <p className="text-sm text-slate-400 mt-2">{error}</p>
        <Link href="/" className="mt-6 rounded-lg bg-slate-800 px-4 py-2 text-xs font-semibold text-slate-200">
          Back to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col bg-slate-950 text-slate-100 p-6 lg:p-12 max-w-6xl mx-auto w-full">
      {/* Dashboard Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-6 mb-8">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="rounded-full bg-purple-950 px-3 py-0.5 text-xs font-semibold text-purple-300 border border-purple-800/40">
              Universe ID: {universe.universe_id}
            </span>
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
          </div>
          <h1 className="text-3xl font-extrabold text-slate-100">{universe.title}</h1>
          <p className="text-xs text-slate-400 mt-1">Reconstructed by {universe.author || "Unknown"}</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleDelete}
            className="flex items-center gap-1.5 rounded-xl border border-red-900/50 bg-red-950/30 px-4 py-2.5 text-xs font-semibold text-red-300 hover:bg-red-900/50 transition-colors"
          >
            <Trash2 className="h-4 w-4" /> Delete Universe
          </button>

          <Link
            href={`/explore/${universe.universe_id}`}
            className="flex items-center gap-2 rounded-xl bg-purple-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-purple-500 transition-colors shadow-lg shadow-purple-950/50"
          >
            <Play className="h-4 w-4 fill-white" />
            Enter Interactive Universe
          </Link>
        </div>
      </div>

      {/* Universe Statistics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
        <div className="flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/80 p-6">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-950 text-purple-400 border border-purple-800/50">
            <Users className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-2xl font-extrabold text-slate-100">{universe.characters_count || 0}</h3>
            <p className="text-xs text-slate-400 font-medium">Reconstructed Characters</p>
          </div>
        </div>

        <div className="flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/80 p-6">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-950 text-blue-400 border border-blue-800/50">
            <MapPin className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-2xl font-extrabold text-slate-100">{universe.locations_count || 0}</h3>
            <p className="text-xs text-slate-400 font-medium">Living Locations</p>
          </div>
        </div>

        <div className="flex items-center gap-4 rounded-xl border border-slate-800 bg-slate-900/80 p-6">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-950 text-amber-400 border border-amber-800/50">
            <Calendar className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100">
              {universe.created_at ? new Date(universe.created_at).toLocaleDateString() : "Recent"}
            </h3>
            <p className="text-xs text-slate-400 font-medium">Compilation Date</p>
          </div>
        </div>
      </div>

      {/* Universe Architecture Overview */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-2">
          <Compass className="h-4 w-4 text-purple-400" /> Universe Simulation Specifications
        </h3>
        <ul className="text-xs text-slate-300 space-y-2 list-disc list-inside">
          <li>Immutable canonical universe model stored under strict Headcanon schema rules.</li>
          <li>Dynamic runtime WorldState managing character positions, relationship scores, and inventories.</li>
          <li>Deterministic simulation consequences applying world updates without modifying original story history.</li>
        </ul>
      </div>
    </div>
  );
}
