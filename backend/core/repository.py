from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import (
    Any,
    TypeVar,
    cast,
)

import structlog
from sqlalchemy import func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import update
from sqlmodel import SQLModel, and_, select

from core.models import BaseModelWithID, ParsedNews, ParsedNewsTagLink, Tag, Topic, ParsedNewsRelevancy


T = TypeVar("T", bound=BaseModelWithID)

logger = structlog.get_logger()


class AsyncBaseRepository[T: BaseModelWithID]:
    """Base async repository with common CRUD operations."""

    def __init__(self, session: AsyncSession, model_class: type[T]):
        self.session = session
        self.model_class = model_class
        logger.info(f"Initialized repository for {model_class.__name__}")

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[None]:
        """Context manager for transactions."""
        logger.debug("Starting transaction")
        try:
            yield
            await self.session.commit()
            logger.debug("Transaction committed")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Transaction rolled back due to error: {e}")
            raise

    async def get_by_id(self, id: int) -> T | None:
        """Get a record by ID."""
        logger.debug(f"Getting {self.model_class.__name__} by ID: {id}")
        result = await self.session.get(self.model_class, id)
        logger.info(f"Found {self.model_class.__name__} with ID {id}: {result is not None}")
        return result

    async def get_by_ids(self, ids: Sequence[int]) -> list[T]:
        """Get records by multiple IDs."""
        if not ids:
            logger.debug(f"No IDs provided for {self.model_class.__name__}")
            return []

        logger.debug(f"Getting {self.model_class.__name__} by IDs: {list(ids)}")

        # Create query to select records where ID is in the provided list
        stmt = select(self.model_class).where(self.model_class.id.in_(ids))  # type: ignore
        result = await self.session.execute(stmt)
        records = result.scalars().all()

        logger.info(f"Found {len(records)} {self.model_class.__name__} records out of {len(ids)} requested IDs")
        return list(records)

    async def get_all(self) -> Sequence[T]:
        """Get all records."""
        logger.debug(f"Getting all {self.model_class.__name__} records")
        statement = select(self.model_class)
        result = await self.session.execute(statement)
        records = result.scalars().all()
        logger.info(f"Retrieved {len(records)} {self.model_class.__name__} records")
        return records

    async def add(self, obj_in: dict[str, Any] | T) -> T:
        """Add a new record to the session without committing."""
        logger.debug(f"Adding new {self.model_class.__name__}")
        if isinstance(obj_in, dict):
            obj = self.model_class(**obj_in)
        else:
            obj = obj_in

        self.session.add(obj)
        await self.session.flush()  # Flush to get the ID but don't commit
        logger.info(f"Added new {self.model_class.__name__} with ID: {getattr(obj, 'id', 'unknown')}")
        return obj

    async def update(self, obj: T) -> T:
        """Update an existing record without committing."""
        logger.debug(f"Updating {self.model_class.__name__} with ID: {getattr(obj, 'id', 'unknown')}")
        self.session.add(obj)
        await self.session.flush()
        logger.info(f"Updated {self.model_class.__name__} with ID: {getattr(obj, 'id', 'unknown')}")
        return obj

    async def update_from_dict(self, structure_id: int, data: dict[str, Any]) -> T | None:
        """
        Update an existing record with the given data.

        Args:
            id: The ID of the record to update
            data: Dictionary containing fields and values to update

        Returns:
            Updated model instance or None if record not found
        """
        logger.info(f"Updating {self.model_class.__name__} with ID {structure_id} from dict")
        logger.debug(f"Updating dict: {data}")
        instance = await self.get_by_id(structure_id)
        if not instance:
            logger.warn(f"{self.model_class.__name__} with ID {structure_id} not found for update")
            return None

        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self.session.add(instance)
        await self.session.flush()
        logger.info(f"Updated {self.model_class.__name__} with ID {structure_id} from dict")

        return instance

    async def refresh(self, obj: T) -> T:
        """Refresh an object from the database."""
        logger.debug(f"Refreshing {self.model_class.__name__} with ID: {getattr(obj, 'id', 'unknown')}")
        await self.session.refresh(obj)
        return obj

    async def remove(self, id: int) -> T | None:
        """Remove a record from the session without committing."""
        logger.debug(f"Removing {self.model_class.__name__} with ID: {id}")
        obj = await self.session.get(self.model_class, id)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()
            logger.info(f"Removed {self.model_class.__name__} with ID: {id}")
        else:
            logger.warn(f"{self.model_class.__name__} with ID {id} not found for removal")
        return obj

    @staticmethod
    async def create_snapshot(instances: Sequence[T]) -> dict[str, Any]:
        """
        Create a simple snapshot of model instances and save to JSON.

        Args:
            instances: List of model instances to snapshot
            filepath: Path where to save the snapshot file
        """
        logger.debug(f"Creating snapshot of {len(instances)} instances")
        data = []
        for instance in instances:
            instance_data = {}
            for field_name, field_value in instance.__dict__.items():
                # Skip SQLAlchemy internals and relationship objects
                if not field_name.startswith("_") and not isinstance(field_value, list | SQLModel):
                    instance_data[field_name] = field_value

            data.append(instance_data)

        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "model_type": T.__name__,  # type: ignore[misc]
            "count": len(instances),
            "data": data,
        }

        logger.info(f"Created snapshot with {len(instances)} instances")
        return snapshot


