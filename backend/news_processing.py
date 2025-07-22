#!/usr/bin/env python
import asyncio
import argparse
import os
import pathlib
import tempfile
import logging
from datetime import datetime, timedelta

import structlog

from core.engine import get_session_context
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel
from features.input_news_processing.ai_library.openai_model import OpenAIModel
from features.input_news_processing.archive.local_archive import LocalArchive
from features.input_news_processing.domain.article_generation_service import ArticleGenerationService
from features.input_news_processing.domain.input_news_service import InputNewsService

logger = structlog.get_logger()


async def get_input_news_and_parse(adjust_parse_date: bool = True, delta: timedelta = timedelta(days=1)) -> list[int]:
    """ Official scenario that will be used to parse new input news and generates the parsed ones from them by CLI"""
    logger.info(f"Starting CLI input news parsing with adjust_parse_date: {adjust_parse_date}, delta: {delta}")
    local_archive_folder = os.getenv("LOCAL_ARCHIVE_FOLDER")
    if local_archive_folder is None:
        logger.error("LOCAL_ARCHIVE_FOLDER environment variable not set")
        raise ValueError("You need to provide LOCAL_ARCHIVE_FOLDER")
    local_archive = LocalArchive(target_location=pathlib.Path(local_archive_folder))

    async with get_session_context() as session:
        input_news_service = InputNewsService(session=session, archive=local_archive)
        result = await input_news_service.scrap_and_save_input_news(delta=delta, adjust_parse_date=adjust_parse_date)
    return [news.id for news in result]


async def generate_and_connect_news(delta: timedelta):
    logger.info(f"Starting CLI news generation and connection with delta: {delta}")
    local_archive_folder = os.getenv("LOCAL_ARCHIVE_FOLDER")
    if local_archive_folder is None:
        logger.error("LOCAL_ARCHIVE_FOLDER environment variable not set")
        raise ValueError("You need to provide LOCAL_ARCHIVE_FOLDER")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("You need to provide GEMINI_API_KEY to use the model.")
    local_archive = LocalArchive(target_location=pathlib.Path(local_archive_folder))
    async with get_session_context() as session:
        article_generation_service = ArticleGenerationService(
            session=session,
            archive=local_archive,
            ai_model=GeminiAIModel(api_key=gemini_api_key)
        )
        input_news_service = InputNewsService(session=session, archive=local_archive)
        await session.flush()
        logger.info("Connecting existing news...")
        input_news = await input_news_service.get_input_news_by_delta(delta=delta, has_parsed_news=False)
        input_news_ids = [inp.id for inp in input_news]
        connected_news_ids = await article_generation_service.connect_input_news_to_existing_articles(
            input_news_ids=input_news_ids)
        logger.info(f"Parsed existing articles with ids picked for enrichment: {[connected_news_ids]}")
        for news_id in connected_news_ids:
            logger.info(f"Enriching article {news_id}")
            await article_generation_service.enrich_existing_article(parsed_news_id=news_id)
        await session.flush()
        logger.info("Creating new news...")
        input_news = await input_news_service.get_input_news_by_delta(delta=delta, has_parsed_news=False)
        input_news_ids = [inp.id for inp in input_news]
        new_news_groups = await article_generation_service.choose_input_news_for_new_articles(input_news_ids=input_news_ids)
        logger.info(f"Input news groups picked for enrichment: {[new_news_groups]}")
        for group in new_news_groups:
            logger.info(f"Creating news articles with ids: {group}")
            await article_generation_service.create_new_article_from_input_news(input_news_ids=group)


