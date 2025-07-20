import datetime
import logging
from typing import List, Optional

import structlog
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from core.converters import orm_list_to_pydantic
from features.api_service.converters import news_list_to_response, news_to_detailed_response
from features.api_service.database.repository import AsyncParsedNewsRepository, AsyncTopicRepository, AsyncTagRepository
from features.api_service.services.schemas import NewsResponseDetailed, NewsResponseBasic, NewsCreate, NewsUpdate, \
    TagResponse, NewsBase, ParsedNewsSummary

logger = structlog.get_logger()


class NewsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.news_repo = AsyncParsedNewsRepository(session)
        self.topic_repo = AsyncTopicRepository(session)
        self.tag_repo = AsyncTagRepository(session)
        logger.info("NewsService initialized")

    async def get_tags(self) -> list[TagResponse]:
        logger.debug("Getting all tags")
        tag_models = await self.tag_repo.get_all()
        result = orm_list_to_pydantic(tag_models, TagResponse)
        logger.info(f"Retrieved {len(result)} tags")
        logger.debug(f"Tags: {[tag.model_dump_json() for tag in result]}")
        return result

    async def get_latest_news(self, skip: int, limit: int) -> List[NewsResponseBasic]:
        """Get the latest N news items"""
        logger.info(f"Fetching latest news (skip={skip}, limit={limit})")
        latest_news = await self.news_repo.get_latest(skip=skip, limit=limit)
        logger.debug(f"Retrieved {len(latest_news)} latest news items")
        return news_list_to_response(latest_news)

    async def get_most_popular_news(self, period: datetime.timedelta, limit: int) -> List[NewsResponseBasic]:
        logger.info(f"Fetching {limit} most popular news for {period}")
        popular_news = await self.news_repo.get_most_viewed_news_by_period(period=period, limit=limit)
        result = news_list_to_response(popular_news)
        logger.info(f"Retrieved {len(result)} most popular news items")
        return result

    async def get_news_by_id(self, news_id: int) -> NewsResponseDetailed:
        """Get a specific news item by ID"""
        logger.info(f"Fetching news by ID: {news_id}")
        news = await self.news_repo.get_with_tags(news_id)
        if not news:
            logger.warning(f"News with ID {news_id} not found")
            raise HTTPException(status_code=404, detail="News not found")

        result = news_to_detailed_response(news)
        logger.info(f"Successfully retrieved news by ID: {news_id}")
        logger.debug(f"News content: {result.model_dump_json(exclude={'content', 'description'})}")
        return result

    async def add_view_to_news(self, news_id: int) -> None:
        """ Add view to the news"""
        logger.debug(f"Adding view to news ID: {news_id}")
        await self.news_repo.add_view_to_news(news_id=news_id)
        logger.debug(f"Successfully added view to news ID: {news_id}")
        return None

    async def get_news_by_topic(self, topic_id: int, limit: int, skip: int) -> List[NewsResponseBasic]:
        """Get all news for a specific topic"""
        logger.info(f"Fetching news for topic ID {topic_id} (skip={skip}, limit={limit})")
        sorted_news = await self.news_repo.get_by_topic_id(topic_id=topic_id, limit=limit,
                                                           skip=skip)
        logger.info(f"Fetched {len(sorted_news)} for topic {topic_id}")
        logger.debug(f"Retrieved news ids: {[news.id for news in sorted_news]}")
        return news_list_to_response(sorted_news)

    async def create_news(self, news_data: NewsCreate) -> NewsResponseDetailed:
        """Create a new news item with tags"""
        logger.info(f"Creating new article with title: {news_data.title}")
        logger.debug(f"News data creation content: {news_data.model_dump_json(exclude={'content', 'description'})}")
        tag_texts = news_data.tags or []
        logger.debug(f"News tags: {', '.join(tag_texts) if tag_texts else 'None'}")

        # TODO: Image url ignored now and made static
        news_dict = news_data.dict(exclude={"tags", "image_url"})
        news_dict[
            "image_url"] = "https://st2.depositphotos.com/4431055/11871/i/600/depositphotos_118715222-stock-photo-businessman-reading-newspaper.jpg"
        news = await self.news_repo.prepare_with_tags(news_dict, tag_texts)
        logger.info(f"Created news item with ID: {news.id}")

        complete_news = await self.news_repo.get_with_tags(news.id)

        result = news_to_detailed_response(complete_news)
        logger.info(f"Successfully created and retrieved complete news item with ID: {news.id}")
        logger.debug(f"News data: {news_data.model_dump_json(exclude={'content', 'description'})}")
        return result

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
        logger.debug(f"Update news_data content: {news_data.model_dump_json(exclude={'content', 'description'})}")
        existing_news = await self.news_repo.get_by_id(news_data.id)
        if not existing_news:
            logger.warning(f"News with ID {news_data.id} not found for update")
            return None

        # TODO: Image url due to unsupported images right now, this will be fixed
        update_data = news_data.dict(exclude={"tags", "id", "image_url"})

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
        result = news_to_detailed_response(complete_news)
        logger.debug(f"Updated news_data content: {news_data.model_dump_json(exclude={'content', 'description'})}")
        return result

    async def get_latest_timestamp(self) -> Optional[datetime.datetime]:
        """
        Returns latest timestamp of the input news
        """
        logger.debug("Getting latest timestamp of the input news...")
        result = await self.news_repo.get_latest_received_timestamp()
        logger.info(f"Latest timestamp of input news retrieved: {result}")
        return result

    async def get_parsed_news_summary(self, delta: datetime.timedelta) -> list[ParsedNewsSummary]:
        """
        Returns ParsedNews with minimal information about them - title, description and other information
        """
        result = await self.news_repo.get_by_time_delta(delta=delta)
        pydantic_structures = orm_list_to_pydantic(orm_list=result, pydantic_class=ParsedNewsSummary)
        return pydantic_structures
