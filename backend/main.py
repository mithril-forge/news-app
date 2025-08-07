import datetime
import os
import time
from typing import Annotated, Any

import structlog
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.account_service import AccountService
from config import Environment
from core.domain.news_service import NewsService
from core.domain.schemas import (
    AccountDetails,
    ParsedNewsBasic,
    ParsedNewsResponseDetailed,
    TopicResponse,
)
from core.domain.topic_service import TopicService
from core.engine import get_session
from dramatiq_tasks import create_daily_pick_for_user
from logger import init_logging

init_logging()
logger = structlog.get_logger()

environment = os.getenv("ENVIRONMENT")
logger.info(f"Environment: {environment}")
default_limits: list[str] = []
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
async def http_exception_handler(request: Request, exc: Any) -> JSONResponse:
    logger.error(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: Any) -> JSONResponse:
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"message": "Validation error", "details": exc.errors()},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next: Any) -> Any:
    """Add basic logging to the request with user tracking."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")

    start_time = time.time()
    logger.debug(f"Request started: {request.method} {request.url.path} from IP: {client_ip}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"Request: {request.method} {request.url.path} {request.query_params} "
        f"| IP: {client_ip} | UA: {user_agent[:50]}... "
        f"| Params: {request.query_params} took {process_time:.2f}s"
    )

    logger.debug(f"Response for the request: {response}")
    return response


# API endpoints
@app.get("/topics")
async def all_topics(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[TopicResponse]:
    """Get all topics"""
    service = TopicService(session)
    result = await service.get_all_topics()
    return result


@app.get("/topics/{topic_id}")
async def specific_topic(topic_id: int, session: Annotated[AsyncSession, Depends(get_session)]) -> TopicResponse:
    """Get a specific topic by ID"""
    service = TopicService(session)
    return await service.get_topic_by_id(topic_id)


@app.get("/news/topics/{topic_id}")
async def news_by_topic(
    session: Annotated[AsyncSession, Depends(get_session)],
    topic_id: int,
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max number of records to return")] = 10,
) -> list[ParsedNewsBasic]:
    """Get news for a specific topic with pagination"""
    service = NewsService(session)
    return await service.get_news_by_topic(topic_id, skip=skip, limit=limit)


@app.get("/news/latest")
async def latest_news(
    session: Annotated[AsyncSession, Depends(get_session)],
    skip: Annotated[int, Query(ge=0, description="Number of records to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max number of records to return")] = 10,
) -> list[ParsedNewsBasic]:
    """Get the latest news items with pagination"""
    service = NewsService(session)
    return await service.get_latest_news(skip=skip, limit=limit)


@app.get("/news/popular")
async def popular_news(
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
    days: Annotated[int, Query(ge=1, le=30)] = 3,
) -> list[ParsedNewsBasic]:
    """Get the most popular news by views"""
    service = NewsService(session=session)
    period = datetime.timedelta(days=days)
    return await service.get_most_popular_news(period=period, limit=limit)


@app.get("/news/{news_id}")
async def read_news(news_id: int, session: Annotated[AsyncSession, Depends(get_session)]) -> ParsedNewsResponseDetailed:
    """Get a specific news item by ID"""
    service = NewsService(session)
    result = await service.get_news_by_id(news_id=news_id)
    await service.add_view_to_news(news_id=news_id)
    return result


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/ai_prompt/set")
async def set_ai_prompt(prompt: str, user_email: str, session: Annotated[AsyncSession, Depends(get_session)]) -> None:
    """ Set default AI prompt for the user."""
    service = AccountService(session)
    return await service.set_prompt(account_email=user_email, prompt=prompt)


@app.get("/account_details/{user_email}")
async def get_account_details(
    user_email: str, session: Annotated[AsyncSession, Depends(get_session)]
) -> AccountDetails:
    """ Return account details for the user."""
    service = AccountService(session)
    return await service.get_account_details(account_email=user_email)


@app.get("/get_latest_pick/{user_email}")
async def get_latest_pick(
    user_email: str, session: Annotated[AsyncSession, Depends(get_session)]
) -> list[ParsedNewsBasic]:
    """ Get latest pick for the user. The time is considered as the creation date of the pick."""
    service = NewsService(session)
    return await service.get_latest_pick_news(user_email=user_email)


@app.get("/get_pick_news/{pick_hash}")
async def get_pick_news(
    pick_hash: str, session: Annotated[AsyncSession, Depends(get_session)]
) -> list[ParsedNewsBasic]:
    """
    Returns News without the content for the hash of the pick. Useful when you want to get title, description and
    other details for specific pick.
    """
    # TODO: Differ between nonexisting hashes and empty ones -> empty list | 404
    service = NewsService(session)
    return await service.get_news_by_pick_hash(pick_hash=pick_hash)


# Use cases:
# 1. User will go to the page, enters a prompt for an email -> POST set_prompt
# 2. User will go to the page, gets the prompt for an email and can change it -> GET account_details, POST set_prompt
# 3. User will go to the page by link that he gets from email -> GET get_pick_news
# 4. User will enter an email in the page and get the latest pick -> GET get_latest_pick / Alternative GET hash for pick and use it in second request
