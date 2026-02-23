from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Mangable"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/mangable"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # API Key
    API_KEY_PREFIX: str = "mng_"

    # Storage (covers only metadata, no actual comic content)
    COVER_URL_BASE: str = "https://covers.example.com"

    class Config:
        env_file = ".env"


settings = Settings()
