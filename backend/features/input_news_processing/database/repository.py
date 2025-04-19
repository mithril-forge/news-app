from datetime import datetime
from typing import Optional, List

from database.repository import AsyncBaseRepository
from features.input_news_processing.models import InputNews


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
