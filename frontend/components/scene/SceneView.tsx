"use client";

import React, { useState } from "react";
import { useHeadcanon } from "@/lib/store";
import SceneImage from "./SceneImage";
import SceneNarration from "./SceneNarration";
import CharacterPanel from "@/components/character/CharacterPanel";
import RelationshipGraph from "@/components/character/RelationshipGraph";
import ActionBar from "@/components/action/ActionBar";
import ActionSuggestions from "@/components/action/ActionSuggestions";
import NavigationPanel from "@/components/navigation/NavigationPanel";
import WorldMap from "@/components/navigation/WorldMap";
import InventoryPanel from "@/components/inventory/InventoryPanel";
import JournalPanel from "@/components/journal/JournalPanel";
import SnapshotPanel from "@/components/storage/SnapshotPanel";
import LoadingOverlay from "@/components/ui/LoadingOverlay";
import { Compass, BookOpen, Layers, Settings, ShieldAlert } from "lucide-react";
import Link from "next/link";

export default function SceneView() {
  const {
    universe,
    worldState,
    scene,
    selectedCharacterId,
    history,
    snapshots,
    isLoading,
    loadingMessage,
    error,
    executeAction,
    travelToLocation,
    generateCurrentSceneMedia,
    takeSnapshot,
    restoreSnapshotState,
    setSelectedCharacterId,
    clearError,
  } = useHeadcanon();

  const [leftTab, setLeftTab] = useState<"navigation" | "inventory" | "map">("navigation");
  const [rightTab, setRightTab] = useState<"characters" | "relationships" | "snapshots">("characters");

  if (!scene) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center p-8 text-center bg-slate-950">
        <Compass className="h-12 w-12 text-slate-700 animate-pulse mb-4" />
        <h2 className="text-xl font-bold text-slate-200">No Active Scene Loaded</h2>
        <p className="text-sm text-slate-400 max-w-md mt-2">
          Select or import a universe to enter the living world simulation.
        </p>
        <Link
          href="/import"
          className="mt-6 rounded-xl bg-purple-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-purple-500 transition-colors shadow-lg"
        >
          Import Universe
        </Link>
      </div>
    );
  }

  const activeCharState = worldState?.characters["char_user"];
  const userInventory = activeCharState?.inventory || [];

  return (
    <div className="relative flex flex-1 flex-col bg-slate-950 text-slate-100 min-h-screen">
      <LoadingOverlay isLoading={isLoading} message={loadingMessage} />

      {/* Top Header Bar */}
      <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-900/90 px-6 backdrop-blur-md sticky top-0 z-30">
        <div className="flex items-center gap-3">
          <Link href="/" className="font-bold text-purple-400 hover:text-purple-300 transition-colors">
            Headcanon
          </Link>
          <span className="text-slate-600">/</span>
          <span className="text-sm font-semibold text-slate-200">{universe?.title || "Universe"}</span>
          <span className="rounded-full bg-slate-800 px-2.5 py-0.5 text-xs text-slate-400 border border-slate-700">
            {scene.location.name}
          </span>
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-400">
          <div className="flex items-center gap-1.5 font-medium text-amber-300 bg-amber-950/40 px-3 py-1 rounded-md border border-amber-800/40">
            <span>Day {scene.environment.time.day}</span>
            <span>•</span>
            <span>
              {scene.environment.time.hour.toString().padStart(2, "0")}:
              {scene.environment.time.minute.toString().padStart(2, "0")}
            </span>
          </div>

          <Link
            href="/settings"
            className="flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-900 px-3 py-1.5 text-slate-300 hover:bg-slate-800 transition-colors"
          >
            <Settings className="h-3.5 w-3.5" />
            Settings
          </Link>
        </div>
      </header>

      {/* Error Alert */}
      {error && (
        <div className="flex items-center justify-between bg-red-950/90 border-b border-red-800 px-6 py-2.5 text-xs text-red-200">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-red-400" />
            <span>{error}</span>
          </div>
          <button onClick={clearError} className="underline hover:text-white">
            Dismiss
          </button>
        </div>
      )}

      {/* Main 5-Panel Grid Layout */}
      <div className="flex-1 p-4 lg:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Sidebar (Cols 1-3) */}
        <aside className="lg:col-span-3 flex flex-col gap-4">
          <div className="flex rounded-xl border border-slate-800 bg-slate-900/60 p-1">
            <button
              onClick={() => setLeftTab("navigation")}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                leftTab === "navigation"
                  ? "bg-purple-950 text-purple-300 border border-purple-800/50"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Navigation
            </button>
            <button
              onClick={() => setLeftTab("inventory")}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                leftTab === "inventory"
                  ? "bg-purple-950 text-purple-300 border border-purple-800/50"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Inventory
            </button>
            <button
              onClick={() => setLeftTab("map")}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                leftTab === "map"
                  ? "bg-purple-950 text-purple-300 border border-purple-800/50"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Map
            </button>
          </div>

          {leftTab === "navigation" && (
            <NavigationPanel
              location={scene.location}
              universeTitle={universe?.title}
              onTravel={travelToLocation}
              disabled={isLoading}
            />
          )}

          {leftTab === "inventory" && (
            <InventoryPanel
              items={userInventory}
              onUseItem={(id) => executeAction(`Use ${id}`)}
              onInspectItem={(id) => executeAction(`Inspect ${id}`)}
              onGiveItem={(id) => executeAction(`Give ${id}`)}
            />
          )}

          {leftTab === "map" && (
            <WorldMap
              currentLocation={scene.location}
              onSelectLocation={travelToLocation}
            />
          )}
        </aside>

        {/* Center Main Panel (Cols 4-9) */}
        <main className="lg:col-span-6 flex flex-col gap-5">
          <SceneImage
            media={scene.media}
            locationName={scene.location.name}
            onGenerateMedia={generateCurrentSceneMedia}
          />

          <SceneNarration scene={scene} />

          <ActionSuggestions
            suggestions={scene.suggested_actions}
            onSelectSuggestion={executeAction}
          />

          <ActionBar onExecuteAction={executeAction} disabled={isLoading} />
        </main>

        {/* Right Sidebar (Cols 10-12) */}
        <aside className="lg:col-span-3 flex flex-col gap-4">
          <div className="flex rounded-xl border border-slate-800 bg-slate-900/60 p-1">
            <button
              onClick={() => setRightTab("characters")}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                rightTab === "characters"
                  ? "bg-purple-950 text-purple-300 border border-purple-800/50"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Characters
            </button>
            <button
              onClick={() => setRightTab("relationships")}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                rightTab === "relationships"
                  ? "bg-purple-950 text-purple-300 border border-purple-800/50"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Matrix
            </button>
            <button
              onClick={() => setRightTab("snapshots")}
              className={`flex-1 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                rightTab === "snapshots"
                  ? "bg-purple-950 text-purple-300 border border-purple-800/50"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Save Points
            </button>
          </div>

          {rightTab === "characters" && (
            <CharacterPanel
              characters={scene.characters}
              selectedCharacterId={selectedCharacterId}
              onSelectCharacter={setSelectedCharacterId}
              onTalkToCharacter={(name) => executeAction(`Talk to ${name}`)}
            />
          )}

          {rightTab === "relationships" && (
            <RelationshipGraph characters={scene.characters} />
          )}

          {rightTab === "snapshots" && (
            <SnapshotPanel
              snapshots={snapshots}
              onCreateSnapshot={takeSnapshot}
              onRestoreSnapshot={restoreSnapshotState}
              disabled={isLoading}
            />
          )}
        </aside>

        {/* Bottom Full-Width Panel: Journal & Timeline */}
        <section className="lg:col-span-12 mt-2">
          <JournalPanel history={history} />
        </section>
      </div>
    </div>
  );
}
