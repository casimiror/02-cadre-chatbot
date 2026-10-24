from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

Role = Literal["user", "assistant"]


class Message(BaseModel):
    id: UUID
    conversation_id: UUID
    role: Role
    content: str
    created_at: datetime


class Conversation(BaseModel):
    id: UUID
    created_at: datetime


class Escalation(BaseModel):
    id: UUID
    conversation_id: UUID
    name: str | None
    email: str
    question: str
    created_at: datetime


class ContactRequest(BaseModel):
    id: UUID
    conversation_id: UUID
    first_name: str
    last_name: str
    company: str
    email: str
    phone: str | None
    message: str
    created_at: datetime
