"""
Utility functions for converting between ORM models and Pydantic schemas.
These functions are not strictly necessary since Pydantic's orm_mode handles conversion,
but they can be useful for more complex transformations.
"""

from typing import List


from core.models import ParsedNews, InputNews
from features.api_service.converters import news_to_detailed_response
from features.input_news_processing.services.schemas import ParsedNewsWithInputNews, InputNewsBase, InputNewsWithID
from core.logger import create_logger

logger = create_logger(__name__)


def input_schema_to_orm(input_metadata: InputNewsBase) -> InputNews:
   """
   Convert an InputNewsMetadata Pydantic model to InputNews SQLModel instance.

   Args:
       input_metadata: An InputNewsMetadata Pydantic model instance

   Returns:
       An InputNews SQLModel instance ready to be added to the database
   """
   logger.debug(f"Converting input schema to ORM: {getattr(input_metadata, 'title', 'unknown')}")
   if not input_metadata:
       logger.warn("Received None input_metadata for conversion to ORM")
       return None

   # Convert tags list to string representation (comma-separated)
   tags_str = ",".join(input_metadata.tags) if input_metadata.tags else None

   # Create InputNews instance
   result = InputNews(
       tags=tags_str,
       category=input_metadata.category,
       source_url=input_metadata.source_url,
       source_site=input_metadata.source_site,
       summary=input_metadata.summary,
       author=input_metadata.author,
       content=input_metadata.content,
       title=input_metadata.title,
       publication_date=input_metadata.publication_date,
   )
   logger.info(f"Successfully converted input schema to ORM: {input_metadata.title}")
   return result


def input_schema_list_to_orm(input_metadata_list: List[InputNewsBase]) -> List[InputNews]:
   """
   Convert a list of InputNewsMetadata Pydantic models to InputNews SQLModel instances.

   Args:
       input_metadata_list: List of InputNewsMetadata Pydantic model instances

   Returns:
       List of InputNews SQLModel instances ready to be added to the database
   """
   logger.debug(f"Converting list of {len(input_metadata_list)} input schemas to ORM")
   result = [input_schema_to_orm(item) for item in input_metadata_list]
   logger.info(f"Successfully converted {len(result)} input schemas to ORM")
   return result


def input_news_to_schema(input_news: InputNews) -> InputNewsWithID:
   """
   Convert an InputNews SQLModel instance to InputNewsWithID Pydantic model.

   Args:
       input_news: An InputNews SQLModel instance from the database

   Returns:
       An InputNewsWithID Pydantic model instance
   """
   logger.debug(f"Converting input news to schema: {getattr(input_news, 'id', 'unknown')}")
   if not input_news:
       logger.warn("Received None input_news for conversion to schema")
       return None

   # Convert tags string to list
   tags_list = input_news.tags.split(",") if input_news.tags else []

   result = InputNewsWithID(
       id=input_news.id,
       tags=tags_list,
       category=input_news.category,
       source_url=input_news.source_url,
       source_site=input_news.source_site,
       summary=input_news.summary,
       author=input_news.author,
       content=input_news.content,
       title=input_news.title,
       publication_date=input_news.publication_date,
   )
   logger.info(f"Successfully converted input news ID {input_news.id} to schema")
   return result


def input_news_list_to_schema(input_news_list: List[InputNews]) -> List[InputNewsWithID]:
   """
   Convert a list of InputNews SQLModel instances to InputNewsWithID Pydantic models.

   Args:
       input_news_list: List of InputNews SQLModel instances from the database

   Returns:
       List of InputNewsWithID Pydantic model instances
   """
   logger.debug(f"Converting list of {len(input_news_list)} input news to schema")
   result = [input_news_to_schema(item) for item in input_news_list if item]
   logger.info(f"Successfully converted {len(result)} input news items to schema")
   return result


def parsed_news_with_input(parsed_news: ParsedNews) -> ParsedNewsWithInputNews:
   """ Connects also input news schema to the parsed news one"""
   logger.debug(f"Converting parsed news with input: {getattr(parsed_news, 'id', 'unknown')}")
   detailed_response = news_to_detailed_response(parsed_news).dict()
   # TODO: workaround for dependency on converter for the FE, we should probably separate it
   del detailed_response["input_news"]
   input_news = input_news_list_to_schema(input_news_list=parsed_news.input_news)
   result = ParsedNewsWithInputNews(**detailed_response, input_news=input_news)
   logger.info(f"Successfully converted parsed news ID {getattr(parsed_news, 'id', 'unknown')} with input")
   return result


def parsed_news_list_with_input(parsed_news_list: List[ParsedNews]) -> List[ParsedNewsWithInputNews]:
   """ Converts a lit of parsed_news_list with input news also"""
   logger.debug(f"Converting list of {len(parsed_news_list)} parsed news with input")
   result = [parsed_news_with_input(item) for item in parsed_news_list if item]
   logger.info(f"Successfully converted {len(result)} parsed news items with input")
   return result