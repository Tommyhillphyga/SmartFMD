import json
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = "Smart Fuel Dispenser Monitoring Dashboard"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    jwt_secret_key: str = "change-me-access"
    jwt_refresh_secret_key: str = "change-me-refresh"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7
    database_url: str = "postgresql+asyncpg://smartfmd:smartfmd@postgres:5432/smartfmd"
    redis_url: str = "redis://redis:6379/0"
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_username: str | None = None
    mqtt_password: str | None = None
    mqtt_base_topic: str = "fuel"
    mqtt_enabled: bool = True
    app_auto_create_schema: bool = False
    prometheus_enabled: bool = True
    email_from: str = "noreply@example.com"
    smtp_host: str = "mailhog"
    smtp_port: int = 1025
    sms_webhook_url: str = "https://example.com/sms"
    whatsapp_webhook_url: str = "https://example.com/whatsapp"

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_backend_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            raw_value = value.strip()
            if not raw_value:
                return []
            if raw_value.startswith("["):
                parsed_value = json.loads(raw_value)
                if isinstance(parsed_value, list):
                    return [str(item).strip() for item in parsed_value if str(item).strip()]
            return [item.strip() for item in raw_value.split(",") if item.strip()]
        raise TypeError("backend_cors_origins must be a list or comma-separated string")

    @property
    def is_test(self) -> bool:
        return self.app_env == "test"


@lru_cache
def get_settings() -> Settings:
    return Settings()
