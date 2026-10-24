"""alembic_version: enable RLS like every other public table

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-24
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Alembic creates this table itself, outside any revision, so 0001 never covered it. Supabase
    # exposes `public` over REST: without RLS the anon role could read or rewrite the version.
    # Migrations still work because they connect as the table owner, which RLS doesn't restrict.
    op.execute("alter table public.alembic_version enable row level security")


def downgrade() -> None:
    op.execute("alter table public.alembic_version disable row level security")
