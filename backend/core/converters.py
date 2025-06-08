from typing import List, TypeVar, Type, Optional

import structlog
from pydantic import BaseModel
from sqlmodel import SQLModel


M = TypeVar('M', bound=SQLModel)
P = TypeVar('P', bound=BaseModel)

logger = structlog.get_logger()

def orm_to_pydantic(orm_obj: M, pydantic_class: Type[P],
                   excludes: Optional[List[str]] = None) -> P:
   """
   Convert an ORM model instance to a Pydantic model instance.

   Args:
       orm_obj: An SQLModel instance
       pydantic_class: A Pydantic model class
       excludes: List of fields to exclude from conversion

   Returns:
       A Pydantic model instance
   """
   if not orm_obj:
       logger.warn("Received None orm_obj for conversion")
       return None

   # Convert SQLModel instance to dict
   if excludes:
       # Convert to dict excluding specified fields
       data = {k: v for k, v in orm_obj.dict().items() if k not in excludes}
       logger.debug(f"Excluded fields: {excludes}")
   else:
       data = orm_obj.dict()

   # Create Pydantic model from dict
   result = pydantic_class(**data)
   return result


def orm_list_to_pydantic(orm_list: List[M], pydantic_class: Type[P],
                        excludes: Optional[List[str]] = None) -> List[P]:
   """
   Convert a list of ORM model instances to a list of Pydantic model instances.

   Args:
       orm_list: List of SQLModel instances
       pydantic_class: A Pydantic model class
       excludes: List of fields to exclude from conversion

   Returns:
       List of Pydantic model instances
   """
   result = [orm_to_pydantic(obj, pydantic_class, excludes) for obj in orm_list]
   return result


def pydantic_to_orm(pydantic_obj: P, orm_class: Type[M],
                   excludes: Optional[List[str]] = None) -> M:
   """
   Convert a Pydantic model instance to an ORM model instance.

   Args:
       pydantic_obj: A Pydantic model instance
       orm_class: An SQLModel class
       excludes: List of fields to exclude from conversion

   Returns:
       An SQLModel instance
   """
   if not pydantic_obj:
       logger.warn("Received None pydantic_obj for conversion")
       return None

   # Convert Pydantic model to dict
   if excludes:
       # Convert to dict excluding specified fields
       data = {k: v for k, v in pydantic_obj.dict().items() if k not in excludes}
   else:
       data = pydantic_obj.dict()

   # Create SQLModel from dict
   result = orm_class(**data)
   return result
