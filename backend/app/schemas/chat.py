from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    conversation_id: UUID | None = None
    # Hard cap at the HTTP layer; the max_length guardrail gives the friendly message.
    message: str = Field(min_length=1, max_length=10_000)


class ChatResponse(BaseModel):
    conversation_id: UUID
    reply: str
