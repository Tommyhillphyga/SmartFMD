from pydantic import BaseModel, EmailStr

from app.core.enums import Role
from app.schemas.common import AppBaseModel


class UserCreate(BaseModel):
    company_id: str
    station_id: str | None = None
    full_name: str
    email: EmailStr
    password: str
    role: Role


class UserRead(AppBaseModel):
    id: str
    company_id: str
    station_id: str | None
    full_name: str
    email: EmailStr
    role: Role
    is_active: bool

