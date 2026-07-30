import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_pipeline_service, get_story_service
from app.models.story import StoryCard
from app.schemas.generation import (
    ContinueStoryRequest,
    GenerationRequest,
    RegenerateSceneRequest,
)
from app.schemas.responses import (
    ErrorResponse,
    RegenerateSceneResponse,
    StoryResponse,
)
from app.services.pipeline_service import PipelineService
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
    pipeline_service: PipelineService = Depends(get_pipeline_service),
) -> StoryResponse:
    try:
        story = pipeline_service.run(request)
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
    response_model=list[StoryCard],
    responses={500: {"model": ErrorResponse}},
)
def list_stories(
    service: StoryService = Depends(get_story_service),
) -> list[StoryCard]:
    try:
        return service.list_stories()
    except Exception as exc:
        logger.exception("Unexpected error listing stories")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


@router.get(
    "/{story_id}",
    response_model=StoryResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def get_story(
    story_id: str,
    service: StoryService = Depends(get_story_service),
) -> StoryResponse:
    try:
        story = service.get_story(story_id)
        return StoryResponse.model_validate(story.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Story not found"
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error getting story %s", story_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc


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
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def delete_story(
    story_id: str,
    service: StoryService = Depends(get_story_service),
) -> None:
    try:
        service.delete_story(story_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Story not found"
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error deleting story %s", story_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc
