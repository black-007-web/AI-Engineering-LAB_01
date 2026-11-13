import httpx
from app.core.config import settings


def get_user_headers(access_token: str) -> dict:
    return {
        "apikey": settings.SUPABASE_PUBLISHABLE_KEY,
        "Authorization": f"Bearer {access_token}",
    }


async def get_user_profile(access_token: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{settings.SUPABASE_URL}/rest/v1/profiles",
            headers={
                **get_user_headers(access_token),
                "Accept": "application/json",
            },
            params={"select": "id,display_name,role,created_at"},
        )
        response.raise_for_status()
        return response.json()


async def create_document_record(
    access_token: str,
    payload: dict,
) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.SUPABASE_URL}/rest/v1/documents",
            headers={
                **get_user_headers(access_token),
                "Content-Type": "application/json",
                "Prefer": "return=representation",
            },
            json=payload,
        )
        response.raise_for_status()
        records = response.json()

        if not records:
            raise RuntimeError("Document record was not created.")

        return records[0]


async def update_document_record(
    access_token: str,
    document_id: str,
    payload: dict,
) -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.patch(
            f"{settings.SUPABASE_URL}/rest/v1/documents",
            headers={
                **get_user_headers(access_token),
                "Content-Type": "application/json",
            },
            params={"id": f"eq.{document_id}"},
            json=payload,
        )
        response.raise_for_status()


async def delete_document_record(
    access_token: str,
    document_id: str,
) -> None:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.delete(
            f"{settings.SUPABASE_URL}/rest/v1/documents",
            headers=get_user_headers(access_token),
            params={"id": f"eq.{document_id}"},
        )
        response.raise_for_status()