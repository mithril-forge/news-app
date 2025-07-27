"""
Utility functions for converting between ORM models and Pydantic schemas.
These functions are not strictly necessary since Pydantic's orm_mode handles conversion,
but they can be useful for more complex transformations.
"""

from collections.abc import Sequence

import structlog

from core.converters import news_to_detailed_response
from core.models import InputNews as InputNewsORM
from core.models import ParsedNews
from features.input_news_processing.domain.schemas import InputNews as InputNewsSchema
from features.input_news_processing.domain.schemas import (
    InputNewsWithID,
    InputNewsWithoutContent,
    ParsedNewsWithInputNews,
)

logger = structlog.get_logger()


def input_schema_to_orm(input_metadata: InputNewsSchema) -> InputNewsORM:
    """
    Convert an InputNewsMetadata Pydantic model to InputNews SQLModel instance.

    Args:
        input_metadata: An InputNewsMetadata Pydantic model instance

    Returns:
        An InputNews SQLModel instance ready to be added to the database
    """
    # Convert tags list to string representation (comma-separated)
    tags_str = ",".join(input_metadata.tags) if input_metadata.tags else None

    # Create InputNews instance
    result = InputNewsORM(
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
    return result


def input_schema_list_to_orm(
    input_metadata_list: list[InputNewsSchema],
) -> list[InputNewsORM]:
    """
    Convert a list of InputNewsMetadata Pydantic models to InputNews SQLModel instances.

    Args:
        input_metadata_list: List of InputNewsMetadata Pydantic model instances

    Returns:
        List of InputNews SQLModel instances ready to be added to the database
    """
    result = [input_schema_to_orm(item) for item in input_metadata_list]
    return result


def input_news_to_schema(input_news: InputNewsORM) -> InputNewsWithID:
    """
    Convert an InputNews SQLModel instance to InputNewsWithID Pydantic model.

    Args:
        input_news: An InputNews SQLModel instance from the database

    Returns:
        An InputNewsWithID Pydantic model instance
    """
    # Convert tags string to list
    tags_list = input_news.tags.split(",") if input_news.tags else []
    input_news_id = input_news.id
    if input_news_id is None:
        raise ValueError("Trying to convert input news without id when required.")
    result = InputNewsWithID(
        id=input_news_id,
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
    return result


def input_news_to_lite_schema(input_news: InputNewsORM) -> InputNewsWithoutContent:
    """
    Convert an InputNews SQLModel instance to InputNewsWithID Pydantic model.

    Args:
        input_news: An InputNews SQLModel instance from the database

    Returns:
        An InputNewsWithID Pydantic model instance
    """
    # Convert tags string to list
    tags_list = input_news.tags.split(",") if input_news.tags else []
    input_news_id = input_news.id
    if input_news_id is None:
        raise ValueError(f"Input news id is None for input news {input_news}")
    result = InputNewsWithoutContent(
        id=input_news_id,
        tags=tags_list,
        category=input_news.category,
        source_url=input_news.source_url,
        source_site=input_news.source_site,
        summary=input_news.summary,
        author=input_news.author,
        title=input_news.title,
        publication_date=input_news.publication_date,
    )
    return result


def input_news_lite_list_to_schema(
    input_news_list: list[InputNewsORM],
) -> list[InputNewsWithoutContent]:
    """
    Convert a list of InputNews SQLModel instances to InputNewsWithID Pydantic models.

    Args:
        input_news_list: List of InputNews SQLModel instances from the database

    Returns:
        List of InputNewsWithID Pydantic model instances
    """
    result = [input_news_to_lite_schema(item) for item in input_news_list if item]
    return result


def input_news_list_to_schema(
    input_news_list: Sequence[InputNewsORM],
) -> list[InputNewsWithID]:
    """
    Convert a list of InputNews SQLModel instances to InputNewsWithID Pydantic models.

    Args:
        input_news_list: List of InputNews SQLModel instances from the database

    Returns:
        List of InputNewsWithID Pydantic model instances
    """
    result = [input_news_to_schema(item) for item in input_news_list if item]
    return result


def parsed_news_with_input(parsed_news: ParsedNews) -> ParsedNewsWithInputNews:
    """Connects also input news schema to the parsed news one"""
    detailed_response = news_to_detailed_response(parsed_news).dict()
    # TODO: workaround for dependency on converter for the FE, we should probably separate it
    del detailed_response["input_news"]
    input_news = input_news_list_to_schema(input_news_list=parsed_news.input_news)
    result = ParsedNewsWithInputNews(**detailed_response, input_news=input_news)
    return result


def parsed_news_list_with_input(
    parsed_news_list: Sequence[ParsedNews],
) -> list[ParsedNewsWithInputNews]:
    """Converts a lit of parsed_news_list with input news also"""
    result = [parsed_news_with_input(item) for item in parsed_news_list if item]
    return result
