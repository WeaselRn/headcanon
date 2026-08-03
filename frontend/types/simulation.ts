import { InteractionResult } from "./interaction";
import { WorldState } from "./world";

export interface SimulationResult {
  simulation_id: string;
  applied_effects: Record<string, unknown>[];
  events_triggered: string[];
  updated_world_state: WorldState;
  success: boolean;
  error_message?: string | null;
}

export interface SimulationRequest {
  universe_id: string;
  interaction_result: InteractionResult;
  user_character_id?: string;
}

export interface SimulationResponse {
  simulation_result: SimulationResult;
  world_state: WorldState;
}
