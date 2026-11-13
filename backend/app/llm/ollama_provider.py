import time
import httpx

from app.core.config import settings


class OllamaProvider:

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None
    ) -> dict:

        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_ctx": 2048
            }
        }

        start_time = time.perf_counter()

        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                )

                response.raise_for_status()
                data = response.json()

        except httpx.TimeoutException as exc:
            raise RuntimeError("Ollama request timed out.") from exc

        except httpx.RequestError as exc:
            raise RuntimeError(
                "Cannot connect to Ollama. Check whether it is running."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Ollama returned HTTP {exc.response.status_code}."
            ) from exc

        elapsed_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        answer = data.get("message", {}).get("content")

        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError("Ollama returned an empty response.")

        return {
            "answer": answer,
            "provider": "ollama",
            "model": self.model,
            "latency_ms": elapsed_ms,
            "input_tokens": data.get("prompt_eval_count"),
            "output_tokens": data.get("eval_count"),
            "total_duration_ns": data.get("total_duration")
        }