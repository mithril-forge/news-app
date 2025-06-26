import json
import pathlib
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional, TypeVar, Generic, Type, Any, Dict, Union, AsyncContextManager

import structlog
from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


T = TypeVar('T', bound=SQLModel)

logger = structlog.get_logger()

class AsyncBaseRepository(Generic[T]):
   """Base async repository with common CRUD operations."""

   def __init__(self, session: AsyncSession, model_class: Type[T]):
       self.session = session
       self.model_class = model_class
       logger.info(f'Initialized repository for {model_class.__name__}')

   @asynccontextmanager
   async def transaction(self) -> AsyncContextManager[None]:
       """Context manager for transactions."""
       logger.debug('Starting transaction')
       try:
           yield
           await self.session.commit()
           logger.debug('Transaction committed')
       except Exception as e:
           await self.session.rollback()
           logger.error(f'Transaction rolled back due to error: {e}')
           raise

   async def get_by_id(self, id: int) -> Optional[T]:
       """Get a record by ID."""
       logger.debug(f'Getting {self.model_class.__name__} by ID: {id}')
       result = await self.session.get(self.model_class, id)
       logger.info(f'Found {self.model_class.__name__} with ID {id}: {result is not None}')
       return result

   async def get_all(self) -> List[T]:
       """Get all records."""
       logger.debug(f'Getting all {self.model_class.__name__} records')
       statement = select(self.model_class)
       result = await self.session.execute(statement)
       records = result.scalars().all()
       logger.info(f'Retrieved {len(records)} {self.model_class.__name__} records')
       return records

   async def add(self, obj_in: Union[Dict[str, Any], T]) -> T:
       """Add a new record to the session without committing."""
       logger.debug(f'Adding new {self.model_class.__name__}')
       if isinstance(obj_in, dict):
           obj = self.model_class(**obj_in)
       else:
           obj = obj_in

       self.session.add(obj)
       await self.session.flush()  # Flush to get the ID but don't commit
       logger.info(f'Added new {self.model_class.__name__} with ID: {getattr(obj, "id", "unknown")}')
       return obj

   async def update(self, obj: T) -> T:
       """Update an existing record without committing."""
       logger.debug(f'Updating {self.model_class.__name__} with ID: {getattr(obj, "id", "unknown")}')
       self.session.add(obj)
       await self.session.flush()
       logger.info(f'Updated {self.model_class.__name__} with ID: {getattr(obj, "id", "unknown")}')
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
       logger.info(f'Updating {self.model_class.__name__} with ID {structure_id} from dict')
       logger.debug(f'Updating dict: {data}')
       instance = await self.get_by_id(structure_id)
       if not instance:
           logger.warn(f'{self.model_class.__name__} with ID {structure_id} not found for update')
           return None

       for key, value in data.items():
           if hasattr(instance, key):
               setattr(instance, key, value)

       self.session.add(instance)
       await self.session.flush()
       logger.info(f'Updated {self.model_class.__name__} with ID {structure_id} from dict')

       return instance

   async def refresh(self, obj: T) -> T:
       """Refresh an object from the database."""
       logger.debug(f'Refreshing {self.model_class.__name__} with ID: {getattr(obj, "id", "unknown")}')
       await self.session.refresh(obj)
       return obj

   async def remove(self, id: int) -> Optional[T]:
       """Remove a record from the session without committing."""
       logger.debug(f'Removing {self.model_class.__name__} with ID: {id}')
       obj = await self.session.get(self.model_class, id)
       if obj:
           await self.session.delete(obj)
           await self.session.flush()
           logger.info(f'Removed {self.model_class.__name__} with ID: {id}')
       else:
           logger.warn(f'{self.model_class.__name__} with ID {id} not found for removal')
       return obj

   async def get_latest(self, skip: int, limit: int) -> List[T]:
       """
       Fetch latest with pagination
       """
       logger.debug(f'Getting latest {self.model_class.__name__} records (skip: {skip}, limit: {limit})')
       query = select(self.model_class).order_by(self.model_class.updated_at.desc()).offset(skip).limit(limit)
       result = await self.session.execute(query)
       records = result.scalars().all()
       logger.info(f'Retrieved {len(records)} latest {self.model_class.__name__} records')
       return records

   @staticmethod
   async def create_snapshot(instances: List[T]) -> dict[str, Any]:
       """
       Create a simple snapshot of model instances and save to JSON.

       Args:
           instances: List of model instances to snapshot
           filepath: Path where to save the snapshot file
       """
       logger.debug(f'Creating snapshot of {len(instances)} instances')
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

       logger.info(f'Created snapshot with {len(instances)} instances')
       return snapshot