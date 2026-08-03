export interface UniverseMetadata {
  id: string;
  title: string;
  author: string;
  source?: string;
  language?: string;
  created_at?: string;
  schema_version?: string;
  characters_count?: number;
  locations_count?: number;
}

export interface ImportUniverseRequest {
  source_type: "text" | "pdf" | "epub" | "web";
  text?: string;
  file_path?: string;
  url?: string;
  title?: string;
  author?: string;
}

export interface ImportUniverseResponse {
  universe_id: string;
  status: string;
  title: string;
  author: string;
  characters_count: number;
  locations_count: number;
  world_state_version: number;
}

export interface UniverseMetadataResponse {
  universe_id: string;
  title: string;
  author: string;
  created_at?: string;
  characters_count: number;
  locations_count: number;
}

export interface UniverseListResponse {
  universes: UniverseMetadataResponse[];
}
