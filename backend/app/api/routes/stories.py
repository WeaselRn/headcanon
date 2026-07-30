import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_story_service
from app.schemas.generation import (
    ContinueStoryRequest,
    GenerationRequest,
    RegenerateSceneRequest,
)
from app.schemas.responses import (
    ErrorResponse,
    RegenerateSceneResponse,
    StoryListResponse,
    StoryResponse,
)
from app.services.story_service import StoryService

router = APIRouter(prefix="/stories", tags=["stories"])

logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=StoryResponse,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def create_story(
    request: GenerationRequest,
    service: StoryService = Depends(get_story_service),
) -> StoryResponse:
    try:
        story = service.generate(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during story generation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
    return StoryResponse.model_validate(story.model_dump())


@router.get(
    "",
    response_model=StoryListResponse,
    responses={500: {"model": ErrorResponse}},
)
def list_stories() -> StoryListResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get(
    "/{story_id}",
    response_model=StoryResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_story(story_id: str) -> StoryResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post(
    "/{story_id}/continue",
    response_model=StoryResponse,
    responses={404: {"model": ErrorResponse}},
)
def continue_story(story_id: str, request: ContinueStoryRequest) -> StoryResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post(
    "/{story_id}/regenerate-scene",
    response_model=RegenerateSceneResponse,
    responses={404: {"model": ErrorResponse}},
)
def regenerate_scene(story_id: str, request: RegenerateSceneRequest) -> RegenerateSceneResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.delete(
    "/{story_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
def delete_story(story_id: str) -> None:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
