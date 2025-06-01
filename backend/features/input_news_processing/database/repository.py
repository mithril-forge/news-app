from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import func
from sqlmodel import select, and_

from core.models import InputNews, ParsedNews
from core.repository import AsyncBaseRepository
from sqlmodel.ext.asyncio.session import AsyncSession


class AsyncInputNewsRepository(AsyncBaseRepository[InputNews]):
    """Async repository for InputNews model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, InputNews)

    async def get_by_source_url(self, source_url: str) -> Optional[InputNews]:
        """
        Get input news by source URL.
        """
        statement = select(InputNews).where(InputNews.source_url == source_url)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_by_time_delta(
            self,
            delta: timedelta,
            has_parsed_news: Optional[bool] = None,
            newer: bool = True
    ) -> List[InputNews]:
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
        from_date = datetime.utcnow() - delta

        conditions = [InputNews.publication_date >= from_date if newer else InputNews.publication_date <= from_date]

        if has_parsed_news is True:
            conditions.append(InputNews.parsed_news != None)
        elif has_parsed_news is False:
            conditions.append(InputNews.parsed_news == None)

        statement = select(InputNews).where(and_(*conditions))
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def update_parsed_news_id(self, input_id: int, parsed_news_id: int) -> InputNews:
        """
        Update the parsed_news_id for an input news item and update the ParsedNews updated_at timestamp.

        Args:
            input_id: ID of the InputNews to update
            parsed_news_id: ID of the ParsedNews to link

        Returns:
            Updated InputNews object or None if not found
        """
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

            await self.session.flush()
        else:
            raise ValueError(f"Didn't find input_news record with {input_id=}")
        return input_news

    async def get_latest_received_timestamp(self) -> Optional[datetime]:
        """
        Get the most recent received_at timestamp.

        Returns:
            The latest timestamp or None if no records exist
        """
        statement = select(func.max(InputNews.received_at))
        result = await self.session.execute(statement)
        latest_timestamp = result.scalar_one_or_none()

        return latest_timestamp
