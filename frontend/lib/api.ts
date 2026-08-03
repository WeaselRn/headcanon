import axios from "axios";
import type {
  ImportUniverseRequest,
  ImportUniverseResponse,
  UniverseMetadataResponse,
} from "@/types/universe";
import type { Scene } from "@/types/scene";
import type { InteractionResult } from "@/types/interaction";
import type { SimulationResult } from "@/types/simulation";
import type { AssetMetadata, MediaPipelineResult } from "@/types/media";
import type { Snapshot, WorldState } from "@/types/world";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
});

/**
 * Import raw story text or file and compile a persistent Universe.
 */
export async function importUniverse(
  payload: ImportUniverseRequest
): Promise<ImportUniverseResponse> {
  const res = await apiClient.post<ImportUniverseResponse>(
    "/api/universes/import",
    payload
  );
  return res.data;
}

/**
 * Get Universe metadata summary by ID.
 */
export async function getUniverse(
  universeId: string
): Promise<UniverseMetadataResponse> {
  const res = await apiClient.get<UniverseMetadataResponse>(
    `/api/universes/${universeId}`
  );
  return res.data;
}

/**
 * List all available persistent universes.
 */
export async function listUniverses(): Promise<UniverseMetadataResponse[]> {
  const res = await apiClient.get<
    { universes: UniverseMetadataResponse[] } | UniverseMetadataResponse[]
  >("/api/universes");
  if (Array.isArray(res.data)) {
    return res.data;
  }
  return res.data?.universes || [];
}

/**
 * Delete a universe by ID.
 */
export async function deleteUniverse(universeId: string): Promise<void> {
  await apiClient.delete(`/api/universes/${universeId}`);
}

/**
 * Get the UI-ready Scene for the active location.
 */
export async function getScene(
  universeId: string,
  locationId?: string,
  userCharacterId: string = "char_user"
): Promise<Scene> {
  const params: Record<string, string> = { universe_id: universeId, user_character_id: userCharacterId };
  if (locationId) params.location_id = locationId;

  const res = await apiClient.get<{ scene: Scene }>("/api/scene", { params });
  return res.data.scene;
}

/**
 * Rebuild/refresh current Scene.
 */
export async function refreshScene(
  universeId: string,
  locationId?: string,
  userCharacterId: string = "char_user"
): Promise<Scene> {
  const res = await apiClient.post<{ scene: Scene }>("/api/scene/refresh", {
    universe_id: universeId,
    location_id: locationId,
    user_character_id: userCharacterId,
  });
  return res.data.scene;
}

/**
 * Process a user interaction action (read-only intent parsing).
 */
export async function interact(
  universeId: string,
  userInput: string,
  userCharacterId: string = "char_user"
): Promise<InteractionResult> {
  const res = await apiClient.post<{ interaction_result: InteractionResult }>(
    "/api/interact",
    {
      universe_id: universeId,
      user_input: userInput,
      user_character_id: userCharacterId,
    }
  );
  return res.data.interaction_result;
}

/**
 * Simulate pending interaction consequences and persist updated WorldState.
 */
export async function simulate(
  universeId: string,
  interactionResult: InteractionResult,
  userCharacterId: string = "char_user"
): Promise<{ simulation_result: SimulationResult; world_state: WorldState }> {
  const res = await apiClient.post<{
    simulation_result: SimulationResult;
    world_state: WorldState;
  }>("/api/simulate", {
    universe_id: universeId,
    interaction_result: interactionResult,
    user_character_id: userCharacterId,
  });
  return res.data;
}

/**
 * Generate narration, illustration, and ambient audio metadata for a Scene.
 */
export async function generateMedia(
  universeId: string,
  scene: Scene
): Promise<MediaPipelineResult> {
  const res = await apiClient.post<{ result: MediaPipelineResult }>(
    "/api/media/generate",
    {
      universe_id: universeId,
      scene: scene,
    }
  );
  return res.data.result;
}

/**
 * Get media asset metadata by ID.
 */
export async function getAssetMetadata(assetId: string): Promise<AssetMetadata> {
  const res = await apiClient.get<{ asset_metadata: AssetMetadata }>(
    `/api/media/${assetId}`
  );
  return res.data.asset_metadata;
}

/**
 * Create a point-in-time WorldState snapshot.
 */
export async function createSnapshot(
  universeId: string,
  description?: string
): Promise<Snapshot> {
  const res = await apiClient.post<{ snapshot: Snapshot }>("/api/snapshot", {
    universe_id: universeId,
    description: description || "",
  });
  return res.data.snapshot;
}

/**
 * Restore a point-in-time snapshot as the active WorldState.
 */
export async function restoreSnapshot(
  universeId: string,
  snapshotId: string
): Promise<Snapshot> {
  const res = await apiClient.post<{ snapshot: Snapshot }>("/api/restore", {
    universe_id: universeId,
    snapshot_id: snapshotId,
  });
  return res.data.snapshot;
}

/**
 * List all saved snapshots for a universe.
 */
export async function listSnapshots(universeId: string): Promise<Snapshot[]> {
  const res = await apiClient.get<{ snapshots: Snapshot[] }>("/api/snapshots", {
    params: { universe_id: universeId },
  });
  return res.data.snapshots || [];
}
