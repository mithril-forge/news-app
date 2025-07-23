from typing import List, TypeVar, Type, Optional

import structlog
from pydantic import BaseModel
from sqlmodel import SQLModel

from core.models import ParsedNews
from core.domain.schemas import (
    TagResponse,
    TopicResponse,
    ParsedNewsBasic,
    ParsedNewsResponseDetailed,
    InputNewsWithoutContent,
)

M = TypeVar("M", bound=SQLModel)
P = TypeVar("P", bound=BaseModel)

logger = structlog.get_logger()


def orm_to_pydantic(
    orm_obj: M, pydantic_class: Type[P], excludes: Optional[List[str]] = None
) -> P:
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


def orm_list_to_pydantic(
    orm_list: List[M], pydantic_class: Type[P], excludes: Optional[List[str]] = None
) -> List[P]:
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


def pydantic_to_orm(
    pydantic_obj: P, orm_class: Type[M], excludes: Optional[List[str]] = None
) -> M:
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


def news_to_response(news: ParsedNews) -> ParsedNewsBasic:
    """
    Convert a ParsedNews ORM model to NewsResponse schema with topic_name populated.

    Args:
        news: A ParsedNews SQLModel instance

    Returns:
        A NewsResponse Pydantic model instance with topic_name set
    """
    logger.debug(f"Converting news to response: {getattr(news, 'id', 'unknown')}")
    if not news:
        logger.warn("Received None news for conversion to response")
        return None

    # Convert to dict first
    data = news.dict()

    # Add topic_name if topic is available
    data["topic"] = orm_to_pydantic(news.topic, TopicResponse)
    data["tags"] = orm_list_to_pydantic(news.tags, TagResponse)

    # Create response model from dict
    result = ParsedNewsBasic(**data)
    logger.debug(
        f"Successfully converted news ID {getattr(news, 'id', 'unknown')} to basic response"
    )
    return result


def news_list_to_response(news_list: List[ParsedNews]) -> List[ParsedNewsBasic]:
    """
    Convert a list of ParsedNews ORM models to NewsResponse schemas with topic_name populated.

    Args:
        news_list: List of ParsedNews SQLModel instances

    Returns:
        List of NewsResponse Pydantic model instances with topic_name set
    """
    logger.debug(f"Converting list of {len(news_list)} news items to response")
    result = [news_to_response(news) for news in news_list]
    logger.debug(
        f"Successfully converted {len(result)} news items to basic response list"
    )
    return result


def news_to_detailed_response(news: ParsedNews) -> ParsedNewsResponseDetailed:
    """
    Convert a ParsedNews ORM model to NewsWithTopicResponse schema with topic relationship.

    Args:
        news: A ParsedNews SQLModel instance

    Returns:
        A NewsWithTopicResponse Pydantic model instance
    """
    logger.debug(
        f"Converting news to detailed response: {getattr(news, 'id', 'unknown')}"
    )
    if not news:
        logger.warn("Received None news for conversion to detailed response")
        return None

    # Convert to dict first
    data = news.dict()

    # Add topic_name if topic is available
    data["topic"] = orm_to_pydantic(news.topic, TopicResponse)
    data["tags"] = orm_list_to_pydantic(news.tags, TagResponse)
    data["input_news"] = orm_list_to_pydantic(news.input_news, InputNewsWithoutContent)

    # Create response model from dict
    result = ParsedNewsResponseDetailed(**data)
    logger.debug(
        f"Successfully converted news ID {getattr(news, 'id', 'unknown')} to detailed response"
    )
    return result
