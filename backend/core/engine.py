import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

def get_database_url():
    """Get database URL with password from Docker secret or environment"""
    base_url = os.getenv('DATABASE_CONNECTION_STR')

    if not base_url:
        raise ValueError("DATABASE_CONNECTION_STR environment variable not set")

    # Try to read password from Docker secret
    password_file = os.getenv('POSTGRES_PASSWORD_FILE')
    if password_file and os.path.exists(password_file):
        try:
            with open(password_file, 'r') as f:
                password = f.read().strip()
            # Insert password into connection string
            # postgresql+psycopg://postgres@postgres:5432/app_db
            # becomes postgresql+psycopg://postgres:PASSWORD@postgres:5432/app_db
            if '@postgres:' in base_url and ':' not in base_url.split('//')[1].split('@')[0]:
                return base_url.replace('@postgres:', f':{password}@postgres:')
        except Exception as e:
            print(f"Warning: Could not read password from secret file: {e}")

    # Fallback to original URL (for development or if secret not available)
    return base_url

DATABASE_CONNECTION_STR = get_database_url()

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
