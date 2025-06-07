from datetime import timedelta, datetime
from typing import List, Optional, TypeVar, Any, Dict

from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql.expression import update
from sqlmodel import select, SQLModel, and_
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import func

from core.repository import AsyncBaseRepository
from core.models import Topic, Tag, ParsedNews, ParsedNewsTagLink
from core.logger import create_logger

T = TypeVar('T', bound=SQLModel)

logger = create_logger(__name__)


class AsyncTopicRepository(AsyncBaseRepository[Topic]):
    """Async repository for Topic model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Topic)
        logger.info("AsyncTopicRepository initialized")

    async def get_by_name(self, name: str) -> Optional[Topic]:
        """Get a topic by its name."""
        logger.debug(f"Getting topic by name: {name}")
        statement = select(Topic).where(Topic.name == name)
        result = await self.session.execute(statement)
        topic = result.scalars().first()
        logger.info(f"Found topic by name '{name}': {topic is not None}")
        return topic


class AsyncTagRepository(AsyncBaseRepository[Tag]):
    """Async repository for Tag model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Tag)
        logger.info("AsyncTagRepository initialized")

    async def get_by_text(self, text: str) -> Optional[Tag]:
        """Get a tag by its text."""
        logger.debug(f"Getting tag by text: {text}")
        statement = select(Tag).where(Tag.text == text)
        result = await self.session.execute(statement)
        tag = result.scalars().first()
        logger.info(f"Found tag by text '{text}': {tag is not None}")
        return tag

    async def get_or_create(self, text: str) -> Tag:
        """Get existing tag or create new tag (without committing)."""
        logger.debug(f"Getting or creating tag: {text}")
        tag = await self.get_by_text(text)
        if not tag:
            tag = await self.add({"text": text})
            logger.info(f"Created new tag: {text}")
        else:
            logger.debug(f"Found existing tag: {text}")
        return tag


class AsyncParsedNewsRepository(AsyncBaseRepository[ParsedNews]):
    """Async repository for ParsedNews model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ParsedNews)
        logger.info("AsyncParsedNewsRepository initialized")

    async def get_most_viewed_news_by_period(
            self,
            period: timedelta,
            limit: int = 10
    ) -> List[ParsedNews]:
        """
        Get most viewed news articles within a specified time period.

        Args:
            period: timedelta object specifying how far back to look
            limit: Maximum number of articles to return
            min_views: Minimum view count to filter by

        Returns:
            List of ParsedNews ordered by view_count descending
        """
        logger.debug(f"Getting most viewed news for period: {period}, limit: {limit}")
        cutoff_date = datetime.utcnow() - period

        stmt = (
            select(ParsedNews)
            .where(
                ParsedNews.created_at >= cutoff_date,
            )
            .order_by(ParsedNews.view_count.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)
        news_list = result.scalars().all()
        logger.info(f"Retrieved {len(news_list)} most viewed news articles")
        return news_list

    async def add_view_to_news(self, news_id: int) -> None:
        """Increment view count for a specific news article."""
        logger.debug(f"Adding view to news ID: {news_id}")
        stmt = (
            update(ParsedNews)
            .where(ParsedNews.id == news_id)
            .values(view_count=ParsedNews.view_count + 1)
        )

        result = await self.session.execute(stmt)

        if result.rowcount == 0:
            logger.error(f"Failed to add view - news with ID {news_id} not found")
            raise NoResultFound(f"News with id {news_id} not found")

        logger.info(f"Successfully added view to news ID: {news_id}")

    async def get_by_title(self, title: str) -> Optional[ParsedNews]:
        """Get news by title."""
        logger.debug(f"Getting news by title: {title}")
        statement = select(ParsedNews).where(ParsedNews.title == title)
        result = await self.session.execute(statement)
        news = result.scalars().first()
        logger.info(f"Found news by title '{title}': {news is not None}")
        return news

    async def get_by_topic_id(self, topic_id: int, skip: int, limit: int) \
            -> List[ParsedNews]:
        """
        Get news for a specific topic with pagination
        """
        logger.debug(f"Getting news by topic ID: {topic_id}, skip: {skip}, limit: {limit}")
        statement = (
            select(ParsedNews)
            .where(ParsedNews.topic_id == topic_id)
            .order_by(ParsedNews.created_at.desc())  # Assuming you want newest first
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        news_list = result.scalars().all()
        logger.info(f"Retrieved {len(news_list)} news articles for topic ID: {topic_id}")
        return news_list

    async def get_with_tags(self, news_id: int) -> Optional[ParsedNews]:
        """Get news with its tags preloaded."""
        logger.debug(f"Getting news with tags for ID: {news_id}")
        news = await self.get_by_id(news_id)
        if news:
            # Load tags relationship
            statement = select(Tag).join(ParsedNewsTagLink).where(
                ParsedNewsTagLink.news_item_id == news_id)
            result = await self.session.execute(statement)
            news.tags = result.scalars().all()
            logger.info(f"Loaded news with {len(news.tags)} tags for ID: {news_id}")
        else:
            logger.warn(f"News with ID {news_id} not found")
        return news

    async def prepare_with_tags(self, news_data: Dict[str, Any],
                                tag_texts: List[str]) -> ParsedNews:
        """
        Prepare news with tags without committing.
        This allows combining with other operations in a single transaction.
        """
        logger.debug(f"Preparing news with {len(tag_texts)} tags")
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
        logger.info(f"Prepared news with ID: {news.id} and {len(tag_texts)} tags")
        return news

    async def get_by_time_delta(
            self,
            delta: timedelta
    ) -> List[ParsedNews]:
        """
        """
        logger.debug(f"Getting news by time delta: {delta}")
        from_date = datetime.utcnow() - delta

        conditions = [ParsedNews.updated_at >= from_date]

        statement = select(ParsedNews).where(and_(*conditions))
        result = await self.session.execute(statement)
        news_list = result.scalars().all()
        logger.info(f"Retrieved {len(news_list)} news articles from time delta: {delta}")
        return news_list

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
        logger.debug(f"Updating news ID: {news_id} with {len(tag_texts)} tags")
        news = await self.update_from_dict(structure_id=news_id, data=news_data)
        if not news:
            logger.error(f"News with ID {news_id} not found for update")
            raise ValueError(f"Structure with id {news_id} not found even what it should be updated ")

        tag_repo = AsyncTagRepository(self.session)
        news.updated_at = datetime.utcnow()
        statement = select(ParsedNewsTagLink).where(
            ParsedNewsTagLink.news_item_id == news_id
        )
        result = await self.session.execute(statement)
        existing_links = result.scalars().all()

        logger.debug(f"Removing {len(existing_links)} existing tag links")
        for link in existing_links:
            await self.session.delete(link)

        logger.debug(f"Adding {len(tag_texts)} new tag links")
        for text in tag_texts:
            tag = await tag_repo.get_or_create(text)
            link = ParsedNewsTagLink(news_item_id=news_id, tag_id=tag.id)
            self.session.add(link)

        await self.session.flush()
        logger.info(f"Successfully updated news ID: {news_id} with {len(tag_texts)} tags")

        return news

    async def get_latest_received_timestamp(self) -> Optional[datetime]:
        """
        Get the most recent received_at timestamp.

        Returns:
            The latest timestamp or None if no records exist
        """
        logger.debug("Getting latest received timestamp")
        statement = select(func.max(ParsedNews.created_at))
        result = await self.session.execute(statement)
        latest_timestamp = result.scalar_one_or_none()

        logger.info(f"Latest received timestamp: {latest_timestamp}")
        return latest_timestamp