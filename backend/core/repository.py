import json
import pathlib
from contextlib import asynccontextmanager
from datetime import datetime
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

    async def update_from_dict(self, structure_id: int, data: Dict[str, Any]) -> Optional[T]:
        """
        Update an existing record with the given data.

        Args:
            id: The ID of the record to update
            data: Dictionary containing fields and values to update

        Returns:
            Updated model instance or None if record not found
        """
        instance = await self.get_by_id(structure_id)
        if not instance:
            return None

        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self.session.add(instance)
        await self.session.flush()

        return instance

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

    @staticmethod
    async def create_snapshot(instances: List[T]) -> dict[str, Any]:
        """
        Create a simple snapshot of model instances and save to JSON.

        Args:
            instances: List of model instances to snapshot
            filepath: Path where to save the snapshot file
        """
        data = []
        for instance in instances:
            instance_data = {}
            for field_name, field_value in instance.__dict__.items():
                # Skip SQLAlchemy internals and relationship objects
                if not field_name.startswith('_') and not isinstance(field_value, (list, SQLModel)):
                    instance_data[field_name] = field_value

            data.append(instance_data)

        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "model_type": T.__name__,
            "count": len(instances),
            "data": data
        }

        return snapshot
