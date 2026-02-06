"""Database connection and session management."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from munger.core.config import settings
from munger.db.models import Base


def get_engine(db_path: str | None = None):
    """Create SQLAlchemy engine."""
    if db_path is None:
        settings.ensure_data_dir()
        db_path = str(settings.db_path)

    return create_engine(f"sqlite:///{db_path}", echo=False)


def init_db(db_path: str | None = None) -> None:
    """Initialize database and create all tables."""
    engine = get_engine(db_path)
    Base.metadata.create_all(engine)


def get_session_factory(db_path: str | None = None) -> sessionmaker[Session]:
    """Get session factory for database operations."""
    engine = get_engine(db_path)
    return sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def get_session(db_path: str | None = None) -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    factory = get_session_factory(db_path)
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
