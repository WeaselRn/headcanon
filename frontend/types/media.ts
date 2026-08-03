import { Scene, SceneMediaAssets } from "./scene";

export interface AmbientAudioMetadata {
  soundscape_category: string;
  intensity: number;
  primary_loop?: string | null;
  ambient_tags: string[];
}

export interface AssetMetadata {
  asset_id: string;
  universe_id: string;
  scene_id: string;
  generation_time: string;
  model_used: string;
  image_url?: string | null;
  audio_url?: string | null;
}

export interface MediaPipelineResult {
  scene_id: string;
  illustration_url?: string | null;
  narration_script?: string | null;
  ambient_audio?: AmbientAudioMetadata | null;
  asset_metadata: AssetMetadata[];
  media: SceneMediaAssets;
  success: boolean;
  error_message?: string | null;
}

export interface MediaGenerationRequest {
  universe_id: string;
  scene: Scene;
}

export interface MediaGenerationResponse {
  result: MediaPipelineResult;
}

export interface AssetMetadataResponse {
  asset_metadata: AssetMetadata;
}
