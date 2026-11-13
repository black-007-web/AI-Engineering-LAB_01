
from fastapi import APIRouter, Depends, HTTPException
import httpx

from app.auth.dependencies import get_current_user
from app.database.supabase import get_user_profile

from app.auth.permissions import require_role


router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"]
)
@router.get("/admin-check")
async def admin_check(
    current_user: dict = Depends(
        require_role("admin")
    )
):
    return {
        "message": "Admin access granted",
        "user_id": current_user["id"]
    }



@router.get("/me")
async def read_my_profile(
    current_user: dict = Depends(get_current_user)
):
    try:
        profiles = await get_user_profile(
            current_user["access_token"]
        )
        return profiles

    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail="Could not retrieve profile"
        )

    except httpx.HTTPError:
        raise HTTPException(
            status_code=502,
            detail="Database service unavailable"
        )
