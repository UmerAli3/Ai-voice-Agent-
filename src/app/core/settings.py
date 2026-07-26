"""Application Settings powered by Pydantic v2 BaseSettings."""

import os
from typing import List, Union
from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Production Pydantic Settings model."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Application Basics
    APP_NAME: str = "Healthcare Voice Agent"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 2

    # CORS
    ALLOWED_ORIGINS: Union[str, List[str]] = "http://localhost:3000,https://internexus.tech,https://api.internexus.tech"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Database Settings
    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "voiceagent"
    POSTGRES_PASSWORD: str = "ChooseAStrongPassword123!"
    POSTGRES_DB: str = "voiceagentdb"
    DATABASE_URL: str = "postgresql://voiceagent:ChooseAStrongPassword123!@postgres:5432/voiceagentdb"

    @field_validator("DATABASE_URL", mode="before")
    def parse_database_url(cls, v: str) -> str:
        if v and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # Security & Vapi Webhook Secret
    SECRET_KEY: str = "default_development_secret_key_change_in_production"
    VAPI_API_KEY: str = "5d47d14d-8512-4d3e-85c8-24e9290dc9aa"
    VAPI_WEBHOOK_SECRET: str = "whsec_your_webhook_secret_here"
    PHI_ENCRYPTION_KEY: str = "fernet_32_byte_base64_encoded_key_here"

    # Observability & Logging
    LOG_LEVEL: str = "INFO"
    PROMETHEUS_METRICS_ENABLED: bool = True


# Singleton settings instance
settings = Settings()
