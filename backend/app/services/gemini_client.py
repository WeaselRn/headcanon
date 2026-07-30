import logging
from pathlib import Path

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent.parent / "prompts"
_GEMINI_MODEL = "gemini-2.0-flash"


class GeminiClient:
    """Thin wrapper around google-genai for text generation."""

    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)

    def generate_text(self, prompt: str) -> str:
        """Send *prompt* to Gemini and return the raw text response."""
        response = self._client.models.generate_content(
            model=_GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.9,
                max_output_tokens=4096,
            ),
        )
        text = response.text
        if text is None:
            raise RuntimeError("Gemini returned an empty response.")
        return text

    @staticmethod
    def load_prompt(filename: str) -> str:
        """Load a prompt template from app/prompts/."""
        return (_PROMPT_DIR / filename).read_text(encoding="utf-8")
