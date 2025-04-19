"""
Utility functions for converting between ORM models and Pydantic schemas.
These functions are not strictly necessary since Pydantic's orm_mode handles conversion,
but they can be useful for more complex transformations.
"""

from typing import List

from pydantic import BaseModel
from sqlmodel import SQLModel

from features.input_news_processing.models import InputNews
from features.input_news_processing.schemas import InputNewsSchema
from features.input_news_processing.testing_data.additional_input_news import InputNewsMetadata


def input_metadata_to_orm(input_metadata: InputNewsMetadata) -> InputNews:
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


def input_metadata_list_to_orm(input_metadata_list: List[InputNewsSchema]) -> List[InputNews]:
    """
    Convert a list of InputNewsMetadata Pydantic models to InputNews SQLModel instances.

    Args:
        input_metadata_list: List of InputNewsMetadata Pydantic model instances

    Returns:
        List of InputNews SQLModel instances ready to be added to the database
    """
    return [input_metadata_to_orm(item) for item in input_metadata_list]