from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR.parent / ".env", BACKEND_DIR / ".env"), extra="ignore"
    )

    llm_provider: str = "openrouter"
    llm_model: str = "google/gemini-3.5-flash-lite"
    llm_api_key: str = ""
    llm_base_url: str | None = None
    llm_temperature: float = 0.2

    # Any Postgres URL (normalized in app/db/url.py). Default: the docker compose `db` service;
    # keep it in sync with docker-compose.yml. On Vercel: Supabase's transaction pooler, either as
    # DATABASE_URL or as POSTGRES_URL (set by the Vercel Supabase integration).
    database_url: str = Field(
        default="postgresql+psycopg://cadre_app:cadre_local_pw@db:5432/cadre_support",
        validation_alias=AliasChoices("DATABASE_URL", "POSTGRES_URL"),
    )

    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    # LANGFUSE_BASE_URL is the SDK's current name; LANGFUSE_HOST still accepted. EU by default,
    # US projects use https://us.cloud.langfuse.com.
    langfuse_base_url: str = Field(
        default="https://cloud.langfuse.com",
        validation_alias=AliasChoices("LANGFUSE_BASE_URL", "LANGFUSE_HOST"),
    )

    rate_limit_chat: str = "10/minute"
    max_input_chars: int = 2000
    max_history_messages: int = 20

    # Cadre has no self-serve calendar: a strategy call starts from the contact page or email.
    website_url: str = "https://cadre.ai"
    booking_url: str = "https://cadre.ai/contact"
    contact_email: str = "hello@gocadre.ai"
    portal_url: str = ""

    frontend_dist: Path = BACKEND_DIR.parent / "frontend" / "dist"

    @property
    def langfuse_enabled(self) -> bool:
        return bool(self.langfuse_public_key and self.langfuse_secret_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
