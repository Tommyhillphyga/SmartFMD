from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    settings = get_settings()
    secret = (
        settings.jwt_refresh_secret_key
        if token_type == "refresh"
        else settings.jwt_secret_key
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "exp": datetime.now(UTC) + expires_delta,
        "iat": datetime.now(UTC),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def create_access_token(subject: str) -> str:
    settings = get_settings()
    return create_token(subject, "access", timedelta(minutes=settings.access_token_expire_minutes))


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    return create_token(subject, "refresh", timedelta(minutes=settings.refresh_token_expire_minutes))


def decode_token(token: str, token_type: str) -> dict[str, Any]:
    settings = get_settings()
    secret = (
        settings.jwt_refresh_secret_key
        if token_type == "refresh"
        else settings.jwt_secret_key
    )
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    if payload.get("type") != token_type:
        raise jwt.InvalidTokenError("Invalid token type")
    return payload
