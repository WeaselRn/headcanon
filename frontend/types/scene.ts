import { WorldTime } from "./world";

export interface SceneLocationSummary {
  location_id: string;
  name: string;
  category: string;
  description: string;
  connected_locations: string[];
}

export interface SceneCharacterSummary {
  character_id: string;
  name: string;
  role: string;
  emotion: string;
  relationship_score: number;
  relationship_label: string;
  is_interacting: boolean;
}

export interface SceneObjectSummary {
  object_id: string;
  name: string;
  category: string;
  is_interactive: boolean;
}

export interface SceneEnvironment {
  time: WorldTime;
  atmosphere: string;
  sensory_details: string[];
}

export interface SceneMediaAssets {
  illustration_url?: string | null;
  narration_url?: string | null;
  ambient_audio_tags: string[];
}

export interface SceneMetadata {
  generation_time: string;
  version: string;
}

export interface Scene {
  scene_id: string;
  universe_id: string;
  location: SceneLocationSummary;
  narration: string;
  characters: SceneCharacterSummary[];
  objects: SceneObjectSummary[];
  environment: SceneEnvironment;
  available_actions: string[];
  suggested_actions: string[];
  media: SceneMediaAssets;
  metadata: SceneMetadata;
}

export interface GetSceneRequest {
  universe_id: string;
  location_id?: string;
  user_character_id?: string;
}

export interface RefreshSceneRequest {
  universe_id: string;
  location_id?: string;
  user_character_id?: string;
}

export interface SceneResponse {
  scene: Scene;
}
