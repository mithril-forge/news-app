import asyncio
import datetime
import os
import pathlib
from datetime import timedelta

import dramatiq
import structlog
from dramatiq.brokers.redis import RedisBroker
from periodiq import PeriodiqMiddleware, cron

from backend.constants import CZECH_MONTHS, CZECH_DAYS
from backend.core.domain.schemas import AccountDetails
from core.domain.account_service import AccountService
from core.domain.news_service import NewsService
from features.input_news_processing.domain.ai_prompts import CUSTOM_ARTICLES_PROMPT
from features.input_news_processing.domain.pick_generation_service import PickGenerationService
from core.engine import get_session_context
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel
from features.input_news_processing.archive.local_archive import LocalArchive
from features.input_news_processing.domain.article_generation_service import (
    ArticleGenerationService,
)
from features.input_news_processing.domain.input_news_service import InputNewsService

logger = structlog.get_logger()
# Simple Redis broker setup
redis_broker = RedisBroker(url="redis://redis:6379")  # type: ignore[no-untyped-call]
dramatiq.set_broker(redis_broker)
redis_broker.add_middleware(PeriodiqMiddleware(skip_delay=30))  # type: ignore[no-untyped-call]


@dramatiq.actor(periodic=cron("00 20 * * *"))
def scrap_articles_task(hours_delta: int = 24) -> None:
    """
    Scraps new articles for passed timedelta and saves them to DB. If there is existing one,
    it adjusts the article in DB
    """
    logger.info(f"Starting scrap_articles_task with hours_delta: {hours_delta}")
    asyncio.run(async_scrap_articles_task(hours_delta=hours_delta))
    logger.info(f"Ended scrap_articles_task with hours_delta: {hours_delta}")


async def async_scrap_articles_task(hours_delta: int) -> None:
    """Async wrapper for scrap_articles_task"""
    delta = datetime.timedelta(hours=hours_delta)
    local_archive_folder = os.getenv("LOCAL_ARCHIVE_FOLDER")
    if local_archive_folder is None:
        logger.error("LOCAL_ARCHIVE_FOLDER environment variable not set")
        raise ValueError("You need to provide LOCAL_ARCHIVE_FOLDER")
    local_archive = LocalArchive(target_location=pathlib.Path(local_archive_folder))
    async with get_session_context() as session:
        input_news_service = InputNewsService(session=session, archive=local_archive)
        result = await input_news_service.scrap_and_save_input_news(delta=delta, adjust_parse_date=True)
        news_ids = [res.id for res in result]
    logger.info(f"Parsed {len(news_ids)} news items: {news_ids}, sending to connection task")
    choose_connected_articles_task.send(input_news_ids=news_ids)


@dramatiq.actor(max_retries=1)
def choose_connected_articles_task(input_news_ids: list[int]) -> None:
    """
    It's querying the AI model if there are any passed input_news that can be connected and enrich older parsed news.
    Then it starts new task to generate new articles from the nonconnectable input_news
    """
    logger.info(f"Starting choose_connected_articles_task with {len(input_news_ids)} news items: {input_news_ids}")
    asyncio.run(async_choose_connected_articles_task(input_news_ids))
    logger.info("Ended choose_connected_articles_task")


