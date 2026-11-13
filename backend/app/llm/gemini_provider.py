import time

from google import genai
from google.genai import types

from app.core.config import settings


class GeminiProvider:

    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("Gemini API key is not configured.")

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options=types.HttpOptions(
                api_version="v1beta"
            )
        )

        self.model = settings.GEMINI_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None
    ) -> dict:

        start = time.perf_counter()

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.2,
                ),
            )

        except Exception as exc:
            raise RuntimeError(
                f"Gemini request failed: {type(exc).__name__}"
            ) from exc

        latency_ms = round(
            (time.perf_counter() - start) * 1000,
            2
        )

        answer = response.text

        if not answer:
            raise RuntimeError("Gemini returned an empty response.")

        usage = response.usage_metadata

        return {
            "answer": answer,
            "provider": "gemini",
            "model": self.model,
            "latency_ms": latency_ms,
            "input_tokens": (
                usage.prompt_token_count if usage else None
            ),
            "output_tokens": (
                usage.candidates_token_count if usage else None
            ),
        }