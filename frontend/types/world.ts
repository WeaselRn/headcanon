export interface WorldTime {
  day: number;
  hour: number;
  minute: number;
  season: string;
}

export interface CharacterState {
  character_id: string;
  location?: string | null;
  emotion: string;
  emotion_intensity: number;
  status: string;
  activity?: string | null;
  inventory: string[];
  memories_count: number;
}

export interface LocationState {
  location_id: string;
  occupants: string[];
  items: string[];
  atmosphere?: string | null;
  is_locked: boolean;
}

export interface RelationshipState {
  source_character_id: string;
  target_character_id: string;
  score: number;
  trust_level: number;
  perceived_type: string;
  last_updated_time?: WorldTime;
}

export interface WorldState {
  universe_id: string;
  time: WorldTime;
  active_branch_id: string;
  characters: Record<string, CharacterState>;
  locations: Record<string, LocationState>;
  relationships: Record<string, RelationshipState>;
  global_flags: Record<string, boolean>;
}

export interface Character {
  id: string;
  name: string;
  aliases: string[];
  role: string;
  summary: string;
  personality: {
    traits: string[];
  };
  speech: {
    tone?: string;
  };
}

export interface Location {
  id: string;
  name: string;
  category: string;
  description: string;
  connected_locations: string[];
}

export interface Snapshot {
  snapshot_id: string;
  universe_id: string;
  world_state: WorldState;
  metadata: {
    created_at: string;
    world_state_version: number;
    description?: string;
  };
}
