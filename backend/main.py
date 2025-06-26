import asyncio
import datetime
import os
import logging
import pathlib
import tempfile
import time
from typing import List, Optional

import structlog
from fastapi import FastAPI, Depends, Query, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware import Middleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from config import Environment

from core.engine import get_session, get_session_context
from features.api_service.services.news_service import NewsService
from features.api_service.services.schemas import TopicResponse, NewsResponseBasic, NewsResponseDetailed
from features.api_service.services.topic_service import TopicService
from features.input_news_processing.archive.local_archive import LocalArchive
from features.input_news_processing.services.input_news_service import InputNewsService
from logger import init_logging
from news_processing import get_input_news_and_parse, generate_and_connect_news

init_logging()
logger = structlog.get_logger()

environment = os.getenv("ENVIRONMENT")
logger.info(f"Environment: {environment}")
default_limits = []
origins = ["http://185.215.165.121"]
if environment == Environment.DEVELOPMENT.value:
    origins = [
        "*",
    ]

app = FastAPI()

# if environment == Environment.PRODUCTION.value:
#     default_limits = ["5/minute"]
#     limiter = Limiter(key_func=get_remote_address, default_limits=default_limits)
#     app = FastAPI(middleware=[Middleware(SlowAPIMiddleware)])
#     app.state.limiter = limiter

app.add_middleware(GZipMiddleware, minimum_size=4000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins allowed to make requests
    allow_credentials=True,  # Allow cookies/authorization headers
    allow_methods=["*"],  # Allow all standard methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error", "details": exc.errors()},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """ Add basic logging to the request with user tracking."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    start_time = time.time()
    logger.debug(f"Request started: {request.method} {request.url.path} from IP: {client_ip}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(f"Request: {request.method} {request.url.path} {request.query_params} "
                f"| IP: {client_ip} | UA: {user_agent[:50]}... "
                f"| Params: {request.query_params} took {process_time:.2f}s")

    logger.debug(f"Response for the request: {response}")
    return response


# API endpoints
@app.get("/topics", response_model=List[TopicResponse])
async def all_topics(session: AsyncSession = Depends(get_session)):
    """Get all topics"""
    service = TopicService(session)
    result = await service.get_all_topics()
    return result


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


@app.get("/news/popular", response_model=List[NewsResponseBasic])
async def popular_news(
        limit: Optional[int] = Query(10, ge=1, le=20),
        days: Optional[int] = Query(3, ge=1, le=30),
        session: AsyncSession = Depends(get_session)
):
    """ Get the most popular news by views"""
    service = NewsService(session=session)
    period = datetime.timedelta(days=days)
    return await service.get_most_popular_news(period=period, limit=limit)


@app.get("/news/{news_id}", response_model=NewsResponseDetailed)
async def read_news(news_id: int, session: AsyncSession = Depends(get_session)):
    """Get a specific news item by ID"""
    service = NewsService(session)
    result = await service.get_news_by_id(news_id=news_id)
    await service.add_view_to_news(news_id=news_id)
    return result


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


async def scheduled_task():
    logger.info("Starting scheduled task")
    while True:
        now = datetime.datetime.now()
        logger.debug(f"Scheduled task running at: {now}")

        async with get_session_context() as session:
            tmp_dir = tempfile.mkdtemp()
            local_archive = LocalArchive(target_location=pathlib.Path(tmp_dir))
            input_news_service = InputNewsService(session=session, archive=local_archive)
            latest_timestamp = await input_news_service.get_latest_timestamp()

        if now.hour >= 18 and latest_timestamp.day != now.day:
            logger.info("Starting input news parsing")
            try:
                delta = datetime.timedelta(days=1)
                await get_input_news_and_parse(adjust_parse_date=True, delta=delta)
                logger.info("Successfully parsed input news")
            except Exception as err:
                logger.error(f"Error {err} when generating articles")
                pass
        else:
            logger.debug(f"Skipping parsing of input news. Latest timestamp: {latest_timestamp}")

        now = datetime.datetime.now()
        async with get_session_context() as session:
            news_service = NewsService(session=session)
            latest_timestamp = await news_service.get_latest_timestamp()

        if now.hour >= 18 and latest_timestamp.day != now.day:
            logger.info("Starting AI news generation")
            try:
                delta = datetime.timedelta(days=1)
                await generate_and_connect_news(delta=delta)
                logger.info("Successfully generated and connected news")
            except Exception as err:
                logger.error(f"Error {err} when generating articles")
                pass
        else:
            logger.debug(f"Skipping AI news generation. Latest timestamp: {latest_timestamp}")

        logger.debug("Scheduled task sleeping for 6 hours")
        await asyncio.sleep(21600)


@app.on_event("startup")
async def startup():
    logger.info("FastAPI application starting up")
    if environment == Environment.PRODUCTION.value:
        logger.info("Running in production mode")
        logger.info("Creating scheduled task for the input news parsing")
        asyncio.create_task(scheduled_task())
    else:
        logger.info("Running in development mode")
