
import httpx

from app.core.config import settings


BUCKET = "knowledge-documents"


async def upload_to_storage(
    access_token: str,
    storage_path: str,
    content: bytes,
    mime_type: str,
) -> None:

    url = (
        f"{settings.SUPABASE_URL}/storage/v1/object/"
        f"{BUCKET}/{storage_path}"
    )

    headers = {
        "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": mime_type,
        "x-upsert": "false",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            headers=headers,
            content=content,
        )

        response.raise_for_status()


async def delete_from_storage(
    access_token: str,
    storage_path: str,
) -> None:

    url = (
        f"{settings.SUPABASE_URL}/storage/v1/object/"
        f"{BUCKET}/{storage_path}"
    )

    headers = {
        "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
        "Authorization": f"Bearer {access_token}",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.delete(
            url,
            headers=headers,
        )

        response.raise_for_status()
