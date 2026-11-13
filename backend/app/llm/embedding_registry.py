
from app.llm.ollama_embeddings import (
    OllamaEmbeddingProvider,
)


def get_embedding_provider(
    provider_name: str = "ollama",
):

    if provider_name == "ollama":
        return OllamaEmbeddingProvider()

    raise ValueError(
        f"Unsupported embedding provider: {provider_name}"
    )
