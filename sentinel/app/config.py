"""Application configuration with strict $0 budget enforcement."""

from functools import lru_cache
from typing import List, Set
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core metadata
    APP_NAME: str = "Sentinel AI Intelligence Agent"
    APP_ENV: str = "production"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = Field(default="", description="Telegram Bot Token")
    TELEGRAM_WEBHOOK_URL: str = Field(default="", description="Full webhook URL")
    TELEGRAM_WEBHOOK_SECRET: str = Field(default="sentinel_secret_token", description="Webhook verification secret")
    ALLOWED_TELEGRAM_USER_IDS: List[int] = Field(default_factory=lambda: [123456789])

    # Database: Default to SQLite for zero-config local testing, PostgreSQL in production
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///sentinel.db",
        description="Async SQLAlchemy database URL (e.g. postgresql+asyncpg://... or sqlite+aiosqlite:///...)",
    )

    # $0 Hard Budget Constraints
    DAILY_AI_BUDGET: float = Field(default=0.0, description="Hard cap on daily spend in USD. Must be 0 for free tier.")
    ALLOW_PAID_PROVIDERS: bool = Field(default=False, description="Strictly False to reject any non-free tier calls.")

    # Free AI Provider Keys & Endpoints
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini Free Tier API Key")
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    GROQ_API_KEY: str = Field(default="", description="Groq Free Tier API Key")
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API Key for free models (:free)")
    
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Local Ollama fallback URL")
    OLLAMA_MODEL: str = "qwen2.5:7b"

    # Ingestion & Polling Defaults
    INGEST_POLL_INTERVAL_HOURS: int = 4
    DIGEST_DELIVERY_TIME_IST: str = "10:00"

    @field_validator("DAILY_AI_BUDGET")
    @classmethod
    def validate_budget(cls, v: float, info) -> float:
        # ponytail: hard $0 guard check; reject non-zero budget if paid providers are disallowed
        if v > 0.0 and not info.data.get("ALLOW_PAID_PROVIDERS", False):
            raise ValueError("DAILY_AI_BUDGET must be 0.0 when ALLOW_PAID_PROVIDERS is False")
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()