async def async_choose_connected_articles_task(input_news_ids: list[int]) -> None:
    """Async wrapper"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("You need to provide GEMINI_API_KEY to use the model.")
    async with get_session_context() as db_session:
        archive = LocalArchive(target_location=pathlib.Path("/tmp"))
        article_generation_service = ArticleGenerationService(
            session=db_session,
            archive=archive,
            ai_model=GeminiAIModel(api_key=gemini_api_key),
        )
        parsed_news_ids = await article_generation_service.connect_input_news_to_existing_articles(
            input_news_ids=input_news_ids
        )
        logger.info(f"Created {len(parsed_news_ids)} regeneration tasks: {parsed_news_ids}")
        for parsed_news_id in parsed_news_ids:
            enrich_parsed_article_task.send(parsed_news_id=parsed_news_id)

    async with get_session_context() as db_session:
        input_news_service = InputNewsService(session=db_session, archive=archive)
        input_news_without_parsed = await input_news_service.get_input_news_by_ids_lite(
            input_news_ids=input_news_ids, has_parsed_news=False
        )
        input_news_ids = [inp.id for inp in input_news_without_parsed]
    choose_new_articles_task.send(input_news_ids=input_news_ids)
    logger.info(f"Successfully created regeneration tasks of {len(parsed_news_ids)} articles.")


@dramatiq.actor(max_retries=1)
def choose_new_articles_task(input_news_ids: list[int], input_news_hours: int = 72, news_limit: int = 20) -> None:
    """Task that takes passed input_news_ids also query for the nonconnected older input news (by param delta).
    Then it queries AI model to choose new parsed articles and creates tasks for their generation"""
    logger.info(f"Starting choose_new_articles_task with {len(input_news_ids)} news items: {input_news_ids}")
    asyncio.run(
        async_choose_new_articles_task(
            input_news_ids=input_news_ids,
            input_news_hours=input_news_hours,
            news_limit=news_limit,
        )
    )
    logger.info("Ended choose_new_articles_task")


async def async_choose_new_articles_task(
        input_news_ids: list[int], input_news_hours: int = 72, news_limit: int = 20
) -> None:
    """Async wrapper"""
    input_news_delta = timedelta(hours=input_news_hours)
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("You need to provide GEMINI_API_KEY to use the model.")
    async with get_session_context() as db_session:
        archive = LocalArchive(target_location=pathlib.Path("/tmp"))
        article_generation_service = ArticleGenerationService(
            session=db_session,
            archive=archive,
            ai_model=GeminiAIModel(api_key=gemini_api_key),
        )
        input_news_service = InputNewsService(session=db_session, archive=archive)
        input_news_older = await input_news_service.get_input_news_by_delta(
            delta=input_news_delta, has_parsed_news=False
        )
        input_news_ids += [news.id for news in input_news_older if news.id not in input_news_ids]
        logger.info(f"Processing {len(input_news_ids)} total news items: {input_news_ids}")
        input_news_lists = await article_generation_service.choose_input_news_for_new_articles(
            input_news_ids=input_news_ids, news_limit=news_limit
        )

    logger.info(f"Created {len(input_news_lists)} generation tasks: {input_news_lists}")
    for input_news_list in input_news_lists:
        generate_article_task.send(input_news_ids=input_news_list)
    logger.info(f"Successfully created creations tasks of {len(input_news_lists)} articles.")


@dramatiq.actor(max_retries=1)
def generate_article_task(input_news_ids: list[int]) -> None:
    """Tasks that takes input_news_ids and queries the AI model for the new parsed article"""
    logger.info(f"Starting generate_article_task with {len(input_news_ids)} news items: {input_news_ids}")
    asyncio.run(async_generate_article_task(input_news_ids))
    logger.info("Ended generate_article_task")


async def async_generate_article_task(input_news_ids: list[int]) -> None:
    """Async wrapper"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("You need to provide GEMINI_API_KEY to use the model.")
    async with get_session_context() as db_session:
        archive = LocalArchive(target_location=pathlib.Path("/tmp"))
        article_generation_service = ArticleGenerationService(
            session=db_session,
            archive=archive,
            ai_model=GeminiAIModel(api_key=gemini_api_key),
        )
        saved_news = await article_generation_service.create_new_article_from_input_news(input_news_ids=input_news_ids)
    logger.info(f"Generated article {saved_news.id}, sending to picture generation")
    generate_and_attach_image_to_news.send(parsed_news_id=saved_news.id)


@dramatiq.actor(max_retries=1)
def enrich_parsed_article_task(parsed_news_id: int) -> None:
    """
    Task that takes parsed news with updated information (input_news etc.) and queries the
    AI model to update this article
    """
    logger.info(f"Starting enrich_parsed_article_task for news {parsed_news_id}")
    asyncio.run(async_enrich_parsed_article_task(parsed_news_id))
    logger.info(f"Ended enrich_parsed_article_task for news {parsed_news_id}")