async def generate_picture_for_news(news_id: int, commit_transaction: bool = False) -> None:
    # TODO: Rework to support latest news without picture instead of passing ID
    """ Generates picture for the news with specific ID"""
    logger.info(f"Generating picture for news ID: {news_id}, commit: {commit_transaction}")
    open_ai_key = os.getenv("OPEN_AI_API_KEY")
    if open_ai_key is None:
        logger.error("OPEN_AI_API_KEY environment variable not set")
        raise ValueError("You need to provide OPEN_AI_API_KEY to use the model")

    tmp_dir = tempfile.mkdtemp()
    local_archive = LocalArchive(target_location=pathlib.Path(tmp_dir))

    async with get_session_context(commit_transaction=commit_transaction) as session:
        article_generation_service = ArticleGenerationService(
            session=session,
            archive=local_archive,
            ai_model=OpenAIModel(api_key=open_ai_key)
        )
        await article_generation_service.generate_and_attach_image_to_news(news_id=news_id)
        logger.info(f"Picture generation completed for news ID: {news_id}")


async def clear_old_input_news(delta: timedelta) -> None:
    """ Clear old input news and saves them to the archive"""
    logger.info(f"Clearing old input news older than delta: {delta}")
    local_archive_folder = os.getenv("LOCAL_ARCHIVE_FOLDER")
    if local_archive_folder is None:
        logger.error("LOCAL_ARCHIVE_FOLDER environment variable not set")
        raise ValueError("You need to provide LOCAL_ARCHIVE_FOLDER")
    local_archive = LocalArchive(target_location=pathlib.Path(local_archive_folder))

    async with get_session_context() as session:
        input_news_service = InputNewsService(session=session, archive=local_archive)
        await input_news_service.clear_old_input_news(delta=delta)
        logger.info("Successfully cleared old input news")


def main():
    parser = argparse.ArgumentParser(description="News Processing CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Parse news command
    parse_parser = subparsers.add_parser("parse", help="Parse input news and generate new articles")
    parse_parser.add_argument("--days", type=int, default=1, help="Number of days to look back for news")
    parse_parser.add_argument("--adjust-date", action="store_true", help="Adjust parse date based on latest timestamp")
    # Generate news
    generate_parser = subparsers.add_parser("generate", help="")
    generate_parser.add_argument("--days", type=int, default=1)
    # Generate picture command
    picture_parser = subparsers.add_parser("generate-picture", help="Generate picture for a specific news article")
    picture_parser.add_argument("news_id", type=int, help="ID of the news article")
    picture_parser.add_argument("--commit", action="store_true", help="Commit transaction to database")

    # Archive old input news
    archive_parser = subparsers.add_parser("archive", help="Archive old input news")
    archive_parser.add_argument("--days", type=int, default=30,
                                help="News older than the delta and without parsed news will be archived.")

    args = parser.parse_args()
    logger.info(f"Executing command: {args.command}")

    loop = asyncio.get_event_loop()

    try:
        if args.command == "parse":
            delta = timedelta(days=args.days)
            logger.info(f"Running parse command with {args.days} days, adjust_date: {args.adjust_date}")
            loop.run_until_complete(get_input_news_and_parse(adjust_parse_date=args.adjust_date, delta=delta))
            loop.run_until_complete(generate_and_connect_news(delta=delta))

        elif args.command == "generate-picture":
            logger.info(f"Running generate-picture command for news ID: {args.news_id}")
            loop.run_until_complete(generate_picture_for_news(news_id=args.news_id, commit_transaction=args.commit))
        elif args.command == "archive":
            delta = timedelta(days=args.days)
            logger.info(f"Running archive command with {args.days} days")
            loop.run_until_complete(clear_old_input_news(delta=delta))
        elif args.command == "generate":
            delta = timedelta(days=args.days)
            logger.info(f"Running generate command with {args.days} days")
            loop.run_until_complete(generate_and_connect_news(delta=delta))
        else:
            logger.error("No command specified")
            parser.print_help()

        logger.info(f"Successfully completed command: {args.command}")

    except Exception as e:
        logger.error(f"Error executing command {args.command}: {e}")
        raise

    finally:
        loop.close()


if __name__ == "__main__":
    main()
