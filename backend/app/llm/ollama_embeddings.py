
import httpx

from app.core.config import settings


class OllamaEmbeddingProvider:

    def __init__(self):

        self.base_url = (
            settings.OLLAMA_BASE_URL.rstrip("/")
        )

        self.model = settings.OLLAMA_EMBED_MODEL

        self.dimensions = 768

    async def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        payload = {
            "model": self.model,
            "input": texts,
        }

        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            response = await client.post(
                f"{self.base_url}/api/embed",
                json=payload,
            )

            response.raise_for_status()

            data = response.json()

        embeddings = data.get("embeddings", [])

        if len(embeddings) != len(texts):
            raise RuntimeError(
                "Embedding count does not match input count."
            )

        for vector in embeddings:

            if len(vector) != self.dimensions:
                raise RuntimeError(
                    "Unexpected embedding dimensions."
                )

        return embeddings
