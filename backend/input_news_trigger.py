import asyncio
import os
import pathlib
import tempfile
import argparse
from datetime import datetime, timedelta

from core.engine import get_session_context
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel
from features.input_news_processing.ai_library.openai_model import OpenAIModel
from features.input_news_processing.archive.local_archive import LocalArchive
from features.input_news_processing.services.article_generation_service import ArticleGenerationService
from features.input_news_processing.services.input_news_service import InputNewsService
from core.logger import create_logger

logger = create_logger(__name__)


async def get_input_news(local_archive: LocalArchive, adjust_parse_date: bool = True,
                         delta: timedelta = timedelta(days=1)):
    """Official scenario that will be used to parse new input news"""
    logger.info(f"Getting input news with delta: {delta}, adjust_parse_date: {adjust_parse_date}")
    async with get_session_context() as session:
        input_news_service = InputNewsService(session=session, archive=local_archive)
        if adjust_parse_date:
            latest_timestamp = await input_news_service.get_latest_timestamp()
            if latest_timestamp is not None:
                now = datetime.utcnow()
                time_since_latest = now - latest_timestamp
                logger.debug(f"Latest timestamp: {latest_timestamp}, time since: {time_since_latest}")

                if time_since_latest < delta:
                    delta = time_since_latest
                    logger.info(f"Adjusted delta to: {delta}")

        result = await input_news_service.scrap_and_save_input_news(delta=delta)
        logger.info(f"Successfully retrieved {len(result)} input news items")


async def parse_input_news(local_archive: LocalArchive, gemini_api_key: str,
                           delta: timedelta = timedelta(days=1)):
    """Parse input news using Gemini AI model"""
    logger.info(f"Parsing input news with delta: {delta}")
    async with get_session_context() as session:
        article_generation_service = ArticleGenerationService(
            session=session,
            archive=local_archive,
            ai_model=GeminiAIModel(api_key=gemini_api_key)
        )
        logger.info("Connecting existing news...")
        connected_news = await article_generation_service.connect_existing_news(delta=delta)
        logger.info(f"Connected {len(connected_news)} existing news articles")

        session.flush()

        logger.info("Creating new news...")
        new_news = await article_generation_service.creates_new_news(delta=delta)
        logger.info(f"Created {len(new_news)} new news articles")


async def generate_picture_for_news(news_id: int, commit_transaction: bool = False) -> None:
    """Generate picture for specific news article"""
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
        await article_generation_service.generate_picture_for_news(news_id=news_id)
        logger.info(f"Picture generation completed for news ID: {news_id}")


def create_local_archive() -> LocalArchive:
    """Create a local archive with temporary directory"""
    tmp_dir = tempfile.mkdtemp()
    logger.info(f"Created local archive at: {tmp_dir}")
    return LocalArchive(target_location=pathlib.Path(tmp_dir))


def validate_api_keys():
    """Validate required API keys"""
    logger.debug("Validating API keys")
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if gemini_api_key is None:
        logger.error("GEMINI_API_KEY environment variable not set")
        raise ValueError("You need to provide GEMINI_API_KEY to use the model")
    logger.info("API keys validated successfully")
    return gemini_api_key


async def main():
    parser = argparse.ArgumentParser(description="News Processing CLI")
    parser.add_argument(
        "command",
        choices=["get-input", "parse", "generate-picture", "full-pipeline"],
        help="Command to execute"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of days to process (default: 1)"
    )
    parser.add_argument(
        "--news-id",
        type=int,
        help="News ID for picture generation"
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        help="Commit transaction to database"
    )
    parser.add_argument(
        "--no-adjust-date",
        action="store_true",
        help="Don't adjust parse date based on latest timestamp"
    )

    args = parser.parse_args()
    logger.info(f"Starting news processing CLI with command: {args.command}")

    try:
        gemini_api_key = validate_api_keys()
        local_archive = create_local_archive()
        delta = timedelta(days=args.days)

        if args.command == "get-input":
            logger.info(f"Executing get-input command for {args.days} day(s)")
            print(f"Getting input news for the last {args.days} day(s)...")
            await get_input_news(
                local_archive=local_archive,
                adjust_parse_date=not args.no_adjust_date,
                delta=delta
            )
            print("Input news retrieval completed.")

        elif args.command == "parse":
            logger.info(f"Executing parse command for {args.days} day(s)")
            print(f"Parsing input news for the last {args.days} day(s)...")
            await parse_input_news(
                local_archive=local_archive,
                gemini_api_key=gemini_api_key,
                delta=delta
            )
            print("News parsing completed.")

        elif args.command == "generate-picture":
            if args.news_id is None:
                logger.error("News ID is required for picture generation")
                raise ValueError("--news-id is required for picture generation")
            logger.info(f"Executing generate-picture command for news ID: {args.news_id}")
            print(f"Generating picture for news ID: {args.news_id}")
            await generate_picture_for_news(
                news_id=args.news_id,
                commit_transaction=args.commit
            )
            print("Picture generation completed.")

        elif args.command == "full-pipeline":
            logger.info(f"Executing full-pipeline command for {args.days} day(s)")
            print(f"Running full pipeline for the last {args.days} day(s)...")
            print("Step 1: Getting input news...")
            await get_input_news(
                local_archive=local_archive,
                adjust_parse_date=not args.no_adjust_date,
                delta=delta
            )
            print("Step 2: Parsing input news...")
            await parse_input_news(
                local_archive=local_archive,
                gemini_api_key=gemini_api_key,
                delta=delta
            )
            print("Full pipeline completed.")

        logger.info(f"Successfully completed command: {args.command}")

    except Exception as e:
        logger.error(f"Error executing command {args.command}: {e}")
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)