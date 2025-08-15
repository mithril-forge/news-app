import asyncio
import datetime
import os
import pathlib
from datetime import timedelta

import dramatiq
import structlog
from dramatiq.brokers.redis import RedisBroker
from periodiq import PeriodiqMiddleware, cron

from core.domain.news_service import NewsService
from core.engine import get_session_context
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel
from features.input_news_processing.archive.local_archive import LocalArchive
from features.input_news_processing.domain.article_generation_service import (
    ArticleGenerationService,
)
from features.input_news_processing.domain.input_news_service import InputNewsService

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

logger = structlog.get_logger()
# Simple Redis broker setup
redis_broker = RedisBroker(url=REDIS_URL)  # type: ignore[no-untyped-call]
redis_broker.add_middleware(PeriodiqMiddleware(skip_delay=30))  # type: ignore[no-untyped-call]
dramatiq.set_broker(redis_broker)

# Get cron schedule from environment variable (default: 8 PM daily)
SCRAP_ARTICLES_CRON = os.getenv("SCRAP_ARTICLES_CRON", "00 20 * * *")
REFRESH_MATERIALIZED_VIEW_CRON = os.getenv("REFRESH_MATERIALIZED_VIEW_CRON", "*/5 * * * *")


@dramatiq.actor(periodic=cron(SCRAP_ARTICLES_CRON))
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
def choose_new_articles_task(
        input_news_ids: list[int], input_news_hours: int | None = None, news_limit: int | None = None
) -> None:
    """Task that takes passed input_news_ids also query for the nonconnected older input news (by param delta).
    Then it queries AI model to choose new parsed articles and creates tasks for their generation"""
    if input_news_hours is None:
        input_news_hours = int(os.getenv("INPUT_NEWS_HOURS", "72"))
    if news_limit is None:
        news_limit = int(os.getenv("INPUT_NEWS_LIMIT", "20"))
    logger.info(f"Starting choose_new_articles_task with {len(input_news_ids)} news items: {input_news_ids}")
    asyncio.run(
        async_choose_new_articles_task(
            input_news_ids=input_news_ids,
            input_news_hours=input_news_hours,
            news_limit=news_limit,
        )
    )
    logger.info("Ended choose_new_articles_task")


async def async_choose_new_articles_task(input_news_ids: list[int], input_news_hours: int, news_limit: int) -> None:
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
    for init_news_pick in input_news_lists:
        generate_article_task.send(input_news_ids=init_news_pick.input_news_ids, importancy=init_news_pick.importancy)
    logger.info(f"Successfully created creations tasks of {len(input_news_lists)} articles.")


@dramatiq.actor(max_retries=1)
def generate_article_task(input_news_ids: list[int], importancy: int) -> None:
    """Tasks that takes input_news_ids and queries the AI model for the new parsed article"""
    logger.info(
        f"Starting generate_article_task with {len(input_news_ids)} news items: {input_news_ids} "
        f"and importancy: {importancy}"
    )
    asyncio.run(async_generate_article_task(input_news_ids, importancy))
    logger.info("Ended generate_article_task")


async def async_generate_article_task(input_news_ids: list[int], importancy: int) -> None:
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
        saved_news = await article_generation_service.create_new_article_from_input_news(
            input_news_ids=input_news_ids, importancy=importancy
        )
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


@dramatiq.actor(
    periodic=cron(REFRESH_MATERIALIZED_VIEW_CRON),
    max_retries=10,
    min_backoff=30000,  # 30 seconds
    max_backoff=300000  # 5 minutes
)
def refresh_materialized_view():
    """ Refreshes materialized view each few seconds"""
    logger.info("Refreshing materialized view of parsed news...")
    asyncio.run(async_refresh_materialized_view())
    logger.info("Materialized view of parsed news finished.")


async def async_refresh_materialized_view():
    """ Async wrapper"""
    async with get_session_context() as db_session:
        news_service = NewsService(session=db_session)
        await news_service.refresh_materialized_view()
