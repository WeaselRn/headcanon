"use client";

import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";
import type { UniverseMetadataResponse } from "@/types/universe";
import type { Scene } from "@/types/scene";
import type { InteractionResult } from "@/types/interaction";
import type { AssetMetadata } from "@/types/media";
import type { Snapshot, WorldState } from "@/types/world";
import * as api from "@/lib/api";

interface HeadcanonContextType {
  universe: UniverseMetadataResponse | null;
  worldState: WorldState | null;
  scene: Scene | null;
  selectedCharacterId: string | null;
  selectedLocationId: string | null;
  snapshots: Snapshot[];
  mediaAssets: AssetMetadata[];
  history: InteractionResult[];
  isLoading: boolean;
  loadingMessage: string;
  error: string | null;
  
  // Actions
  loadUniverse: (universeId: string) => Promise<void>;
  executeAction: (userInput: string) => Promise<void>;
  travelToLocation: (locationId: string) => Promise<void>;
  generateCurrentSceneMedia: () => Promise<void>;
  takeSnapshot: (description?: string) => Promise<void>;
  restoreSnapshotState: (snapshotId: string) => Promise<void>;
  setSelectedCharacterId: (characterId: string | null) => void;
  clearError: () => void;
}

const HeadcanonContext = createContext<HeadcanonContextType | undefined>(undefined);

export function HeadcanonProvider({ children }: { children: ReactNode }) {
  const [universe, setUniverse] = useState<UniverseMetadataResponse | null>(null);
  const [worldState, setWorldState] = useState<WorldState | null>(null);
  const [scene, setScene] = useState<Scene | null>(null);
  const [selectedCharacterId, setSelectedCharacterId] = useState<string | null>(null);
  const [selectedLocationId, setSelectedLocationId] = useState<string | null>(null);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [mediaAssets, setMediaAssets] = useState<AssetMetadata[]>([]);
  const [history, setHistory] = useState<InteractionResult[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [loadingMessage, setLoadingMessage] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const clearError = useCallback(() => setError(null), []);

  /**
   * Load active Universe, initial Scene, and Snapshots.
   */
  const loadUniverse = useCallback(async (universeId: string) => {
    setIsLoading(true);
    setLoadingMessage("Entering universe...");
    setError(null);
    try {
      const uMeta = await api.getUniverse(universeId);
      setUniverse(uMeta);

      const initialScene = await api.getScene(universeId);
      setScene(initialScene);
      setSelectedLocationId(initialScene.location.location_id);

      const snapList = await api.listSnapshots(universeId);
      setSnapshots(snapList);
    } catch (err: any) {
      console.error("Failed to load universe:", err);
      setError(err?.response?.data?.detail || err.message || "Failed to load universe.");
    } finally {
      setIsLoading(false);
      setLoadingMessage("");
    }
  }, []);

  /**
   * Complete Scene Refresh Flow:
   * User Action -> POST /interact -> POST /simulate -> Refresh Scene
   */
  const executeAction = useCallback(
    async (userInput: string) => {
      if (!universe) return;
      setIsLoading(true);
      setLoadingMessage("Processing action...");
      setError(null);
      try {
        // Step 1: Interaction Engine (intent parsing & pending effects)
        const interactionRes = await api.interact(universe.universe_id, userInput);
        setHistory((prev) => [interactionRes, ...prev]);

        // Step 2: Simulation Engine (apply consequences & update WorldState)
        setLoadingMessage("Simulating world consequences...");
        const simRes = await api.simulate(universe.universe_id, interactionRes);
        setWorldState(simRes.world_state);

        // Step 3: Refresh Scene
        setLoadingMessage("Updating scene...");
        const newLocationId =
          simRes.world_state.characters["char_user"]?.location || selectedLocationId || undefined;
        const refreshedScene = await api.refreshScene(universe.universe_id, newLocationId);
        setScene(refreshedScene);
        if (newLocationId) setSelectedLocationId(newLocationId);
      } catch (err: any) {
        console.error("Action execution failed:", err);
        setError(err?.response?.data?.detail || err.message || "Action execution failed.");
      } finally {
        setIsLoading(false);
        setLoadingMessage("");
      }
    },
    [universe, selectedLocationId]
  );

  /**
   * Travel to a connected location.
   */
  const travelToLocation = useCallback(
    async (targetLocationId: string) => {
      await executeAction(`Go to ${targetLocationId}`);
    },
    [executeAction]
  );

  /**
   * Trigger optional media pipeline generation for current scene.
   */
  const generateCurrentSceneMedia = useCallback(async () => {
    if (!universe || !scene) return;
    setIsLoading(true);
    setLoadingMessage("Generating scene media assets...");
    setError(null);
    try {
      const mediaRes = await api.generateMedia(universe.universe_id, scene);
      if (mediaRes.media) {
        setScene((prev) => (prev ? { ...prev, media: mediaRes.media } : prev));
      }
      if (mediaRes.asset_metadata) {
        setMediaAssets((prev) => [...mediaRes.asset_metadata, ...prev]);
      }
    } catch (err: any) {
      console.error("Media generation failed:", err);
      setError("Media generation failed.");
    } finally {
      setIsLoading(false);
      setLoadingMessage("");
    }
  }, [universe, scene]);

  /**
   * Create point-in-time snapshot.
   */
  const takeSnapshot = useCallback(
    async (description?: string) => {
      if (!universe) return;
      try {
        const newSnap = await api.createSnapshot(universe.universe_id, description);
        setSnapshots((prev) => [newSnap, ...prev]);
      } catch (err: any) {
        console.error("Failed to create snapshot:", err);
        setError("Failed to create snapshot.");
      }
    },
    [universe]
  );

  /**
   * Restore past snapshot.
   */
  const restoreSnapshotState = useCallback(
    async (snapshotId: string) => {
      if (!universe) return;
      setIsLoading(true);
      setLoadingMessage("Restoring snapshot...");
      try {
        const restoredSnap = await api.restoreSnapshot(universe.universe_id, snapshotId);
        setWorldState(restoredSnap.world_state);
        const refreshedScene = await api.refreshScene(universe.universe_id);
        setScene(refreshedScene);
      } catch (err: any) {
        console.error("Snapshot restoration failed:", err);
        setError("Snapshot restoration failed.");
      } finally {
        setIsLoading(false);
        setLoadingMessage("");
      }
    },
    [universe]
  );

  return (
    <HeadcanonContext.Provider
      value={{
        universe,
        worldState,
        scene,
        selectedCharacterId,
        selectedLocationId,
        snapshots,
        mediaAssets,
        history,
        isLoading,
        loadingMessage,
        error,
        loadUniverse,
        executeAction,
        travelToLocation,
        generateCurrentSceneMedia,
        takeSnapshot,
        restoreSnapshotState,
        setSelectedCharacterId,
        clearError,
      }}
    >
      {children}
    </HeadcanonContext.Provider>
  );
}

export function useHeadcanon() {
  const context = useContext(HeadcanonContext);
  if (!context) {
    throw new Error("useHeadcanon must be used within a HeadcanonProvider");
  }
  return context;
}
