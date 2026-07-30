import type {
  ContinueStoryRequest,
  GenerationRequest,
  RegenerateSceneRequest,
  Story,
  StoryCard,
} from "@/types/story";
import type { RegenerateSceneResponse } from "@/types/api";

export async function createStory(_request: GenerationRequest): Promise<Story> {
  throw new Error("Not implemented");
}

export async function listStories(): Promise<StoryCard[]> {
  throw new Error("Not implemented");
}

export async function getStory(_storyId: string): Promise<Story> {
  throw new Error("Not implemented");
}

export async function continueStory(
  _storyId: string,
  _request: ContinueStoryRequest
): Promise<Story> {
  throw new Error("Not implemented");
}

export async function regenerateScene(
  _storyId: string,
  _request: RegenerateSceneRequest
): Promise<RegenerateSceneResponse> {
  throw new Error("Not implemented");
}

export async function deleteStory(_storyId: string): Promise<void> {
  throw new Error("Not implemented");
}
