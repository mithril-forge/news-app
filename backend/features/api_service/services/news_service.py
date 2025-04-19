import logging
from typing import List

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from features.api_service.converters import news_list_to_response, news_to_detailed_response
from features.api_service.database.repository import AsyncParsedNewsRepository, AsyncTopicRepository, AsyncTagRepository
from features.api_service.services.schemas import NewsResponseDetailed, NewsResponseBasic, NewsCreate

# Configure module logger
logger = logging.getLogger(__name__)


class NewsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.news_repo = AsyncParsedNewsRepository(session)
        self.topic_repo = AsyncTopicRepository(session)
        self.tag_repo = AsyncTagRepository(session)
        logger.debug("NewsService initialized")

    async def get_latest_news(self, skip: int, limit: int) -> List[NewsResponseBasic]:
        """Get the latest N news items"""
        logger.info(f"Fetching latest news (skip={skip}, limit={limit})")
        latest_news = await self.news_repo.get_latest(skip=skip, limit=limit)
        logger.debug(f"Retrieved {len(latest_news)} latest news items")
        return news_list_to_response(latest_news)

    async def get_news_by_id(self, news_id: int) -> NewsResponseDetailed:
        """Get a specific news item by ID"""
        logger.info(f"Fetching news by ID: {news_id}")
        news = await self.news_repo.get_with_tags(news_id)
        if not news:
            logger.warning(f"News with ID {news_id} not found")
            raise HTTPException(status_code=404, detail="News not found")

        return news_to_detailed_response(news)

    async def get_news_by_topic(self, topic_id: int, limit: int, skip: int) -> List[NewsResponseBasic]:
        """Get all news for a specific topic"""
        logger.info(f"Fetching news for topic ID {topic_id} (skip={skip}, limit={limit})")
        sorted_news = await self.news_repo.get_by_topic_id(topic_id=topic_id, limit=limit,
                                                           skip=skip)
        logger.debug(f"Retrieved {len(sorted_news)} news items for topic {topic_id}")
        return news_list_to_response(sorted_news)

    async def create_news(self, news_data: NewsCreate) -> NewsResponseDetailed:
        """Create a new news item with tags"""
        logger.info(f"Creating new news item: {news_data.title}")

        tag_texts = news_data.tags or []
        logger.debug(f"News tags: {', '.join(tag_texts) if tag_texts else 'None'}")

        news_dict = news_data.dict(exclude={"tags"})

        news = await self.news_repo.prepare_with_tags(news_dict, tag_texts)
        logger.info(f"Created news item with ID: {news.id}")

        complete_news = await self.news_repo.get_with_tags(news.id)

        return news_to_detailed_response(complete_news)
