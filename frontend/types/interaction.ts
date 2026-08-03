import { Scene } from "./scene";

export interface ParsedAction {
  action_type: string;
  target_id?: string | null;
  parameters: Record<string, unknown>;
  raw_input: string;
}

export interface InteractionResult {
  interaction_id: string;
  action: string;
  target?: string | null;
  narration: string;
  character_dialogue?: Record<string, string> | null;
  scene: Scene;
  pending_world_effects: Record<string, unknown>[];
  success: boolean;
  error_message?: string | null;
}

export interface InteractionRequest {
  universe_id: string;
  user_input: string;
  user_character_id?: string;
}

export interface InteractionResponse {
  interaction_result: InteractionResult;
}