async def async_enrich_parsed_article_task(parsed_news_id: int) -> None:
    """Aync wrapper"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("You need to provide GEMINI_API_KEY to use the model.")
    async with get_session_context() as db_session:
        archive = LocalArchive(target_location=pathlib.Path("/tmp"))
        article_generation_service = ArticleGenerationService(
            session=db_session,
            archive=archive,
            ai_model=GeminiAIModel(api_key=gemini_api_key),
        )
        await article_generation_service.enrich_existing_article(parsed_news_id=parsed_news_id)


@dramatiq.actor
def generate_and_attach_image_to_news(parsed_news_id: int) -> None:
    """Task for the picture generation"""
    logger.info(f"Starting generate_and_attach_image_to_news for news {parsed_news_id}")
    asyncio.run(async_generate_picture_for_news(parsed_news_id))
    logger.info(f"Ended generate_and_attach_image_to_news for news {parsed_news_id}")


async def async_generate_picture_for_news(parsed_news_id: int) -> None:
    """Async wrapper"""
    pass


@dramatiq.actor(periodic=cron("00 08 * * *"))
def distribute_daily_picks_task() -> None:
    """Start creation and distribution of daily picks from previous day. Wrapper for the logic itself."""
    logger.info("Starting to distribute daily picks for all users.")
    users = asyncio.run(async_distribute_daily_picks_task())
    logger.info(f"Successfully distributed daily pick tasks for {len(users)} users.")


async def async_distribute_daily_picks_task() -> list[AccountDetails]:
    """ Start creation and distribution of daily picks from previous day."""
    date = datetime.date.today() - timedelta(days=1)
    async with get_session_context() as db_session:
        account_service = AccountService(session=db_session)
        users = await account_service.get_accounts()
    for user in users:
        create_daily_pick_for_user.send(user_id=user.id, user_email=user.email, date=date, prompt=user.prompt)
    return users


@dramatiq.actor
def create_daily_pick_for_user(account_id: int, user_email: str, date: datetime.date, prompt: str) -> None:
    """ Async wrapper for the generation of daily task for user."""
    logger.info(f"Starting daily pick task for user: {account_id} and date {date}")
    asyncio.run(async_create_daily_pick_for_user(account_id=account_id, user_email=user_email, date=date, prompt=prompt))
    logger.info(f"Successfully generated daily pick for user: {account_id}")


async def async_create_daily_pick_for_user(account_id: int, user_email: str, date: datetime.date, prompt: str) -> None:
    """Create a daily pick for a user."""
    czech_date_str = f"{CZECH_DAYS[date.weekday()]}, {date.day}. {CZECH_MONTHS[date.month]} {date.year}"
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("You need to provide GEMINI_API_KEY to use the model.")
    async with get_session_context() as db_session:
        gemini_ai_model = GeminiAIModel(api_key=gemini_api_key)
        news_service = NewsService(session=db_session)
        pick_generation_service = PickGenerationService(session=db_session)
        prompt_formatted = CUSTOM_ARTICLES_PROMPT.format(prompt=prompt)
        parsed_news = await news_service.get_news_titles_by_date(date=date)
        files = ArticleGenerationService.save_pydantic_lists_as_files(parsed_news=parsed_news)
        result = await gemini_ai_model.prompt_model(files=files, prompt=prompt_formatted, response_model=list[int])
        logger.info(f"Successfully generated daily pick for user {user_email} with news ids: {result}")
        pick_id = await pick_generation_service.save_pick(
            account_id=account_id, date=date, description=f"Denní výběr pro {czech_date_str}"
        )
        await pick_generation_service.connect_news_to_pick(pick_id=pick_id, news_ids=result)


async def send_daily_pick_for_user(user_email: str) -> None:
    """Send a daily pick for a user."""
    pass
