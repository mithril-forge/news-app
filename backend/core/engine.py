import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession


logger = structlog.get_logger()
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

if not all(
    [POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB]
):
    logger.error("One or more database environment variables are not set")
    raise ValueError("One or more database environment variables are not set")

DATABASE_CONNECTION_STR = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
logger.info(
    f"Database connection configured for host: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

async_engine = create_async_engine(DATABASE_CONNECTION_STR, echo=False)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
logger.info("Database engine and session maker initialized")


async def get_session(
    commit_transaction: bool = True,
) -> AsyncGenerator[AsyncSession, None]:
    # Use the async_session_maker to create a session
    logger.debug(
        f"Creating new database session (commit_transaction: {commit_transaction})"
    )
    async with async_session_maker() as session:
        try:
            yield session
            if commit_transaction:
                await session.commit()
                logger.debug("Database session committed")
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session rolled back due to error: {e}")
            raise
        finally:
            await session.close()
            logger.debug("Database session is closing...")


@asynccontextmanager
async def get_session_context(commit_transaction: bool = True):
    logger.debug(f"Getting session context (commit_transaction: {commit_transaction})")
    async for session in get_session(commit_transaction=commit_transaction):
        try:
            yield session
        finally:
            # The session cleanup is handled by get_session itself
            pass
