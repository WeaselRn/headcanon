from pydantic import BaseModel


class GenerationRequest(BaseModel):
    universe: str
    character_name: str
    role: str
    mood: str
    prompt: str


class ContinueStoryRequest(BaseModel):
    prompt: str


class RegenerateSceneRequest(BaseModel):
    scene_number: int
