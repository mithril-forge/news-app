from typing import List, Union

from fastapi import FastAPI, Depends

from services.dependencies import get_news_service, get_topic_service
from services.news_service import NewsService
from services.topic_service import TopicService
from schemas import TopicResponse, NewsResponse
from database.engine import create_async_db_and_tables

app = FastAPI()


# API endpoints
@app.get("/topics", response_model=List[TopicResponse])
async def all_topics(service: TopicService = Depends(get_topic_service)):
    """Get all topics"""
    return await service.get_all_topics()


@app.get("/topics/{topic_id}", response_model=TopicResponse)
async def specific_topic(topic_id: int, service: TopicService = Depends(get_topic_service)):
    """Get a specific topic by ID"""
    return await service.get_topic_by_id(topic_id)


# Route order matters - more specific routes first
@app.get("/news/topics/{topic_id}", response_model=List[NewsResponse])
async def news_by_topic(topic_id: int, service: NewsService = Depends(get_news_service)):
    """Get all news for a specific topic"""
    return await service.get_news_by_topic(topic_id)


@app.get("/news/latest/{latest_count}", response_model=List[NewsResponse])
async def latest_news(latest_count: int, service: NewsService = Depends(get_news_service)):
    """Get the latest N news items"""
    return await service.get_latest_news(latest_count)


@app.get("/news/{news_id}", response_model=NewsResponse)
async def read_news(news_id: int, service: NewsService = Depends(get_news_service)):
    """Get a specific news item by ID"""
    return await service.get_news_by_id(news_id)


@app.on_event("startup")
async def on_startup():
    # Create tables
    await create_async_db_and_tables()
