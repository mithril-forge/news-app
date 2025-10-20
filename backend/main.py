import datetime
import os
import time
from enum import Enum
from typing import Annotated, Any

import structlog
from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config import Environment
from core.domain.account_service import AccountService
from core.domain.email_service import EmailNewsletterService
from core.domain.news_service import NewsService
from core.domain.schemas import (
    AccountDetails,
    NewsPickResponse,
    ParsedNewsBasic,
    ParsedNewsResponseDetailed,
    TopicResponse,
)
from core.domain.topic_service import TopicService
from core.engine import get_session
from core.exceptions import (
    AccountDeletionException,
    AccountDeletionFailedException,
    AccountNotFoundException,
    TokenAlreadyUsedException,
    TokenExpiredException,
    TokenNotFoundException,
)
from core.presentation.schemas import AccountDeletionResponse, PickGenerationResponse
from features.input_news_processing.domain.pick_generation_service import PickGenerationService
from logger import init_logging

init_logging()
logger = structlog.get_logger()

environment = os.getenv("ENVIRONMENT")
logger.info(f"Environment: {environment}")

# Check if mocking is enabled via environment variable
use_mocked_ai = os.getenv("USE_MOCKED_AI", "false").lower() == "true"
logger.info(f"AI Mocking enabled: {use_mocked_ai}")

default_limits: list[str] = []

# Get CORS origins from environment variable
cors_origins_env = os.getenv("CORS_ALLOWED_ORIGINS")
origins = [origin.strip() for origin in cors_origins_env.split(",")] if cors_origins_env else []

if environment == Environment.DEVELOPMENT.value:
    origins = [
        "*",
    ]

FRONTEND_ACCOUNT_DELETION_URL = "https://tvujnovinar.cz/delete?token={plain_token}"


class NewsSortBy(str, Enum):
    """Enum for different news sorting options"""

    LATEST = "latest"  # Sort by created_at/updated_at DESC
    RELEVANCE = "relevance"  # Sort by relevance_score DESC


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
    sort_by: Annotated[NewsSortBy, Query(description="How to sort the news items")] = NewsSortBy.LATEST,
) -> list[ParsedNewsBasic]:
    """Get the latest news items with pagination"""
    service = NewsService(session)
    if sort_by == NewsSortBy.LATEST:
        return await service.get_latest_news(skip=skip, limit=limit)
    else:
        return await service.get_latest_news_by_relevancy(skip=skip, limit=limit)


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
    """Set default AI prompt for the user."""
    service = AccountService(session)
    return await service.set_prompt(account_email=user_email, prompt=prompt.strip())


@app.get("/account_details/{user_email}")
async def get_account_details(
    user_email: str, session: Annotated[AsyncSession, Depends(get_session)]
) -> AccountDetails | None:
    """Return account details for the user."""
    service = AccountService(session)
    return await service.get_account_details(account_email=user_email)


@app.get("/get_latest_pick/{user_email}")
async def get_latest_pick(user_email: str, session: Annotated[AsyncSession, Depends(get_session)]) -> NewsPickResponse:
    """Get all news articles from the latest pick for the user along with the original prompt."""
    service = NewsService(session)
    return await service.get_latest_pick_for_user(account_email=user_email)


@app.get("/get_pick_news/{pick_hash}")
async def get_pick_news(pick_hash: str, session: Annotated[AsyncSession, Depends(get_session)]) -> NewsPickResponse:
    """
    Returns News without the content for the hash of the pick along with the original prompt.
    Useful when you want to get title, description and other details for specific pick.
    """
    # TODO: Differ between nonexisting hashes and empty ones -> empty list | 404
    service = NewsService(session)
    return await service.get_pick_by_hash(pick_hash=pick_hash)


@app.post("/generate_pick")
async def generate_pick_endpoint(
    session: Annotated[AsyncSession, Depends(get_session)],
    user_email: Annotated[str | None, Form()] = None,
    prompt: Annotated[str | None, Form()] = None,
) -> PickGenerationResponse:
    """
    Unified pick generation endpoint that handles both anonymous and logged-in users.

    For logged-in users: Pass user_email, prompt is fetched from database
    For anonymous users: Pass prompt in form data, user_email should be None
    """
    service = PickGenerationService(session)

    if user_email is not None:
        pick_hash = await service.generate_pick_logged_in_user(
            user_email=user_email, bypass_daily_limit=False, news_age_in_hours=48
        )
        return PickGenerationResponse(hash=pick_hash, message="Pick generated successfully")

    elif prompt is not None:
        prompt = prompt.strip()
        pick_hash = await service.generate_pick_anonymous(prompt=prompt, news_age_in_hours=48)
        return PickGenerationResponse(hash=pick_hash, message="Pick generated successfully")
    else:
        raise HTTPException(status_code=400, detail="Either user_email or prompt must be provided.")


@app.post("/link_anonymous_pick_to_user")
async def link_anonymous_pick_to_user(
    user_email: Annotated[str, Form()],
    pick_hash: Annotated[str, Form()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Links an anonymous pick (by hash) to a user account."""
    service = NewsService(session)
    await service.link_anonymous_pick_to_user(user_email=user_email, pick_hash=pick_hash)


@app.exception_handler(AccountDeletionException)
async def account_deletion_exception_handler(request: Request, exc: AccountDeletionException) -> JSONResponse:
    """Global handler for account deletion exceptions"""

    status_code_map = {
        TokenNotFoundException: 404,
        AccountNotFoundException: 404,
        TokenAlreadyUsedException: 400,
        TokenExpiredException: 400,
        AccountDeletionFailedException: 500,
    }

    status_code = status_code_map.get(type(exc), 400)

    logger.error(f"Account deletion error: {exc.error_code} - {exc.message}")

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": exc.error_code,
            "message": exc.message,
        },
    )


@app.post("/account/request-deletion")
async def request_account_deletion(
    email: Annotated[str, Form()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AccountDeletionResponse:
    """
    Generate deletion token and send email with link.
    Always returns success to prevent email enumeration.
    """
    logger.info(f"Deletion requested for: {email}")
    brevo_api_key = os.getenv("BREVO_API_KEY")
    if brevo_api_key is None:
        logger.error("BREVO_API_KEY environment variable not set")
        raise ValueError("You need to provide BREVO_API_KEY to use the model.")
    try:
        account_service = AccountService(session=session)
        email_service = EmailNewsletterService(brevo_api_key=brevo_api_key)
        token_response = await account_service.create_deletion_token(email=email)

        deletion_url = FRONTEND_ACCOUNT_DELETION_URL.format(plain_token=token_response["plain_token"])
        await email_service.send_deletion_email(email, deletion_url)
        await session.commit()

    except AccountNotFoundException:
        pass

    return AccountDeletionResponse(message="Instrukce pro smazání byly odeslány na email.")


@app.delete("/account/execute-deletion")
async def execute_account_deletion(
    token: Annotated[str, Form()],  # Changed this line only
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AccountDeletionResponse:
    """
    Verify token and delete account.
    Exceptions handled by global exception handler.
    """
    logger.info("Executing account deletion")

    account_service = AccountService(session=session)

    await account_service.verify_and_delete_account(plain_token=token)  # Changed this

    await session.commit()

    logger.info("Account successfully deleted")

    return AccountDeletionResponse(message="Váš účet byl úspěšně smazán.")
