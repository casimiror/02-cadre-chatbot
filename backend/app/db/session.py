from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings


def build_session_factory(settings: Settings) -> sessionmaker[Session]:
    # Supabase: use the direct or *session* pooler URL (port 5432). The transaction
    # pooler (6543) breaks psycopg prepared statements.
    engine = create_engine(settings.database_url, pool_pre_ping=True, pool_size=5)
    return sessionmaker(engine, expire_on_commit=False)
