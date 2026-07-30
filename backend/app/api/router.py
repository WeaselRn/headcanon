from fastapi import APIRouter

from app.api.routes import stories

api_router = APIRouter(prefix="/api")

api_router.include_router(stories.router)
