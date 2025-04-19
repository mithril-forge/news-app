from typing import List

from pydantic import BaseModel

from core.converters import orm_to_pydantic, orm_list_to_pydantic
from sqlmodel import SQLModel

from features.api_service.database.models import ParsedNews
from features.api_service.services.schemas import NewsResponseBasic, TopicResponse, TagResponse, NewsResponseDetailed


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

