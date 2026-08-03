"""
Headcanon FastAPI Application Main Entry Point.

Reference: docs/runtime_pipeline.md, docs/error_handling.md
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.api.routes.health import router as health_router
from app.config.logging import configure_logging
from app.config.settings import get_settings

settings = get_settings()
configure_logging(debug=settings.debug)

app = FastAPI(
    title="Headcanon Engine API",
    version=settings.app_version,
    description=(
        "Persistent Fictional Universe Simulation Engine API. Reconstructs universes, "
        "simulates world state evolution, manages character reasoning, and generates "
        "explorable scenes and multimedia assets."
    ),
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Health check endpoint
app.include_router(health_router)

# Main API router (/api/...)
app.include_router(api_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle explicit HTTP exceptions without exposing internal details."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request schema validation errors cleanly."""
    return JSONResponse(
        status_code=422,
        content={"error": "Validation Error", "detail": str(exc)},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all exception handler preventing stack trace leaks."""
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"},
    )
