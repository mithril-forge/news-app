from contextlib import asynccontextmanager
from typing import List, Optional, TypeVar, Generic, Type, Any, Dict, Union, AsyncContextManager

from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar('T', bound=SQLModel)


class AsyncBaseRepository(Generic[T]):
    """Base async repository with common CRUD operations."""

    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    @asynccontextmanager
    async def transaction(self) -> AsyncContextManager[None]:
        """Context manager for transactions."""
        try:
            yield
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def get_by_id(self, id: int) -> Optional[T]:
        """Get a record by ID."""
        return await self.session.get(self.model_class, id)

    async def get_all(self) -> List[T]:
        """Get all records."""
        statement = select(self.model_class)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def add(self, obj_in: Union[Dict[str, Any], T]) -> T:
        """Add a new record to the session without committing."""
        if isinstance(obj_in, dict):
            obj = self.model_class(**obj_in)
        else:
            obj = obj_in

        self.session.add(obj)
        await self.session.flush()  # Flush to get the ID but don't commit
        return obj

    async def update(self, obj: T) -> T:
        """Update an existing record without committing."""
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def refresh(self, obj: T) -> T:
        """Refresh an object from the database."""
        await self.session.refresh(obj)
        return obj

    async def remove(self, id: int) -> Optional[T]:
        """Remove a record from the session without committing."""
        obj = await self.session.get(self.model_class, id)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()
        return obj

    async def get_latest(self, skip: int, limit: int) -> List[T]:
        """
        Fetch latest with pagination
        """
        query = select(self.model_class).order_by(self.model_class.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
