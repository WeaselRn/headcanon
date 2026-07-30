import logging
from pathlib import Path

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent.parent / "prompts"
_CANDIDATE_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]


class GeminiClient:
    """Thin wrapper around google-genai for text generation."""

    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)

    def generate_text(self, prompt: str) -> str:
        """Send *prompt* to Gemini and return the raw text response."""
        last_exc: Exception | None = None
        for model in _CANDIDATE_MODELS:
            try:
                response = self._client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.9,
                        max_output_tokens=4096,
                        response_mime_type="application/json",
                    ),
                )
                text = response.text
                if text is not None:
                    return text
            except Exception as exc:
                logger.warning("Gemini call failed for model %s: %s", model, exc)
                last_exc = exc

        if last_exc is not None:
            raise last_exc
        raise RuntimeError("Gemini returned an empty response.")

    @staticmethod
    def load_prompt(filename: str) -> str:
        """Load a prompt template from app/prompts/."""
        return (_PROMPT_DIR / filename).read_text(encoding="utf-8")
