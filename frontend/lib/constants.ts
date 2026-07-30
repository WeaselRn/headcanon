export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const STORY_MOODS = [
  "Dark",
  "Adventurous",
  "Romantic",
  "Mysterious",
  "Comedic",
  "Epic",
  "Melancholic",
] as const;

export const PIPELINE_VERSION = "v1";
