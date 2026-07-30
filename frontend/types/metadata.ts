export interface StoryMetadata {
  created_at: string;
  updated_at: string;
  models: string[];
  pipeline_version: string;
}

export interface Provenance {
  execution_id: string;
  pipeline_version: string;
  models_used: string[];
  started_at: string;
  completed_at: string;
  assets_generated: string[];
}
