from pydantic import BaseModel


class Scene(BaseModel):
    scene_number: int
    title: str
    description: str
    image_prompt: str
    image_url: str
