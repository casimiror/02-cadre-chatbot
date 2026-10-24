from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.db.url import database_config


def build_session_factory(settings: Settings) -> sessionmaker[Session]:
    db = database_config(settings.database_url)
    engine = create_engine(db.url, pool_pre_ping=True, pool_size=5, connect_args=db.connect_args)
    return sessionmaker(engine, expire_on_commit=False)
