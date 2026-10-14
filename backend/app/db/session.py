
from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def _database_url() -> str:
    url = get_settings().database_url

    if url.startswith("postgresql://"):
        url = url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )
    elif url.startswith("postgres://"):
        url = url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1,
        )

    return url


@lru_cache
def get_engine():
    return create_engine(
        _database_url(),
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=10,
    )


@lru_cache
def get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_engine(),
        autoflush=False,
        expire_on_commit=False,
    )


def get_db() -> Iterator[Session]:
    """Request-scoped session. Services commit explicitly; anything uncommitted is rolled back on close."""
    db = get_sessionmaker()()
    try:
        yield db
    finally:
        db.close()
