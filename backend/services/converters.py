"""
Utility functions for converting between ORM models and Pydantic schemas.
These functions are not strictly necessary since Pydantic's orm_mode handles conversion,
but they can be useful for more complex transformations.
"""

from typing import List, TypeVar, Type, Optional

from database.models import ParsedNews, InputNews
from pydantic import BaseModel
from schemas import NewsResponseBasic, NewsResponseDetailed, TagResponse, TopicResponse
from sqlmodel import SQLModel

from topic_generation.input_news_schema import InputNewsSchema
from topic_generation.testing_data.additional_input_news import InputNewsMetadata

M = TypeVar('M', bound=SQLModel)
P = TypeVar('P', bound=BaseModel)


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
        return None

    # Convert SQLModel instance to dict
    if excludes:
        # Convert to dict excluding specified fields
        data = {k: v for k, v in orm_obj.dict().items() if k not in excludes}
    else:
        data = orm_obj.dict()

    # Create Pydantic model from dict
    return pydantic_class(**data)


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
    return [orm_to_pydantic(obj, pydantic_class, excludes) for obj in orm_list]


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
        return None

    # Convert Pydantic model to dict
    if excludes:
        # Convert to dict excluding specified fields
        data = {k: v for k, v in pydantic_obj.dict().items() if k not in excludes}
    else:
        data = pydantic_obj.dict()

    # Create SQLModel from dict
    return orm_class(**data)


def news_to_response(news: ParsedNews) -> NewsResponseBasic:
    """
    Convert a ParsedNews ORM model to NewsResponse schema with topic_name populated.

    Args:
        news: A ParsedNews SQLModel instance

    Returns:
        A NewsResponse Pydantic model instance with topic_name set
    """
    if not news:
        return None

    # Convert to dict first
    data = news.dict()

    # Add topic_name if topic is available
    data["topic"] = orm_to_pydantic(news.topic, TopicResponse)
    data["tags"] = orm_list_to_pydantic(news.tags, TagResponse)

    # Create response model from dict
    return NewsResponseBasic(**data)


def news_list_to_response(news_list: List[ParsedNews]) -> List[NewsResponseBasic]:
    """
    Convert a list of ParsedNews ORM models to NewsResponse schemas with topic_name populated.

    Args:
        news_list: List of ParsedNews SQLModel instances

    Returns:
        List of NewsResponse Pydantic model instances with topic_name set
    """
    return [news_to_response(news) for news in news_list]


def news_to_detailed_response(news: ParsedNews) -> NewsResponseDetailed:
    """
    Convert a ParsedNews ORM model to NewsWithTopicResponse schema with topic relationship.

    Args:
        news: A ParsedNews SQLModel instance

    Returns:
        A NewsWithTopicResponse Pydantic model instance
    """
    if not news:
        return None

    # Convert to dict first
    data = news.dict()

    # Add topic_name if topic is available
    data["topic"] = orm_to_pydantic(news.topic, TopicResponse)
    data["tags"] = orm_list_to_pydantic(news.tags, TagResponse)

    # Create response model from dict
    return NewsResponseDetailed(**data)


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