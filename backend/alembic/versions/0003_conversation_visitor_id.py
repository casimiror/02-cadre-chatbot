"""conversations.visitor_id: anonymous browser id, also the Langfuse user id

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Nullable: existing conversations have no visitor. RLS is already on for this table (0001).
    op.add_column("conversations", sa.Column("visitor_id", postgresql.UUID(as_uuid=True)))
    op.create_index("ix_conversations_visitor_id", "conversations", ["visitor_id"])


def downgrade() -> None:
    op.drop_index("ix_conversations_visitor_id", table_name="conversations")
    op.drop_column("conversations", "visitor_id")
