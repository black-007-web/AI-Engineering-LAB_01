
from fastapi import Depends, HTTPException

from app.auth.dependencies import get_current_user
from app.database.supabase import get_user_profile


def require_role(*allowed_roles):

    async def role_checker(
        current_user: dict = Depends(get_current_user)
    ):
        profiles = await get_user_profile(
            current_user["access_token"]
        )

        if not profiles:
            raise HTTPException(
                status_code=403,
                detail="User profile not found"
            )

        application_role = profiles[0]["role"]

        if application_role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )

        return current_user

    return role_checker
