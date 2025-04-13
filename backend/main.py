import os
import logging
import time
from typing import List, Optional

from fastapi import FastAPI, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel.ext.asyncio.session import AsyncSession

from config import Environment
from database.engine import get_session
from schemas import TopicResponse, NewsResponseBasic, NewsResponseDetailed
from services.news_service import NewsService
from services.topic_service import TopicService
from fastapi.middleware import Middleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])
app = FastAPI(middleware=[Middleware(SlowAPIMiddleware)])
app.state.limiter = limiter
environment = os.getenv("ENVIRONMENT")
origins = []
if environment == Environment.DEVELOPMENT.value:
    origins = [
        "http://localhost",
    ]
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins allowed to make requests
    allow_credentials=True,  # Allow cookies/authorization headers
    allow_methods=["*"],  # Allow all standard methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """ Add basic logging to the request."""
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url.path} {request.query_params}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} took {process_time:.2f}s")
    logger.debug(f"Response for the request: {response}")
    return response


# API endpoints
@app.get("/topics", response_model=List[TopicResponse])
async def all_topics(session: AsyncSession = Depends(get_session)):
    """Get all topics"""
    service = TopicService(session)
    return await service.get_all_topics()


@app.get("/topics/{topic_id}", response_model=TopicResponse)
async def specific_topic(topic_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific topic by ID"""
    service = TopicService(session)
    return await service.get_topic_by_id(topic_id)


@app.get("/news/topics/{topic_id}", response_model=List[NewsResponseBasic])
async def news_by_topic(
        topic_id: int,
        skip: Optional[int] = Query(0, ge=0, description="Number of records to skip"),
        limit: Optional[int] = Query(10, ge=1, le=100, description="Max number of records to return"),
        session: AsyncSession = Depends(get_session)
):
    """Get news for a specific topic with pagination"""
    service = NewsService(session)
    return await service.get_news_by_topic(topic_id, skip=skip, limit=limit)


@app.get("/news/latest", response_model=List[NewsResponseBasic])
async def latest_news(
        skip: Optional[int] = Query(0, ge=0, description="Number of records to skip"),
        limit: Optional[int] = Query(10, ge=1, le=100, description="Max number of records to return"),
        session: AsyncSession = Depends(get_session)
):
    """Get the latest news items with pagination"""
    service = NewsService(session)
    return await service.get_latest_news(skip=skip, limit=limit)


@app.get("/news/{news_id}", response_model=NewsResponseDetailed)
async def read_news(news_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific news item by ID"""
    service = NewsService(session)
    return await service.get_news_by_id(news_id)