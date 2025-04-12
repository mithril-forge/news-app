# async_repositories.py
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional, TypeVar, Generic, Type, Any, Dict, Union, AsyncContextManager

from database.models import Topic, ParsedNews, Tag, InputNews, ParsedNewsTagLink
from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar('T', bound=SQLModel)


class AsyncBaseRepository(Generic[T]):
    """Base async repository with common CRUD operations."""

    def __init__(self, session: AsyncSession, model_class: Type[T]):
        self.session = session
        self.model_class = model_class

    @asynccontextmanager
    async def transaction(self) -> AsyncContextManager[None]:
        """Context manager for transactions."""
        try:
            yield
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def get_by_id(self, id: int) -> Optional[T]:
        """Get a record by ID."""
        return await self.session.get(self.model_class, id)

    async def get_all(self) -> List[T]:
        """Get all records."""
        statement = select(self.model_class)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def add(self, obj_in: Union[Dict[str, Any], T]) -> T:
        """Add a new record to the session without committing."""
        if isinstance(obj_in, dict):
            obj = self.model_class(**obj_in)
        else:
            obj = obj_in

        self.session.add(obj)
        await self.session.flush()  # Flush to get the ID but don't commit
        return obj

    async def update(self, obj: T) -> T:
        """Update an existing record without committing."""
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def refresh(self, obj: T) -> T:
        """Refresh an object from the database."""
        await self.session.refresh(obj)
        return obj

    async def remove(self, id: int) -> Optional[T]:
        """Remove a record from the session without committing."""
        obj = await self.session.get(self.model_class, id)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()
        return obj

    async def get_latest(self, skip: int, limit: int) -> List[T]:
        """
        Fetch latest with pagination
        """
        query = select(self.model_class).order_by(self.model_class.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()


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
