from langchain_core.callbacks import BaseCallbackHandler
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from app.core.config import Settings

_client: Langfuse | None = None


def init_observability(settings: Settings) -> None:
    """Create the Langfuse client once; CallbackHandler() picks it up afterwards."""
    global _client
    if settings.langfuse_enabled and _client is None:
        _client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            base_url=settings.langfuse_base_url,
        )


def trace_config(conversation_id: str, tags: list[str] | None = None) -> dict:
    """RunnableConfig for one chat turn: one trace, grouped by conversation."""
    callbacks: list[BaseCallbackHandler] = [CallbackHandler()] if _client else []
    return {
        "callbacks": callbacks,
        "metadata": {"langfuse_session_id": conversation_id, "langfuse_tags": tags or []},
    }


def flush() -> None:
    if _client:
        _client.flush()
