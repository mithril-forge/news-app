import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from core.secrets import get_database_config

logger = structlog.get_logger()

# Database configuration with secret support
db_config = get_database_config()

if not all(db_config.values()):
    logger.error("One or more database environment variables are not set")
    raise ValueError("One or more database environment variables are not set")

DATABASE_CONNECTION_STR = f"postgresql+psycopg://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
logger.info(f"Database connection configured for host: {db_config['host']}:{db_config['port']}/{db_config['database']}")

async_engine = create_async_engine(DATABASE_CONNECTION_STR, echo=False)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
logger.info("Database engine and session maker initialized")


async def get_session(commit_transaction: bool = True) -> AsyncGenerator[AsyncSession, None]:
    # Use the async_session_maker to create a session
    async with async_session_maker() as session:
        try:
            yield session
            if commit_transaction:
                await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()  # Or handled by context manager

@asynccontextmanager
async def get_session_context(commit_transaction: bool = True):
    async for session in get_session(commit_transaction=commit_transaction):
        try:
            yield session
        finally:
            # The session cleanup is handled by get_session itself
            pass