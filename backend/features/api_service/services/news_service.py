import logging
from typing import List, Optional

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from core.converters import orm_list_to_pydantic
from features.api_service.converters import news_list_to_response, news_to_detailed_response
from features.api_service.database.repository import AsyncParsedNewsRepository, AsyncTopicRepository, AsyncTagRepository
from features.api_service.services.schemas import NewsResponseDetailed, NewsResponseBasic, NewsCreate, NewsUpdate, \
    TagResponse

# Configure module logger
logger = logging.getLogger(__name__)


class NewsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.news_repo = AsyncParsedNewsRepository(session)
        self.topic_repo = AsyncTopicRepository(session)
        self.tag_repo = AsyncTagRepository(session)
        logger.debug("NewsService initialized")

    async def get_tags(self) -> list[TagResponse]:
        tag_models = await self.tag_repo.get_all()
        return orm_list_to_pydantic(tag_models, TagResponse)

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

    async def add_view_to_news(self, news_id: int) -> None:
        """ Add view to the news"""
        logger.info(f"Fetching news by ID: {news_id}")
        await self.news_repo.add_view_to_news(news_id=news_id)
        return None

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

    async def update_news(self, news_data: NewsUpdate) -> Optional[NewsResponseDetailed]:
        """
        Update an existing news item including its tags

        Args:
            news_data: News data with updated fields and tags

        Returns:
            Updated news item with detailed information

        Raises:
            HTTPException: If news item not found
        """
        logger.info(f"Updating news item with ID: {news_data.id}")
        existing_news = await self.news_repo.get_by_id(news_data.id)
        if not existing_news:
            logger.warning(f"News with ID {news_data.id} not found for update")
            return None

        update_data = news_data.dict(exclude={"tags", "id"})

        tag_texts = news_data.tags or []
        logger.debug(f"Updating news tags to: {', '.join(tag_texts) if tag_texts else 'None'}")

        # Call repository method to handle the update and tag linking
        await self.news_repo.update_with_tags(
            news_id=news_data.id,
            news_data=update_data,
            tag_texts=tag_texts
        )

        # Get the completely updated news with tags
        complete_news = await self.news_repo.get_with_tags(news_data.id)
        logger.info(f"Successfully updated news item with ID: {news_data.id}")

        return news_to_detailed_response(complete_news)
