from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends

from database.engine import get_async_session
from services.topic_service import TopicService
from services.news_service import NewsService

# Dependency to get topic service
async def get_topic_service(session: AsyncSession = Depends(get_async_session)) -> TopicService:
    return TopicService(session)

# Dependency to get news service
async def get_news_service(session: AsyncSession = Depends(get_async_session)) -> NewsService:
    return NewsService(session)