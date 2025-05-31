from datetime import timedelta, datetime
from typing import List, Optional, TypeVar, Any, Dict

from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql.expression import update
from sqlmodel import select, SQLModel, and_
from sqlmodel.ext.asyncio.session import AsyncSession

from core.models import InputNews
from core.repository import AsyncBaseRepository
from core.models import Topic, Tag, ParsedNews, ParsedNewsTagLink

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

    async def add_view_to_news(self, news_id: int) -> None:
        """Increment view count for a specific news article."""
        stmt = (
            update(ParsedNews)
            .where(ParsedNews.id == news_id)
            .values(view_count=ParsedNews.view_count + 1)
        )

        result = await self.session.execute(stmt)

        if result.rowcount == 0:
            raise NoResultFound(f"News with id {news_id} not found")

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
        await self.session.refresh(news, ['tags'])
        # DON'T try to assign to news.tags directly
        # Instead, just return the news object without manually loading the tags
        return news

    async def get_by_time_delta(
            self,
            delta: timedelta
    ) -> List[ParsedNews]:
        """
        """
        from_date = datetime.utcnow() - delta

        conditions = [ParsedNews.updated_at >= from_date]

        statement = select(ParsedNews).where(and_(*conditions))
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def update_with_tags(self, news_id: int, news_data: Dict[str, Any],
                               tag_texts: List[str]) -> ParsedNews:
        """
        Update news with its tags in a single transaction.

        Args:
            news_id: ID of the news to update
            news_data: Dictionary with news fields to update
            tag_texts: List of tag texts to associate with the news

        Returns:
            Updated ParsedNews object

        Raises:
            HTTPException: If news with given ID is not found
        """
        news = await self.update_from_dict(structure_id=news_id, data=news_data)
        if not news:
            raise ValueError(f"Structure with id {news_id} not found even what it should be updated ")

        tag_repo = AsyncTagRepository(self.session)
        news.updated_at = datetime.utcnow()
        statement = select(ParsedNewsTagLink).where(
            ParsedNewsTagLink.news_item_id == news_id
        )
        result = await self.session.execute(statement)
        existing_links = result.scalars().all()

        for link in existing_links:
            await self.session.delete(link)

        for text in tag_texts:
            tag = await tag_repo.get_or_create(text)
            link = ParsedNewsTagLink(news_item_id=news_id, tag_id=tag.id)
            self.session.add(link)

        await self.session.flush()

        return news
