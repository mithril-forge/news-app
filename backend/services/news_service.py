from typing import List, Optional
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from database.repository import AsyncParsedNewsRepository, AsyncTopicRepository, AsyncTagRepository
from database.models import ParsedNews
from schemas import NewsCreate, NewsResponse, NewsWithTopicResponse
from services.converters import news_to_response, news_list_to_response, news_to_detailed_response


class NewsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.news_repo = AsyncParsedNewsRepository(session)
        self.topic_repo = AsyncTopicRepository(session)
        self.tag_repo = AsyncTagRepository(session)

    async def get_latest_news(self, count: int) -> List[NewsResponse]:
        """Get the latest N news items"""
        news = await self.news_repo.get_all()
        # Sort by created_at in descending order (newest first)
        sorted_news = sorted(news, key=lambda x: x.created_at, reverse=True)
        # Take only the requested number of items
        latest_news = sorted_news[:count]

        # Convert ORM models to response schemas with topic name
        return news_list_to_response(latest_news)

    async def get_news_by_id(self, news_id: int) -> NewsWithTopicResponse:
        """Get a specific news item by ID"""
        news = await self.news_repo.get_with_tags(news_id)
        if not news:
            raise HTTPException(status_code=404, detail="News not found")

        # Convert ORM model to detailed response schema
        return news_to_detailed_response(news)

    async def get_news_by_topic(self, topic_id: int) -> List[NewsResponse]:
        """Get all news for a specific topic"""
        # First verify the topic exists
        topic = await self.topic_repo.get_by_id(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        # Get news for this topic
        news_items = await self.news_repo.get_by_topic_id(topic_id)

        # Convert ORM models to response schemas with topic name
        return news_list_to_response(news_items)

    async def create_news(self, news_data: NewsCreate) -> NewsResponse:
        """Create a new news item with tags"""
        # Extract tags from the request
        tag_texts = news_data.tags or []

        # Create dict for the news item without tags
        news_dict = news_data.dict(exclude={"tags"})

        # Use repository to prepare news with tags (without committing)
        news = await self.news_repo.prepare_with_tags(news_dict, tag_texts)

        # Commit the transaction
        async with self.news_repo.transaction():
            pass

        # Get the complete news item with tags loaded
        complete_news = await self.news_repo.get_with_tags(news.id)

        # Convert ORM model to response schema with topic name
        return news_to_response(complete_news)