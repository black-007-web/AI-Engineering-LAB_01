
import jwt

from jwt import PyJWKClient
from jwt.exceptions import PyJWTError

from app.core.config import settings


jwks_client = PyJWKClient(settings.SUPABASE_JWKS_URL)


def verify_access_token(token: str) -> dict:
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
            issuer=f"{settings.SUPABASE_URL}/auth/v1"
        )

        if not claims.get("sub"):
            raise ValueError("Token has no user identity")

        return claims

    except (PyJWTError, ValueError) as exc:
        raise ValueError("Invalid or expired access token") from exc
