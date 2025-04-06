import os
from typing import AsyncGenerator

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

ASYNC_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres+psycopg:postgres@postgres:5432/app_db")
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)


async def create_async_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session

if __name__ == "__main__":
    # Allows running `python database.py` to create tables
    import asyncio
    asyncio.run(create_async_db_and_tables())
