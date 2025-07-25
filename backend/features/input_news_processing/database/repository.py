from datetime import datetime, timedelta
from collections.abc import Sequence

import structlog
from sqlalchemy import func
from sqlmodel import select, and_

from core.models import InputNews, ParsedNews
from core.repository import AsyncBaseRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


class AsyncInputNewsRepository(AsyncBaseRepository[InputNews]):
    """Async repository for InputNews model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, InputNews)
        logger.info("AsyncInputNewsRepository initialized")

    async def get_by_source_url(self, source_url: str) -> InputNews | None:
        """
        Get input news by source URL.
        """
        logger.debug(f"Getting input news by source URL: {source_url}")
        statement = select(InputNews).where(InputNews.source_url == source_url)
        result = await self.session.execute(statement)
        input_news = result.scalars().first()
        logger.info(
            f"Found input news by source URL '{source_url}': {input_news is not None}"
        )
        return input_news

    async def get_by_time_delta(
        self,
        delta: timedelta,
        has_parsed_news: bool | None = None,
        newer: bool = True,
    ) -> Sequence[InputNews]:
        """
        Get input news published within a time delta from now.

        Args:
            delta: Time delta to look back from current time
            has_parsed_news: If True, only return news with parsed_news link.
                            If False, only return news without parsed_news link.
                            If None, return all news regardless of parsed_news status.
            newer: if True than newer than timedelta, else older

        Returns:
            List of InputNews within the time delta
        """
        logger.debug(
            f"Getting input news by time delta: {delta}, has_parsed_news: {has_parsed_news}, newer: {newer}"
        )
        from_date = datetime.utcnow() - delta
        conditions = [
            InputNews.publication_date >= from_date  # type: ignore[operator]
            if newer
            else InputNews.publication_date <= from_date  # type: ignore[operator]
        ]

        if has_parsed_news:
            conditions.append(InputNews.parsed_news is not None)
        elif has_parsed_news is False:
            conditions.append(InputNews.parsed_news is None)

        statement = select(InputNews).where(and_(*conditions))
        result = await self.session.execute(statement)
        input_news_list = result.scalars().all()
        logger.info(f"Retrieved {len(input_news_list)} input news items by time delta")
        return input_news_list

    async def update_parsed_news_id(
        self, input_id: int, parsed_news_id: int
    ) -> InputNews:
        """
        Update the parsed_news_id for an input news item and update the ParsedNews updated_at timestamp.

        Args:
            input_id: ID of the InputNews to update
            parsed_news_id: ID of the ParsedNews to link

        Returns:
            Updated InputNews object or None if not found
        """
        logger.debug(
            f"Updating parsed_news_id for input ID: {input_id} to parsed_news ID: {parsed_news_id}"
        )
        input_news = await self.get_by_id(input_id)
        if input_news:
            input_news.parsed_news = parsed_news_id
            self.session.add(input_news)
            statement = select(ParsedNews).where(ParsedNews.id == parsed_news_id)
            result = await self.session.execute(statement)
            parsed_news = result.scalars().first()
            if parsed_news:
                parsed_news.updated_at = datetime.utcnow()
                self.session.add(parsed_news)
                logger.debug(f"Updated ParsedNews timestamp for ID: {parsed_news_id}")

            await self.session.flush()
            logger.info(f"Successfully updated parsed_news_id for input ID: {input_id}")
        else:
            logger.error(f"Input news record not found with input_id: {input_id}")
            raise ValueError(f"Didn't find input_news record with {input_id=}")
        return input_news

    async def get_latest_received_timestamp(self) -> datetime | None:
        """
        Get the most recent received_at timestamp.

        Returns:
            The latest timestamp or None if no records exist
        """
        logger.debug("Getting latest received timestamp for input news")
        statement = select(func.max(InputNews.received_at))
        result = await self.session.execute(statement)
        latest_timestamp = result.scalar_one_or_none()

        logger.info(f"Latest received timestamp for input news: {latest_timestamp}")
        return latest_timestamp
