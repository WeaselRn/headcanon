"use client";

import { useState } from "react";
import type { Story } from "@/types/story";

export interface UseStoryState {
  story: Story | null;
  loading: boolean;
  error: string | null;
}

export function useStory(_storyId: string): UseStoryState {
  const [story] = useState<Story | null>(null);
  const [loading] = useState(false);
  const [error] = useState<string | null>(null);

  return { story, loading, error };
}
