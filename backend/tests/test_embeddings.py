
import asyncio

from app.llm.embedding_registry import (
    get_embedding_provider,
)


def test_embedding_dimensions():

    provider = get_embedding_provider()

    embeddings = asyncio.run(
        provider.embed([
            "RAG combines retrieval and generation."
        ])
    )

    assert len(embeddings) == 1
    assert len(embeddings[0]) == 768
