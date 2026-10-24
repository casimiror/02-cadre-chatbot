from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR.parent / ".env", BACKEND_DIR / ".env"), extra="ignore"
    )

    llm_provider: str = "anthropic"
    llm_model: str = "claude-haiku-5-5"
    llm_api_key: str = ""
    llm_base_url: str | None = None
    llm_temperature: float = 0.2

    # Supabase Postgres, SQLAlchemy URL: postgresql+psycopg://user:pass@host:5432/postgres
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"

    rate_limit_chat: str = "10/minute"
    max_input_chars: int = 2000
    max_history_messages: int = 20

    booking_url: str = ""
    portal_url: str = ""

    frontend_dist: Path = BACKEND_DIR.parent / "frontend" / "dist"

    @property
    def langfuse_enabled(self) -> bool:
        return bool(self.langfuse_public_key and self.langfuse_secret_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
