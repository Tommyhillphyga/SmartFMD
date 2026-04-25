from pydantic import BaseModel, EmailStr

from app.core.enums import Role
from app.schemas.common import AppBaseModel


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(AppBaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthUser(AppBaseModel):
    id: str
    company_id: str
    station_id: str | None
    full_name: str
    email: EmailStr
    role: Role
    is_active: bool


class AuthResponse(TokenPair):
    user: AuthUser

