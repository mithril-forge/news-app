import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

DATABASE_CONNECTION_STR = os.getenv("DATABASE_CONNECTION_STR")
if DATABASE_CONNECTION_STR is None:
    raise ValueError("DATABASE_CONNECTION_STR is empty, please provide this environment var")
async_engine = create_async_engine(DATABASE_CONNECTION_STR, echo=True)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


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