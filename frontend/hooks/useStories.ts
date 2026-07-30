"use client";

import { useState } from "react";
import type { StoryCard } from "@/types/story";

export interface UseStoriesState {
  stories: StoryCard[];
  loading: boolean;
  error: string | null;
}

export function useStories(): UseStoriesState {
  const [stories] = useState<StoryCard[]>([]);
  const [loading] = useState(false);
  const [error] = useState<string | null>(null);

  return { stories, loading, error };
}
