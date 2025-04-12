import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

ASYNC_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres+psycopg:postgres@postgres:5432/app_db")
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
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

if __name__ == "__main__":
    # Allows running `python database.py` to create tables
    import asyncio
    asyncio.run(create_async_db_and_tables())
