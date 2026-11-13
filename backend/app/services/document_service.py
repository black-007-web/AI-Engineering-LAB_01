
import httpx

from app.core.config import settings


def get_headers(access_token: str) -> dict:
    return {
        "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
        "Authorization": f"Bearer {access_token}",
    }


async def get_document(
    document_id: str,
    access_token: str,
) -> dict | None:
    """
    Retrieve one document using the current user's JWT.
    Supabase RLS controls which documents the user can access.
    """

    url = f"{settings.SUPABASE_URL}/rest/v1/documents"

    params = {
        "select": "id,title,status,owner_id,original_filename,chunk_count",
        "id": f"eq.{document_id}",
        "limit": "1",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            url,
            headers=get_headers(access_token),
            params=params,
        )

        response.raise_for_status()
        documents = response.json()

    if not documents:
        return None

    return documents[0]


async def get_document_chunks(
    document_id: str,
    access_token: str,
) -> list[dict]:
    """
    Retrieve the indexed chunks for a document.
    Supabase RLS ensures the user can only access permitted rows.
    """

    url = f"{settings.SUPABASE_URL}/rest/v1/document_chunks"

    params = {
        "select": "id,document_id,chunk_index,content,metadata",
        "document_id": f"eq.{document_id}",
        "order": "chunk_index.asc",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            url,
            headers=get_headers(access_token),
            params=params,
        )

        response.raise_for_status()
        chunks = response.json()

    return chunks
