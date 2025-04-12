import os
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

async def create_async_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    # Use the async_session_maker to create a session
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close() # Or handled by context manager
