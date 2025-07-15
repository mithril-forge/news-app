import asyncio
import datetime
import os
import pathlib
from datetime import timedelta

import dramatiq
import structlog
from dramatiq.brokers.redis import RedisBroker

from core.engine import get_session_context
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel
from features.input_news_processing.archive.local_archive import LocalArchive
from features.input_news_processing.services.article_generation_service import ArticleGenerationService
from news_processing import get_input_news_and_parse

logger = structlog.get_logger()
# Simple Redis broker setup
redis_broker = RedisBroker(url="redis://redis:6379")
dramatiq.set_broker(redis_broker)


@dramatiq.actor
async def scrap_articles_task(hours_delta: int) -> None:
    """
    Scraps new articles for passed timedelta and saves them to DB. If there is existing one,
    it adjusts the article in DB
    """
    # TODO: Maybe input for new functions should be input_news ids
    logger.info("Starting to parse input news")
    delta = datetime.timedelta(hours=hours_delta)
    news_ids = await get_input_news_and_parse(adjust_parse_date=True, delta=delta)
    choose_connected_articles_task.send(input_news_ids=news_ids)
    logger.info("Successfully parsed input news")


@dramatiq.actor
async def choose_connected_articles_task(input_news_ids: list[int]):
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
    for parsed_news_id in parsed_news_ids:
        regenerate_parsed_news_task.send(parsed_news_id=parsed_news_id)
    choose_new_articles_task.send(input_news_ids=input_news_ids)
    logger.info(f"Successfully created regeneration tasks of {len(parsed_news_ids)} articles.")

@dramatiq.actor
async def choose_new_articles_task(input_news_ids: list[int]):
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
        input_news_lists = await article_generation_service.pick_corresponding_input_news(
            input_news_ids=input_news_ids)
    for input_news_list in input_news_lists:
        generate_article_task.send(input_news_ids=input_news_list)
    logger.info(f"Successfully created creations tasks of {len(input_news_lists)} articles.")

@dramatiq.actor
async def generate_article_task(input_news_ids: list[int]):
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
    generate_picture_for_news.send(parsed_news_id=saved_news.id)


@dramatiq.actor
async def regenerate_parsed_news_task(parsed_news_id: int):
    """"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("You need to provide GEMINI_API_KEY to use the model.")
    with get_session_context() as db_session:
        archive = LocalArchive(target_location=pathlib.Path("/tmp"))
        article_generation_service = ArticleGenerationService(session=db_session, archive=archive,
                                                              ai_model=GeminiAIModel(api_key=gemini_api_key))
        await article_generation_service.enrich_existing_article(parsed_news_id=parsed_news_id)


@dramatiq.actor
async def generate_picture_for_news(parsed_news_id: int):
    """"""
    pass

