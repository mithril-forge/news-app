import asyncio
import datetime
import os
import pathlib
from datetime import timedelta

import dramatiq
import structlog
from dramatiq.brokers.redis import RedisBroker
from periodiq import PeriodiqMiddleware, cron

from core.engine import get_session_context
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel
from features.input_news_processing.archive.local_archive import LocalArchive
from features.input_news_processing.services.article_generation_service import ArticleGenerationService
from features.input_news_processing.services.input_news_service import InputNewsService
from news_processing import get_input_news_and_parse

logger = structlog.get_logger()
# Simple Redis broker setup
redis_broker = RedisBroker(url="redis://redis:6379")
dramatiq.set_broker(redis_broker)
redis_broker.add_middleware(PeriodiqMiddleware(skip_delay=30))


@dramatiq.actor(periodic=cron('20 13 * * *'))
def scrap_articles_task(hours_delta: int = 24) -> None:
    """
    Scraps new articles for passed timedelta and saves them to DB. If there is existing one,
    it adjusts the article in DB
    """
    logger.info(f"Starting scrap_articles_task with hours_delta: {hours_delta}")
    asyncio.run(async_scrap_articles_task(hours_delta=hours_delta))
    logger.info(f"Ended scrap_articles_task with hours_delta: {hours_delta}")


async def async_scrap_articles_task(hours_delta: int) -> None:
    delta = datetime.timedelta(hours=hours_delta)
    news_ids = await get_input_news_and_parse(adjust_parse_date=True, delta=delta)
    logger.info(f"Parsed {len(news_ids)} news items: {news_ids}, sending to connection task")
    choose_connected_articles_task.send(input_news_ids=news_ids)


@dramatiq.actor(max_retries=1)
def choose_connected_articles_task(input_news_ids: list[int]):
    """Simple data processing task"""
    logger.info(f"Starting choose_connected_articles_task with {len(input_news_ids)} news items: {input_news_ids}")
    asyncio.run(async_choose_connected_articles_task(input_news_ids))
    logger.info(f"Ended choose_connected_articles_task")


async def async_choose_connected_articles_task(input_news_ids: list[int]):
    """Simple data processing task"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("You need to provide GEMINI_API_KEY to use the model.")
    async with get_session_context() as db_session:
        archive = LocalArchive(target_location=pathlib.Path("/tmp"))
        article_generation_service = ArticleGenerationService(session=db_session, archive=archive,
                                                              ai_model=GeminiAIModel(api_key=gemini_api_key))
        parsed_news_ids = await article_generation_service.initial_connect_new_input_news(
            input_news_ids=input_news_ids)

    logger.info(f"Created {len(parsed_news_ids)} regeneration tasks: {parsed_news_ids}")
    for parsed_news_id in parsed_news_ids:
        regenerate_parsed_news_task.send(parsed_news_id=parsed_news_id)

    choose_new_articles_task.send(input_news_ids=input_news_ids)
    logger.info(f"Successfully created regeneration tasks of {len(parsed_news_ids)} articles.")


@dramatiq.actor(max_retries=1)
def choose_new_articles_task(input_news_ids: list[int], input_news_hours: int = 72):
    """Simple data processing task"""
    logger.info(f"Starting choose_new_articles_task with {len(input_news_ids)} news items: {input_news_ids}")
    asyncio.run(async_choose_new_articles_task(input_news_ids, input_news_hours))
    logger.info(f"Ended choose_new_articles_task")


async def async_choose_new_articles_task(input_news_ids: list[int], input_news_hours: int = 72):
    """Simple data processing task"""
    input_news_delta = timedelta(hours=input_news_hours)
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("You need to provide GEMINI_API_KEY to use the model.")
    async with get_session_context() as db_session:
        archive = LocalArchive(target_location=pathlib.Path("/tmp"))
        article_generation_service = ArticleGenerationService(session=db_session, archive=archive,
                                                              ai_model=GeminiAIModel(api_key=gemini_api_key))
        input_news_service = InputNewsService(session=db_session, archive=archive)
        input_news_older = await input_news_service.get_input_news_by_delta(delta=input_news_delta,
                                                                            has_parsed_news=False)
        input_news_ids += [news.id for news in input_news_older if news.id not in input_news_ids]
        logger.info(f"Processing {len(input_news_ids)} total news items: {input_news_ids}")
        input_news_lists = await article_generation_service.pick_corresponding_input_news(
            input_news_ids=input_news_ids, news_limit=5)

    logger.info(f"Created {len(input_news_lists)} generation tasks: {input_news_lists}")
    for input_news_list in input_news_lists:
        generate_article_task.send(input_news_ids=input_news_list)
    logger.info(f"Successfully created creations tasks of {len(input_news_lists)} articles.")


@dramatiq.actor(max_retries=1)
def generate_article_task(input_news_ids: list[int]):
    """ """
    logger.info(f"Starting generate_article_task with {len(input_news_ids)} news items: {input_news_ids}")
    asyncio.run(async_generate_article_task(input_news_ids))
    logger.info(f"Ended generate_article_task")


async def async_generate_article_task(input_news_ids: list[int]):
    """ """
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("You need to provide GEMINI_API_KEY to use the model.")
    async with get_session_context() as db_session:
        archive = LocalArchive(target_location=pathlib.Path("/tmp"))
        article_generation_service = ArticleGenerationService(session=db_session, archive=archive,
                                                              ai_model=GeminiAIModel(api_key=gemini_api_key))
        saved_news = await article_generation_service.create_new_article(input_news_ids=input_news_ids)
    logger.info(f"Generated article {saved_news.id}, sending to picture generation")
    generate_picture_for_news.send(parsed_news_id=saved_news.id)


@dramatiq.actor(max_retries=1)
def regenerate_parsed_news_task(parsed_news_id: int):
    """"""
    logger.info(f"Starting regenerate_parsed_news_task for news {parsed_news_id}")
    asyncio.run(async_regenerate_parsed_news_task(parsed_news_id))
    logger.info(f"Ended regenerate_parsed_news_task for news {parsed_news_id}")


async def async_regenerate_parsed_news_task(parsed_news_id: int):
    """"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("You need to provide GEMINI_API_KEY to use the model.")
    async with get_session_context() as db_session:
        archive = LocalArchive(target_location=pathlib.Path("/tmp"))
        article_generation_service = ArticleGenerationService(session=db_session, archive=archive,
                                                              ai_model=GeminiAIModel(api_key=gemini_api_key))
        await article_generation_service.enrich_existing_article(parsed_news_id=parsed_news_id)


@dramatiq.actor
def generate_picture_for_news(parsed_news_id: int):
    """"""
    logger.info(f"Starting generate_picture_for_news for news {parsed_news_id}")
    asyncio.run(async_generate_picture_for_news(parsed_news_id))
    logger.info(f"Ended generate_picture_for_news for news {parsed_news_id}")


async def async_generate_picture_for_news(parsed_news_id: int):
    """"""
    pass