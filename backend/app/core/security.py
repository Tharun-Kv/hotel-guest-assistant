import secrets

from fastapi import HTTPException, Request

from app.core.config import settings


def require_admin(request: Request) -> None:
    configured_token = settings.ADMIN_API_TOKEN
    supplied_token = request.headers.get("x-admin-token", "")
    if configured_token:
        if not secrets.compare_digest(supplied_token, configured_token):
            raise HTTPException(status_code=401, detail="A valid admin token is required.")
        return
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=503, detail="Admin updates are disabled until ADMIN_API_TOKEN is configured.")
