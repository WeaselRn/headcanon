"""
Headcanon Main API Router.

Includes endpoints for Universe, Scene, Interaction, Simulation, Media, and Storage APIs.
Retains legacy story endpoints marked as deprecated.

Reference: docs/runtime_pipeline.md
"""

from fastapi import APIRouter

from app.api.routes import (
    interaction,
    media,
    scene,
    simulation,
    storage,
    stories,
    universes,
)

api_router = APIRouter(prefix="/api")

# Universe & Simulation Engine API endpoints
api_router.include_router(universes.router)
api_router.include_router(scene.router)
api_router.include_router(interaction.router)
api_router.include_router(simulation.router)
api_router.include_router(media.router)
api_router.include_router(storage.router)

# Legacy Story API endpoints (retained for backwards compatibility, marked deprecated)
api_router.include_router(stories.router, deprecated=True)
