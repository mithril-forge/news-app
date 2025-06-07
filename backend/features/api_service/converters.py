from typing import List

from core.converters import orm_to_pydantic, orm_list_to_pydantic
from core.models import ParsedNews

from features.api_service.services.schemas import NewsResponseBasic, TopicResponse, TagResponse, NewsResponseDetailed, \
   InputNewsDetailed
from core.logger import create_logger

logger = create_logger(__name__)


def news_to_response(news: ParsedNews) -> NewsResponseBasic:
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
   result = NewsResponseBasic(**data)
   logger.info(f"Successfully converted news ID {getattr(news, 'id', 'unknown')} to basic response")
   return result


def news_list_to_response(news_list: List[ParsedNews]) -> List[NewsResponseBasic]:
   """
   Convert a list of ParsedNews ORM models to NewsResponse schemas with topic_name populated.

   Args:
       news_list: List of ParsedNews SQLModel instances

   Returns:
       List of NewsResponse Pydantic model instances with topic_name set
   """
   logger.debug(f"Converting list of {len(news_list)} news items to response")
   result = [news_to_response(news) for news in news_list]
   logger.info(f"Successfully converted {len(result)} news items to basic response list")
   return result


def news_to_detailed_response(news: ParsedNews) -> NewsResponseDetailed:
   """
   Convert a ParsedNews ORM model to NewsWithTopicResponse schema with topic relationship.

   Args:
       news: A ParsedNews SQLModel instance

   Returns:
       A NewsWithTopicResponse Pydantic model instance
   """
   logger.debug(f"Converting news to detailed response: {getattr(news, 'id', 'unknown')}")
   if not news:
       logger.warn("Received None news for conversion to detailed response")
       return None

   # Convert to dict first
   data = news.dict()

   # Add topic_name if topic is available
   data["topic"] = orm_to_pydantic(news.topic, TopicResponse)
   data["tags"] = orm_list_to_pydantic(news.tags, TagResponse)
   data["input_news"] = orm_list_to_pydantic(news.input_news, InputNewsDetailed)

   # Create response model from dict
   result = NewsResponseDetailed(**data)
   logger.info(f"Successfully converted news ID {getattr(news, 'id', 'unknown')} to detailed response")
   return result
