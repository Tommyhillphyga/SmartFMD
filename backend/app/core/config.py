from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    project_name: str = "Smart Fuel Dispenser Monitoring Dashboard"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
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

    @property
    def is_test(self) -> bool:
        return self.app_env == "test"


@lru_cache
def get_settings() -> Settings:
    return Settings()
