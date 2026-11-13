
from app.core.config import settings
from app.llm.embedding_registry import get_embedding_provider


async def retrieve_chunks(
    question: str,
    access_token: str,
    document_id: str | None = None,
    top_k: int = 5,
) -> list[dict]:

    if not question.strip():
        raise ValueError("Question cannot be empty.")

    top_k = max(1, min(top_k, 20))

    embedding_provider = get_embedding_provider("ollama")

    query_embeddings = await embedding_provider.embed(
        [question]
    )

    query_embedding = query_embeddings[0]

    headers = {
        "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "query_embedding": query_embedding,
        "match_count": top_k,
        "filter_owner_id": None,
        "filter_document_id": document_id,
    }

    import httpx

    async with httpx.AsyncClient(timeout=60.0) as client:

        response = await client.post(
            f"{settings.SUPABASE_URL}/rest/v1/rpc/match_document_chunks",
            headers=headers,
            json=payload,
        )

        response.raise_for_status()

        results = response.json()

    return results
