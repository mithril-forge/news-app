from datetime import datetime, timedelta
from typing import Optional, List

from sqlmodel import select, and_

from core.models import InputNews
from core.repository import AsyncBaseRepository
from sqlmodel.ext.asyncio.session import AsyncSession


class AsyncInputNewsRepository(AsyncBaseRepository[InputNews]):
    """Async repository for InputNews model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, InputNews)

    async def get_unprocessed(self) -> List[InputNews]:
        """Get all unprocessed input news."""
        statement = select(InputNews).where(InputNews.processed_at == None)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def mark_as_processed(self, input_id: int, parsed_news_id: int) -> InputNews:
        """Mark input news as processed and link to its parsed version without committing."""
        input_news = await self.get_by_id(input_id)
        if input_news:
            input_news.processed_at = datetime.utcnow()
            input_news.parsed_news = parsed_news_id
            self.session.add(input_news)
            await self.session.flush()
        return input_news

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
            has_parsed_news: Optional[bool] = None
    ) -> List[InputNews]:
        """
        Get input news published within a time delta from now.

        Args:
            delta: Time delta to look back from current time
            has_parsed_news: If True, only return news with parsed_news link.
                            If False, only return news without parsed_news link.
                            If None, return all news regardless of parsed_news status.

        Returns:
            List of InputNews within the time delta
        """
        from_date = datetime.utcnow() - delta

        conditions = [InputNews.publication_date >= from_date]

        if has_parsed_news is True:
            conditions.append(InputNews.parsed_news_id != None)
        elif has_parsed_news is False:
            conditions.append(InputNews.parsed_news_id == None)

        statement = select(InputNews).where(and_(*conditions))
        result = await self.session.execute(statement)
        return result.scalars().all()
