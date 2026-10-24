"""initial schema: conversations, messages, escalations

Revision ID: 0001
Revises:
Create Date: 2026-10-23
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = ("conversations", "messages", "escalations")


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    ]


def upgrade() -> None:
    op.create_table("conversations", *_timestamps())
    op.create_table(
        "messages",
        *_timestamps(),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.CheckConstraint("role in ('user', 'assistant')", name="messages_role_check"),
    )
    op.create_index(
        "messages_conversation_created_idx", "messages", ["conversation_id", "created_at"]
    )
    op.create_table(
        "escalations",
        *_timestamps(),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text),
        sa.Column("email", sa.Text, nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("status", sa.String(16), server_default="open", nullable=False),
        sa.CheckConstraint(
            "status in ('open', 'contacted', 'closed')", name="escalations_status_check"
        ),
    )
    # Supabase exposes public tables through its REST API: RLS on with no policies means only
    # our backend (direct Postgres connection) can read or write them.
    for table in TABLES:
        op.execute(f"alter table public.{table} enable row level security")


def downgrade() -> None:
    op.drop_table("escalations")
    op.drop_index("messages_conversation_created_idx", table_name="messages")
    op.drop_table("messages")
    op.drop_table("conversations")
