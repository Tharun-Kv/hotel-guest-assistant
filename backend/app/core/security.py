import secrets
from base64 import b64decode

from fastapi import HTTPException, Request

from app.core.config import settings


def require_admin(request: Request) -> None:
    authorization = request.headers.get("authorization", "")
    if authorization.lower().startswith("basic ") and settings.ADMIN_USERNAME and settings.ADMIN_PASSWORD:
        try:
            decoded = b64decode(authorization[6:], validate=True).decode("utf-8")
            username, separator, password = decoded.partition(":")
        except (ValueError, UnicodeDecodeError):
            username, separator, password = "", "", ""
        if separator and secrets.compare_digest(username, settings.ADMIN_USERNAME) and secrets.compare_digest(password, settings.ADMIN_PASSWORD):
            return
        raise HTTPException(status_code=401, detail="Invalid admin username or password.")

    configured_token = settings.ADMIN_API_TOKEN
    supplied_token = request.headers.get("x-admin-token", "")
    if configured_token:
        if not secrets.compare_digest(supplied_token, configured_token):
            raise HTTPException(status_code=401, detail="A valid admin token is required.")
        return
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=503, detail="Admin updates are disabled until ADMIN_API_TOKEN is configured.")
