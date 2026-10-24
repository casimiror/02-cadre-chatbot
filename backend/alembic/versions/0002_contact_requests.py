"""contact_requests: strategy-call requests taken by the bot

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "contact_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("first_name", sa.Text, nullable=False),
        sa.Column("last_name", sa.Text, nullable=False),
        sa.Column("company", sa.Text, nullable=False),
        sa.Column("email", sa.Text, nullable=False),
        sa.Column("phone", sa.Text),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("status", sa.String(16), server_default="open", nullable=False),
        sa.CheckConstraint(
            "status in ('open', 'contacted', 'closed')", name="contact_requests_status_check"
        ),
    )
    # Same as 0001: RLS on, no policies, so only the backend's direct connection can access it.
    op.execute("alter table public.contact_requests enable row level security")


def downgrade() -> None:
    op.drop_table("contact_requests")
