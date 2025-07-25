import io
import json
import zipfile
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

import structlog

from features.input_news_processing.archive.abstract_archive import AbstractArchive
from features.input_news_processing.database.repository import AsyncInputNewsRepository
from cz_news import crawl_czech_news, Article

from core.repository import AsyncParsedNewsRepository
from features.input_news_processing.converters import (
    parsed_news_list_with_input,
    input_news_list_to_schema,
    input_schema_list_to_orm,
    input_news_to_schema,
    input_news_lite_list_to_schema,
)
from features.input_news_processing.domain.schemas import (
    ParsedNewsWithInputNews,
    InputNews,
    InputNewsWithID,
    InputNewsWithoutContent,
)

logger = structlog.get_logger()


class InputNewsService:
    def __init__(self, session: AsyncSession, archive: AbstractArchive) -> None:
        self.session = session
        self.input_news_repo = AsyncInputNewsRepository(session=session)
        self.parsed_news_repo = AsyncParsedNewsRepository(session=session)
        self.archive = archive
        logger.info("InputNewsService initialized")

    async def add_or_update_input_news_batch(self, input_news_list: list[InputNews]) -> list[InputNewsWithID]:
        """
        Add a batch of input news items to the database.

        Args:
            input_news_list: List of InputNewsMetadata instances

        Returns:
            List of IDs of the added/updated news items
        """
        logger.info(f"Adding batch of {len(input_news_list)} input news items")
        orm_models = input_schema_list_to_orm(input_news_list)
        result_models = []
        for model in orm_models:
            existing = await self.input_news_repo.get_by_source_url(model.source_url)

            if existing:
                logger.debug(f"Updating existing input news with source_url: {model.source_url}")
                for key, value in model.dict(exclude={"id"}).items():
                    if value is not None:
                        setattr(existing, key, value)
                updated = await self.input_news_repo.update(existing)
                result_models.append(updated)
            else:
                # Add new model
                logger.debug(f"Adding new input news with title: {model.title}")
                new_model = await self.input_news_repo.add(model.dict(exclude={"id"}))
                result_models.append(new_model)

        logger.info(f"Successfully processed {len(result_models)} input news items")
        return input_news_list_to_schema(result_models)

    async def scrap_and_save_input_news(self, adjust_parse_date: bool, delta: timedelta) -> list[InputNewsWithID]:
        """
        Query latest news from the corresponding websites by delta and update them in DB or create news ones.
        adjust_parse_date parameter is to optimalize parsing delta. It will check latest timestamp in DB and if it's newer
        than the delta, it will adjust the delat to it
        """
        logger.info(f"Scraping and saving input news with delta: {delta}")
        if adjust_parse_date:
            latest_timestamp = await self.get_latest_timestamp()
            if latest_timestamp is not None:
                now = datetime.utcnow()
                time_since_latest = now - latest_timestamp
                logger.debug(f"Time of the latest input news is: {latest_timestamp}")
                if time_since_latest < delta:
                    delta = time_since_latest
                    logger.info(f"Adjusted delta of parsing for input news to: {delta}")
        input_news = await self.scrap_input_news(delta=delta)
        result = await self.add_or_update_input_news_batch(input_news_list=input_news)
        logger.info(f"Scraped and saved {len(result)} input news items")
        return result

    async def clear_old_input_news(self, delta: timedelta) -> None:
        """
        Function that will archive older input news from DB that weren't used for any parsed news.
        The implementation would be probably by some JSON dump.
        """
        logger.info(f"Clearing old input news older than delta: {delta}")
        old_input_news = await self.input_news_repo.get_by_time_delta(delta=delta, newer=False, has_parsed_news=False)
        logger.debug(f"Found {len(old_input_news)} old input news items to archive")

        snapshot = await self.input_news_repo.create_snapshot(old_input_news)
        json_str = json.dumps(snapshot, indent=2, default=str)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("input_news.json", json_str)
        zip_buffer.seek(0)
        zip_bytes = zip_buffer.getvalue()
        archive_path = self.archive.save_file(file_content=zip_bytes, suffix=".zip")
        logger.info(f"Archived {len(old_input_news)} old input news items to: {archive_path}")

        for input_news in old_input_news:
            input_news_id = input_news.id
            if input_news_id is None:
                raise ValueError(f"Input news {input_news} doesn't have properly set id.")
            await self.input_news_repo.remove(id=input_news_id)
        logger.info(f"Removed {len(old_input_news)} old input news items from database")

    @staticmethod
    async def scrap_input_news(
        delta: timedelta,
        max_articles_per_site: int = 10,
        websites: list[str] | None = None,
    ) -> list[InputNews]:
        """
        Function that calls the Czech News Crawler to fetch input news from websites.

        Args:
            delta: Time period to look back for articles

        Returns:
            List of InputNewsBase objects with news article data
        """
        logger.info(f"Scraping input news with delta: {delta}, max_articles_per_site: {max_articles_per_site}")
        if websites is not None:
            logger.debug(f"Scraping from specific websites: {websites}")
            crawl_result = crawl_czech_news(
                time_delta=delta,
                max_articles_per_site=max_articles_per_site,
                websites=websites,
            )
        else:
            logger.debug("Scraping from all available websites")
            crawl_result = crawl_czech_news(time_delta=delta, max_articles_per_site=max_articles_per_site)

        articles_by_domain: dict[str, list[Article]] = crawl_result.articles_by_domain
        articles: list[Article] = []
        for _domain, articles_list in articles_by_domain.items():
            articles.extend(articles_list)

        logger.debug(f"Retrieved {len(articles)} total articles from {len(articles_by_domain)} domains")

        input_news_list = []
        for article in articles:
            author = ",".join(article.authors)
            publish_date = article.publish_date if article.publish_date else datetime.now()
            input_news = InputNews(
                tags=article.tags,
                category="",
                publication_date=publish_date,
                author=author,
                source_site=article.domain,
                source_url=article.normalized_url,
                content=article.text,
                title=article.title,
                summary=article.description,
            )
            input_news_list.append(input_news)

        logger.info(f"Scraped {len(input_news_list)} articles from {len(articles_by_domain)} domains")
        return input_news_list

    async def get_input_news_by_delta(
        self, delta: timedelta, has_parsed_news: bool | None = None
    ) -> list[InputNewsWithID]:
        """
        Retrieves input news within a specified time period.
        Args:
            delta: Time period to look back from current time
            has_parsed_news: Filter by whether news has connected parsed news or not (None takes all)
        """
        logger.debug(f"Getting input news by delta: {delta}, has_parsed_news: {has_parsed_news}")
        result = await self.input_news_repo.get_by_time_delta(delta=delta, has_parsed_news=has_parsed_news)
        converted_result = input_news_list_to_schema(input_news_list=result)
        logger.info(f"Retrieved {len(converted_result)} input news items by delta")
        return converted_result

    async def get_input_news_by_ids_lite(
        self, input_news_ids: list[int], has_parsed_news: bool | None = None
    ) -> list[InputNewsWithoutContent]:
        """
        Retrieves input news within a specified time period (lite version with less information).
        Args:
            input_news_ids:
            has_parsed_news: Filter by whether news has connected parsed news or not (None takes all)
        """
        logger.debug(f"Getting input news for input news ids: {input_news_ids}, has_parsed_news: {has_parsed_news}")
        result = await self.input_news_repo.get_by_ids(ids=input_news_ids)
        match has_parsed_news:
            case True:
                result = [res for res in result if res.parsed_news is not None]
            case False:
                result = [res for res in result if res.parsed_news is None]
        converted_result = input_news_lite_list_to_schema(input_news_list=result)
        logger.info(f"Retrieved {len(converted_result)} input news items by ids (lite)")
        return converted_result

    async def get_parsed_with_input_news(self, delta: timedelta) -> list[ParsedNewsWithInputNews]:
        """
        Retrieves parsed news with their associated input news within a specified time period.
        """
        logger.debug(f"Getting parsed news with input by delta: {delta}")
        result = await self.parsed_news_repo.get_by_time_delta(delta=delta)
        converted_result = parsed_news_list_with_input(parsed_news_list=result)
        logger.info(f"Retrieved {len(converted_result)} parsed news with input by delta")
        return converted_result

    async def connect_input_with_parsed(self, parsed_id: int, input_id: int) -> InputNewsWithID:
        """
        Links a parsed news entry with its original input news entry.
        """
        logger.info(f"Connecting input news ID {input_id} with parsed news ID {parsed_id}")
        db_result = await self.input_news_repo.update_parsed_news_id(input_id=input_id, parsed_news_id=parsed_id)
        result = input_news_to_schema(db_result)
        logger.info(f"Successfully connected input news ID {input_id} with parsed news ID {parsed_id}")
        return result

    async def get_latest_timestamp(self) -> datetime | None:
        """
        Returns latest timestamp of the input news
        """
        logger.debug("Getting latest timestamp for input news")
        result = await self.input_news_repo.get_latest_received_timestamp()
        logger.info(f"Latest input news timestamp: {result}")
        return result
