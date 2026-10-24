"""ORM tables. Single source of truth for the schema: Alembic autogenerates from here."""

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampedMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ConversationRow(TimestampedMixin, Base):
    """Anonymous: a prospect gets an id the first time they write."""

    __tablename__ = "conversations"


class MessageRow(TimestampedMixin, Base):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint("role in ('user', 'assistant')", name="messages_role_check"),
        Index("messages_conversation_created_idx", "conversation_id", "created_at"),
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)


class EscalationRow(TimestampedMixin, Base):
    """Questions the bot could not answer, for the inbound team."""

    __tablename__ = "escalations"
    __table_args__ = (
        CheckConstraint(
            "status in ('open', 'contacted', 'closed')", name="escalations_status_check"
        ),
    )

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default="open")
