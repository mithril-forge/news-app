import asyncio
import datetime
import os
import pathlib
from datetime import timedelta

import dramatiq
import structlog
from dramatiq.brokers.redis import RedisBroker
from periodiq import PeriodiqMiddleware, cron

from core.domain.account_service import AccountService
from core.domain.email_service import EmailNewsletterService
from core.domain.news_service import NewsService
from core.domain.schemas import AccountDetails
from core.engine import get_session_context
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel
from features.input_news_processing.archive.local_archive import LocalArchive
from features.input_news_processing.domain.article_generation_service import (
    ArticleGenerationService,
)
from features.input_news_processing.domain.input_news_service import InputNewsService
from features.input_news_processing.domain.pick_generation_service import PickGenerationService

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

logger = structlog.get_logger()
# Simple Redis broker setup
redis_broker = RedisBroker(url=REDIS_URL)  # type: ignore[no-untyped-call]
redis_broker.add_middleware(PeriodiqMiddleware(skip_delay=30))  # type: ignore[no-untyped-call]
dramatiq.set_broker(redis_broker)

# Get cron schedule from environment variable (default: 8 PM daily)
SCRAP_ARTICLES_CRON = os.getenv("SCRAP_ARTICLES_CRON", "00 20 * * *")
REFRESH_MATERIALIZED_VIEW_CRON = os.getenv("REFRESH_MATERIALIZED_VIEW_CRON", "*/5 * * * *")
CONNECTING_PARSED_NEWS_LIMIT = int(os.getenv("CONNECTING_PARSED_NEWS_LIMIT", "24"))
CONNECTING_INPUT_NEWS_LIMIT = int(os.getenv("CONNECTING_INPUT_NEWS_LIMIT", "72"))
DAILY_PICK_GENERATION_CRON = os.getenv("DAILY_PICK_GENERATION_CRON", "00 06 * * *")


@dramatiq.actor(periodic=cron(SCRAP_ARTICLES_CRON))
def scrap_articles_task(hours_delta: int = 24) -> None:
    """
    Scraps new articles for passed timedelta and saves them to DB. If there is existing one,
    it adjusts the article in DB
    """
    logger.info(f"Starting scrap_articles_task with hours_delta: {hours_delta}")
    news_ids = asyncio.run(async_scrap_articles_task(hours_delta=hours_delta))
    choose_connected_articles_task.send(input_news_ids=news_ids)
    logger.info(f"Ended scrap_articles_task with hours_delta: {hours_delta}")


async def async_scrap_articles_task(hours_delta: int) -> list[int]:
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
    logger.info(f"Parsed {len(news_ids)} news items: {news_ids}")
    return news_ids


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
            input_news_ids=input_news_ids,
            input_news_hours_delta=CONNECTING_INPUT_NEWS_LIMIT,
            parsed_news_hours_delta=CONNECTING_PARSED_NEWS_LIMIT,
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
    max_backoff=300000,  # 5 minutes
)
def refresh_materialized_view() -> None:
    """Refreshes materialized view each few seconds"""
    logger.info("Refreshing materialized view of parsed news...")
    asyncio.run(async_refresh_materialized_view())
    logger.info("Materialized view of parsed news finished.")


async def async_refresh_materialized_view() -> None:
    """Async wrapper"""
    async with get_session_context() as db_session:
        news_service = NewsService(session=db_session)
        await news_service.refresh_materialized_view()


@dramatiq.actor(periodic=cron(DAILY_PICK_GENERATION_CRON))
def distribute_daily_picks_task() -> None:
    """Start creation and distribution of daily picks from previous day. Wrapper for the logic itself."""
    logger.info("Starting to distribute daily picks for all accounts.")
    accounts = asyncio.run(async_distribute_daily_picks_task())
    logger.info(f"Successfully distributed daily pick tasks for {len(accounts)} accounts.")


async def async_distribute_daily_picks_task() -> list[AccountDetails]:
    """Start creation and distribution of daily picks from previous day."""
    date = datetime.date.today() - timedelta(days=1)
    async with get_session_context() as db_session:
        account_service = AccountService(session=db_session)
        accounts = await account_service.get_accounts()
    for account in accounts:
        create_daily_pick_for_account.send(
            account_email=account.email,
            date=date.isoformat(),
        )
    return accounts


@dramatiq.actor
def create_daily_pick_for_account(account_email: str, date: str) -> None:
    """Async wrapper for the generation of daily task for account."""
    parsed_date = datetime.date.fromisoformat(date)
    logger.info(f"Starting daily pick task for account: {account_email} and date {parsed_date}")
    asyncio.run(async_create_daily_pick_for_account(account_email=account_email, date=parsed_date))


async def async_create_daily_pick_for_account(
    account_email: str,
    date: datetime.date,
) -> None:
    """Create a daily pick for an account using the centralized PickGenerationService."""
    czech_days = {
        0: "z pondělí",
        1: "z úterý",
        2: "ze středy",
        3: "ze čtvrtku",
        4: "z pátku",
        5: "ze soboty",
        6: "z neděle",
    }

    date_start = datetime.datetime.combine(date, datetime.time.min)
    now = datetime.datetime.now()
    hours_since_date_start = int((now - date_start).total_seconds() / 3600)

    day_name = czech_days[date.weekday()]
    description = f"Denní výběr zpráv {day_name}"

    async with get_session_context() as db_session:
        pick_generation_service = PickGenerationService(session=db_session)

        try:
            pick_hash = await pick_generation_service.generate_pick_logged_in_user(
                user_email=account_email,
                bypass_daily_limit=True,
                news_age_in_hours=hours_since_date_start,
                description=description,
            )
            logger.info(f"Successfully generated daily pick for account {account_email}: {pick_hash}")

            if pick_hash:
                send_daily_pick_email.send(account_email, pick_hash)
            else:
                logger.error(f"No pick_hash returned for account {account_email}")

        except Exception as e:
            logger.error(f"Failed to generate daily pick for account {account_email}: {e}")


@dramatiq.actor
def send_daily_pick_email(account_email: str, pick_hash: str) -> None:
    """Async wrapper for sending daily pick email."""
    logger.info(f"Starting email send task for account: {account_email} and pick: {pick_hash}")
    asyncio.run(async_send_daily_pick_for_account(account_email=account_email, pick_hash=pick_hash))


async def async_send_daily_pick_for_account(account_email: str, pick_hash: str) -> None:
    """Send a daily pick for an account."""
    brevo_api_key = os.getenv("BREVO_API_KEY")
    if brevo_api_key is None:
        logger.error("BREVO_API_KEY environment variable not set")
        raise ValueError("You need to provide BREVO_API_KEY to use the model.")
    async with get_session_context() as db_session:
        news_service = NewsService(db_session)
        account_service = AccountService(db_session)

        try:
            news_pick = await news_service.get_pick_by_hash(pick_hash=pick_hash)
            account = await account_service.get_account_details(account_email=account_email)
            if account is None:
                raise ValueError(f"Account with {account_email} not available")
            email_service = EmailNewsletterService(brevo_api_key=brevo_api_key)
            prompt = account.prompt or "Prompt nedostupný"
            await email_service.send_newsletter(
                recipient_email=account_email, articles=news_pick.articles, prompt_description=prompt
            )
            logger.info(f"Successfully sent daily pick email to {account_email}")
        except Exception as e:
            logger.error(f"Failed to send daily pick email to {account_email}: {e}")
