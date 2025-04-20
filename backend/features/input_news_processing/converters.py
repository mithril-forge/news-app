"""
Utility functions for converting between ORM models and Pydantic schemas.
These functions are not strictly necessary since Pydantic's orm_mode handles conversion,
but they can be useful for more complex transformations.
"""

from typing import List


from core.models import ParsedNews, InputNews
from features.api_service.converters import news_to_detailed_response
from features.input_news_processing.services.schemas import ParsedNewsWithInputNews, InputNewsSchema


def input_schema_to_orm(input_metadata: InputNewsSchema) -> InputNews:
    """
    Convert an InputNewsMetadata Pydantic model to InputNews SQLModel instance.

    Args:
        input_metadata: An InputNewsMetadata Pydantic model instance

    Returns:
        An InputNews SQLModel instance ready to be added to the database
    """
    if not input_metadata:
        return None

    # Convert tags list to string representation (comma-separated)
    tags_str = ",".join(input_metadata.tags) if input_metadata.tags else None

    # Create InputNews instance
    return InputNews(
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


def input_schema_list_to_orm(input_metadata_list: List[InputNewsSchema]) -> List[InputNews]:
    """
    Convert a list of InputNewsMetadata Pydantic models to InputNews SQLModel instances.

    Args:
        input_metadata_list: List of InputNewsMetadata Pydantic model instances

    Returns:
        List of InputNews SQLModel instances ready to be added to the database
    """
    return [input_schema_to_orm(item) for item in input_metadata_list]


def input_news_to_schema(input_news: InputNews) -> InputNewsSchema:
    """
    Convert an InputNews SQLModel instance to InputNewsSchema Pydantic model.

    Args:
        input_news: An InputNews SQLModel instance from the database

    Returns:
        An InputNewsSchema Pydantic model instance
    """
    if not input_news:
        return None

    # Convert tags string to list
    tags_list = input_news.tags.split(",") if input_news.tags else []

    # Create InputNewsSchema instance
    return InputNewsSchema(
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
        received_at=input_news.received_at,
        parsed_news_id=input_news.parsed_news_id
    )


def input_news_list_to_schema(input_news_list: List[InputNews]) -> List[InputNewsSchema]:
    """
    Convert a list of InputNews SQLModel instances to InputNewsSchema Pydantic models.

    Args:
        input_news_list: List of InputNews SQLModel instances from the database

    Returns:
        List of InputNewsSchema Pydantic model instances
    """
    return [input_news_to_schema(item) for item in input_news_list if item]


def parsed_news_with_input(parsed_news: ParsedNews) -> ParsedNewsWithInputNews:
    """ """
    detailed_response = news_to_detailed_response(parsed_news)
    input_news = input_news_list_to_schema(input_news_list=parsed_news.input_news)
    return ParsedNewsWithInputNews(**detailed_response.dict(), input_news=input_news)


def parsed_news_list_with_input(parsed_news_list: List[ParsedNews]) -> List[ParsedNewsWithInputNews]:
    """ """
    return [parsed_news_with_input(item) for item in parsed_news_list if item]
