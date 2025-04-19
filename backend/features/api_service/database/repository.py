from typing import List, Optional, TypeVar, Any, Dict

from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from core.repository import AsyncBaseRepository
from features.api_service.database.models import Topic, Tag, ParsedNews, ParsedNewsTagLink

T = TypeVar('T', bound=SQLModel)

class AsyncTopicRepository(AsyncBaseRepository[Topic]):
    """Async repository for Topic model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Topic)

    async def get_by_name(self, name: str) -> Optional[Topic]:
        """Get a topic by its name."""
        statement = select(Topic).where(Topic.name == name)
        result = await self.session.execute(statement)
        return result.scalars().first()


class AsyncTagRepository(AsyncBaseRepository[Tag]):
    """Async repository for Tag model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Tag)

    async def get_by_text(self, text: str) -> Optional[Tag]:
        """Get a tag by its text."""
        statement = select(Tag).where(Tag.text == text)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_or_create(self, text: str) -> Tag:
        """Get existing tag or create new tag (without committing)."""
        tag = await self.get_by_text(text)
        if not tag:
            tag = await self.add({"text": text})
        return tag


class AsyncParsedNewsRepository(AsyncBaseRepository[ParsedNews]):
    """Async repository for ParsedNews model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ParsedNews)

    async def get_by_title(self, title: str) -> Optional[ParsedNews]:
        """Get news by title."""
        statement = select(ParsedNews).where(ParsedNews.title == title)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_by_topic_id(self, topic_id: int, skip: int, limit: int) \
            -> List[ParsedNews]:
        """
        Get news for a specific topic with pagination
        """
        statement = (
            select(ParsedNews)
            .where(ParsedNews.topic_id == topic_id)
            .order_by(ParsedNews.created_at.desc())  # Assuming you want newest first
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_with_tags(self, news_id: int) -> Optional[ParsedNews]:
        """Get news with its tags preloaded."""
        news = await self.get_by_id(news_id)
        if news:
            # Load tags relationship
            statement = select(Tag).join(ParsedNewsTagLink).where(
                ParsedNewsTagLink.news_item_id == news_id)
            result = await self.session.execute(statement)
            news.tags = result.scalars().all()
        return news

    async def prepare_with_tags(self, news_data: Dict[str, Any],
                                tag_texts: List[str]) -> ParsedNews:
        """
        Prepare news with tags without committing.
        This allows combining with other operations in a single transaction.
        """
        tag_repo = AsyncTagRepository(self.session)

        # Create news
        news = await self.add(news_data)

        # Add tags
        for text in tag_texts:
            tag = await tag_repo.get_or_create(text)
            # Create link manually
            link = ParsedNewsTagLink(news_item_id=news.id, tag_id=tag.id)
            self.session.add(link)

        # Flush to ensure all objects have IDs but don't commit
        await self.session.flush()

        # DON'T try to assign to news.tags directly
        # Instead, just return the news object without manually loading the tags
        return news
