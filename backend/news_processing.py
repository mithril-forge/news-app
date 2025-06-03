#!/usr/bin/env python
import asyncio
import argparse
import os
import pathlib
import tempfile
import logging
from datetime import datetime, timedelta

from core.engine import get_session_context
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel
from features.input_news_processing.ai_library.openai_model import OpenAIModel
from features.input_news_processing.archive.local_archive import LocalArchive
from features.input_news_processing.services.article_generation_service import ArticleGenerationService
from features.input_news_processing.services.input_news_service import InputNewsService
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Starting parsing")

async def get_input_news_and_parse(adjust_parse_date: bool = True, delta: timedelta = timedelta(days=1)):
    """ Official scenario that will be used to parse new input news and generates the parsed ones from them"""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    local_archive_folder = os.getenv("LOCAL_ARCHIVE_FOLDER")
    if gemini_api_key is None:
        raise ValueError("You need to provide GEMINI_API_KEY to use the model")
    if local_archive_folder is None:
        raise ValueError("You need to provide LOCAL_ARCHIVE_FOLDER")
    local_archive = LocalArchive(target_location=pathlib.Path(local_archive_folder))

    async with get_session_context() as session:
        input_news_service = InputNewsService(session=session, archive=local_archive)
        if adjust_parse_date:
            latest_timestamp = await input_news_service.get_latest_timestamp()
            if latest_timestamp is not None:
                now = datetime.utcnow()
                time_since_latest = now - latest_timestamp

                if time_since_latest < delta:
                    delta = time_since_latest
        await input_news_service.scrap_and_save_input_news(delta=delta)

async def generate_and_connect_news(delta: timedelta):
    local_archive_folder = os.getenv("LOCAL_ARCHIVE_FOLDER")
    if local_archive_folder is None:
        raise ValueError("You need to provide LOCAL_ARCHIVE_FOLDER")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        raise ValueError("You need to provide GEMINI_API_KEY to use the model.")
    local_archive = LocalArchive(target_location=pathlib.Path(local_archive_folder))
    async with get_session_context() as session:
        article_generation_service = ArticleGenerationService(
            session=session,
            archive=local_archive,
            ai_model=GeminiAIModel(api_key=gemini_api_key)
        )
        # TODO: Fix connection and enable again
        #await session.flush()
        #await article_generation_service.connect_existing_news(delta=delta)
        await session.flush()
        await article_generation_service.creates_new_news(delta=delta)


async def generate_picture_for_news(news_id: int, commit_transaction: bool = False) -> None:
    # TODO: Rework to support latest news without picture instead of passing ID
    """ Generates picture for the news with specific ID"""
    open_ai_key = os.getenv("OPEN_AI_API_KEY")
    if open_ai_key is None:
        raise ValueError("You need to provide OPEN_AI_API_KEY to use the model")

    tmp_dir = tempfile.mkdtemp()
    local_archive = LocalArchive(target_location=pathlib.Path(tmp_dir))

    async with get_session_context(commit_transaction=commit_transaction) as session:
        article_generation_service = ArticleGenerationService(
            session=session,
            archive=local_archive,
            ai_model=OpenAIModel(api_key=open_ai_key)
        )
        await article_generation_service.generate_picture_for_news(news_id=news_id)


async def clear_old_input_news(delta: timedelta) -> None:
    """ Clear old input news and saves them to the archive"""
    local_archive_folder = os.getenv("LOCAL_ARCHIVE_FOLDER")
    if local_archive_folder is None:
        raise ValueError("You need to provide LOCAL_ARCHIVE_FOLDER")
    local_archive = LocalArchive(target_location=pathlib.Path(local_archive_folder))

    async with get_session_context() as session:
        input_news_service = InputNewsService(session=session, archive=local_archive)
        await input_news_service.clear_old_input_news(delta=delta)


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

    loop = asyncio.get_event_loop()

    if args.command == "parse":
        delta = timedelta(days=args.days)
        loop.run_until_complete(get_input_news_and_parse(adjust_parse_date=args.adjust_date, delta=delta))
        loop.run_until_complete(generate_and_connect_news(delta=delta))

    elif args.command == "generate-picture":
        loop.run_until_complete(generate_picture_for_news(news_id=args.news_id, commit_transaction=args.commit))
    elif args.command == "archive":
        delta = timedelta(days=args.days)
        loop.run_until_complete(clear_old_input_news(delta=delta))
    elif args.command == "generate":
        delta = timedelta(days=args.days)
        loop.run_until_complete(generate_and_connect_news(delta=delta))
    else:
        parser.print_help()

    loop.close()


if __name__ == "__main__":
    main()