class AsyncTopicRepository(AsyncBaseRepository[Topic]):
    """Async repository for Topic model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Topic)
        logger.info("AsyncTopicRepository initialized")

    async def get_by_name(self, name: str) -> Topic | None:
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

    async def get_by_text(self, text: str) -> Tag | None:
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

    async def get_latest_by_relevance(self, skip: int, limit: int) -> Sequence[ParsedNewsRelevancy]:
        """
        Fetch latest news sorted by relevance score from materialized view with pagination

        Args:
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return

        Returns:
            Sequence of ParsedNewsRelevancy ordered by relevance_score desc
        """
        logger.debug(f"Getting latest news by relevance (skip: {skip}, limit: {limit})")
        query = (
            select(ParsedNewsRelevancy)
            .order_by(ParsedNewsRelevancy.relevance_score.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        records = result.scalars().all()
        logger.info(f"Retrieved {len(records)} news records sorted by relevance")
        return records

    async def get_latest(self, skip: int, limit: int) -> Sequence[ParsedNews]:
        """
        Fetch latest with pagination
        """
        logger.debug(f"Getting latest {self.model_class.__name__} records (skip: {skip}, limit: {limit})")
        query = (
            select(ParsedNews)
            .order_by(ParsedNews.updated_at.desc())  # type: ignore[attr-defined]
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        records = result.scalars().all()
        logger.info(f"Retrieved {len(records)} latest {self.model_class.__name__} records")
        return records

    async def get_most_viewed_news_by_period(self, period: timedelta, limit: int = 10) -> Sequence[ParsedNews]:
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
                ParsedNews.updated_at >= cutoff_date,
            )
            .order_by(ParsedNews.view_count.desc())  # type: ignore[attr-defined]
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
            .where(ParsedNews.id == news_id)  # type: ignore[arg-type]
            .values(view_count=ParsedNews.view_count + 1)
        )

        result = await self.session.execute(stmt)

        if result.rowcount == 0:
            logger.error(f"Failed to add view - news with ID {news_id} not found")
            raise NoResultFound(f"News with id {news_id} not found")

        logger.info(f"Successfully added view to news ID: {news_id}")

    async def get_by_title(self, title: str) -> ParsedNews | None:
        """Get news by title."""
        logger.debug(f"Getting news by title: {title}")
        statement = select(ParsedNews).where(ParsedNews.title == title)
        result = await self.session.execute(statement)
        news = result.scalars().first()
        logger.info(f"Found news by title '{title}': {news is not None}")
        return news

    async def get_by_topic_id(self, topic_id: int, skip: int, limit: int) -> list[ParsedNews]:
        """
        Get news for a specific topic with pagination
        """
        logger.debug(f"Getting news by topic ID: {topic_id}, skip: {skip}, limit: {limit}")
        statement = (
            select(ParsedNews)
            .where(ParsedNews.topic_id == topic_id)
            .order_by(ParsedNews.updated_at.desc())  # type: ignore[attr-defined]
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        news_list = result.scalars().all()
        logger.info(f"Retrieved {len(news_list)} news articles for topic ID: {topic_id}")
        return cast(list[ParsedNews], news_list)

    async def get_with_tags(self, news_id: int) -> ParsedNews | None:
        """Get news with its tags preloaded."""
        logger.debug(f"Getting news with tags for ID: {news_id}")

        statement = select(ParsedNews).options(joinedload(ParsedNews.tags)).where(ParsedNews.id == news_id)

        result = await self.session.execute(statement)
        news = result.unique().scalar_one_or_none()  # unique() needed with joinedload

        if news:
            logger.info(f"Loaded news with {len(news.tags)} tags for ID: {news_id}")
        else:
            logger.warn(f"News with ID {news_id} not found")

        return news

    async def prepare_with_tags(self, news_data: dict[str, Any], tag_texts: list[str]) -> ParsedNews:
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
        await self.session.refresh(news, ["tags"])
        logger.info(f"Prepared news with ID: {news.id} and {len(tag_texts)} tags")
        return news

    async def get_by_time_delta(self, delta: timedelta) -> Sequence[ParsedNews]:
        """ """
        logger.debug(f"Getting news by time delta: {delta}")
        from_date = datetime.utcnow() - delta

        conditions = [ParsedNews.updated_at >= from_date]

        statement = select(ParsedNews).where(and_(*conditions))
        result = await self.session.execute(statement)
        news_list = result.scalars().all()
        logger.info(f"Retrieved {len(news_list)} news articles from time delta: {delta}")
        return news_list

    async def update_with_tags(self, news_id: int, news_data: dict[str, Any], tag_texts: list[str]) -> ParsedNews:
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
        logger.info(f"Updating news ID: {news_id} with {tag_texts} tags")
        news = await self.update_from_dict(structure_id=news_id, data=news_data)
        if not news:
            logger.error(f"News with ID {news_id} not found for update")
            raise ValueError(f"Structure with id {news_id} not found even what it should be updated ")

        tag_repo = AsyncTagRepository(self.session)
        news.updated_at = datetime.utcnow()
        statement = select(ParsedNewsTagLink).where(ParsedNewsTagLink.news_item_id == news_id)
        result = await self.session.execute(statement)
        existing_links = result.scalars().all()

        logger.debug(f"Removing existing tag links: {existing_links}")
        for link in existing_links:
            await self.session.delete(link)

        logger.debug(f"Adding new tag links: {tag_texts}")
        for text in tag_texts:
            tag = await tag_repo.get_or_create(text)
            link = ParsedNewsTagLink(news_item_id=news_id, tag_id=tag.id)
            self.session.add(link)

        await self.session.flush()
        await self.session.refresh(news, ["tags"])
        logger.info(f"Successfully updated news ID: {news_id} with {tag_texts} tags")

        return news

    async def get_latest_received_timestamp(self) -> datetime | None:
        """
        Get the most recent received_at timestamp.

        Returns:
            The latest timestamp or None if no records exist
        """
        logger.debug("Getting latest received timestamp")
        statement = select(func.max(ParsedNews.updated_at))
        result = await self.session.execute(statement)
        latest_timestamp = result.scalar_one_or_none()

        logger.info(f"Latest received timestamp: {latest_timestamp}")
        return latest_timestamp
