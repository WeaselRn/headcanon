import type { Scene } from "./scene";
import type { StoryMetadata } from "./metadata";

export interface Story {
  story_id: string;
  title: string;
  universe: string;
  character_name: string;
  role: string;
  mood: string;
  story: string;
  scenes: Scene[];
  metadata: StoryMetadata;
}

export interface StoryCard {
  story_id: string;
  title: string;
  thumbnail: string;
}

export interface GenerationRequest {
  universe: string;
  character_name: string;
  role: string;
  mood: string;
  prompt: string;
}

export interface ContinueStoryRequest {
  prompt: string;
}

export interface RegenerateSceneRequest {
  scene_number: number;
}
