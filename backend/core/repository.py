import datetime
from collections.abc import AsyncGenerator, Sequence
from contextlib import asynccontextmanager
from typing import (
    Any,
    TypedDict,
    TypeVar,
    cast,
)

import structlog
from sqlalchemy import exists, func, not_, text
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import update
from sqlmodel import SQLModel, and_, select

from core.domain.token_generator import TokenGenerator
from core.exceptions import (
    AccountDeletionFailedException,
    AccountNotFoundException,
    TokenAlreadyUsedException,
    TokenExpiredException,
    TokenNotFoundException,
)
from core.models import (
    Account,
    AccountDeletionToken,
    BaseModel,
    BaseModelWithID,
    InputNews,
    NewsPick,
    NewsPickItem,
    ParsedNews,
    ParsedNewsRelevancy,
    ParsedNewsTagLink,
    Tag,
    Topic,
)

G = TypeVar("G", bound=BaseModel)
T = TypeVar("T", bound=BaseModelWithID)

logger = structlog.get_logger()


class TokenGenerationResponse(TypedDict):
    plain_token: str
    token_record: AccountDeletionToken


class AsyncBaseRepository[G: BaseModel]:
    """Basic repository for all the models."""

    def __init__(self, session: AsyncSession, model_class: type[G]):
        self.session = session
        self.model_class = model_class
        logger.info(f"Initialized repository for {model_class.__name__}")

    async def get_all(self) -> Sequence[G]:
        """Get all records."""
        logger.debug(f"Getting all {self.model_class.__name__} records")
        statement = select(self.model_class)
        result = await self.session.execute(statement)
        records = result.scalars().all()
        logger.info(f"Retrieved {len(records)} {self.model_class.__name__} records")
        return records

    async def add(self, obj_in: dict[str, Any] | G) -> G:
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

    async def update(self, obj: G) -> G:
        """Update an existing record without committing."""
        logger.debug(f"Updating {self.model_class.__name__} with ID: {getattr(obj, 'id', 'unknown')}")
        self.session.add(obj)
        await self.session.flush()
        logger.info(f"Updated {self.model_class.__name__} with ID: {getattr(obj, 'id', 'unknown')}")
        return obj

    async def refresh(self, obj: G) -> G:
        """Refresh an object from the database."""
        logger.debug(f"Refreshing {self.model_class.__name__} with ID: {getattr(obj, 'id', 'unknown')}")
        await self.session.refresh(obj)
        return obj


class AsyncBaseRepositoryWithID[T: BaseModelWithID](AsyncBaseRepository[T]):
    """Base async repository with common CRUD operations for models with ID"""

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
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "model_type": T.__name__,  # type: ignore[misc]
            "count": len(instances),
            "data": data,
        }

        logger.info(f"Created snapshot with {len(instances)} instances")
        return snapshot


class AsyncTopicRepositoryWithID(AsyncBaseRepositoryWithID[Topic]):
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


class AsyncTagRepositoryWithID(AsyncBaseRepositoryWithID[Tag]):
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


class AsyncParsedNewsRepositoryWithID(AsyncBaseRepositoryWithID[ParsedNews]):
    """Async repository for ParsedNews model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ParsedNews)
        logger.info("AsyncParsedNewsRepository initialized")

    async def search_news(self, q: str, limit: int, offset: int) -> list[ParsedNews]:
        """
        Search news articles by query string with pagination.

        Args:
            q: Search query string
            limit: Maximum number of records to return
            offset: Number of records to skip for pagination

        Returns:
            List of ParsedNews articles matching the query
        """
        logger.debug(f"Searching news with query: '{q}', limit: {limit}, offset: {offset}")

        search_filter = func.to_tsvector(
            "simple",
            func.unaccent(
                func.coalesce(ParsedNews.title, "")
                + " "
                + func.coalesce(ParsedNews.description, "")
                + " "
                + func.coalesce(ParsedNews.content, "")
            ),
        ).op("@@")(func.plainto_tsquery("simple", func.unaccent(q)))

        stmt = (
            select(ParsedNews).where(search_filter).order_by(ParsedNews.updated_at.desc()).offset(offset).limit(limit)  # type: ignore[attr-defined]
        )

        result = await self.session.execute(stmt)
        articles = list(result.scalars().all())

        logger.info(f"Found {len(articles)} articles matching query '{q}'")

        return articles

    async def refresh_materialized_view(self) -> None:
        """Refresh the news relevance materialized view"""
        await self.session.execute(text("REFRESH MATERIALIZED VIEW news_relevance"))

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
            select(ParsedNewsRelevancy).order_by(ParsedNewsRelevancy.relevance_score.desc()).offset(skip).limit(limit)  # type: ignore[attr-defined]
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

    async def get_most_viewed_news_by_period(self, period: datetime.timedelta, limit: int = 10) -> Sequence[ParsedNews]:
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
        cutoff_date = datetime.datetime.utcnow() - period

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

        if result.rowcount == 0:  # type: ignore[attr-defined]
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
        tag_repo = AsyncTagRepositoryWithID(self.session)

        # Create news
        news = await self.add(news_data)

        # Add tags
        for txt in tag_texts:
            tag = await tag_repo.get_or_create(txt)
            # Create link manually
            link = ParsedNewsTagLink(news_item_id=news.id, tag_id=tag.id)
            self.session.add(link)

        # Flush to ensure all objects have IDs but don't commit
        await self.session.flush()
        await self.session.refresh(news, ["tags"])
        logger.info(f"Prepared news with ID: {news.id} and {len(tag_texts)} tags")
        return news

    async def get_by_time_delta(
        self,
        delta: datetime.timedelta,
        input_news_delta: datetime.timedelta | None = None,
    ) -> Sequence[ParsedNews]:
        """
        Get parsed news updated within a time delta from now.

        Args:
            delta: Time delta to look back from current time for updated_at
            input_news_delta: Optional time delta to filter by input_news timestamp.
                             If None, no additional input_news filtering is applied.

        Returns:
            List of ParsedNews within the time delta criteria
        """
        logger.debug(f"Getting news by time delta: {delta}, input_news_delta: {input_news_delta}")
        from_date = datetime.datetime.utcnow() - delta

        conditions = [ParsedNews.updated_at >= from_date]

        if input_news_delta is not None:
            input_news_from_date = datetime.datetime.utcnow() - input_news_delta
            input_news_condition = not_(
                exists().where(
                    and_(InputNews.parsed_news == ParsedNews.id, InputNews.received_at < input_news_from_date)
                )
            )
            conditions.append(cast(bool, input_news_condition))

        statement = select(ParsedNews).where(and_(*conditions))
        result = await self.session.execute(statement)
        news_list = result.scalars().all()
        logger.info(
            f"Retrieved {len(news_list)} news articles from time delta: {delta}"
            f"{' with input_news_delta filter' if input_news_delta else ''}"
        )
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

        tag_repo = AsyncTagRepositoryWithID(self.session)
        news.updated_at = datetime.datetime.utcnow()
        statement = select(ParsedNewsTagLink).where(ParsedNewsTagLink.news_item_id == news_id)
        result = await self.session.execute(statement)
        existing_links = result.scalars().all()

        logger.debug(f"Removing existing tag links: {existing_links}")
        for link in existing_links:
            await self.session.delete(link)

        logger.debug(f"Adding new tag links: {tag_texts}")
        for txt in tag_texts:
            tag = await tag_repo.get_or_create(txt)
            link = ParsedNewsTagLink(news_item_id=news_id, tag_id=tag.id)
            self.session.add(link)

        await self.session.flush()
        await self.session.refresh(news, ["tags"])
        logger.info(f"Successfully updated news ID: {news_id} with {tag_texts} tags")

        return news

    async def get_latest_received_timestamp(self) -> datetime.datetime | None:
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

    async def get_parsed_news_by_pick_hash(self, pick_hash: str) -> Sequence[ParsedNews]:
        """Get all parsed news items for a pick with the given hash."""
        logger.debug(f"Getting parsed news for pick hash: {pick_hash}")
        statement = (
            select(ParsedNews)
            .join(NewsPickItem, ParsedNews.id == NewsPickItem.parsed_news_id)  # type: ignore[arg-type]
            .join(NewsPick, NewsPickItem.pick_id == NewsPick.id)  # type: ignore[arg-type]
            .where(NewsPick.hash == pick_hash)
            .order_by(ParsedNews.updated_at.desc())  # type: ignore[attr-defined]
            .options(
                joinedload(ParsedNews.topic),
                joinedload(ParsedNews.tags),
            )
        )

        result = await self.session.execute(statement)
        parsed_news_items = result.scalars().unique().all()

        logger.info(f"Found {len(parsed_news_items)} parsed news items for pick hash '{pick_hash}'")
        return parsed_news_items

    async def get_news_by_creation_day(self, date: datetime.date) -> Sequence[ParsedNews]:
        """Get all news items created on the given day."""
        logger.debug(f"Getting news from day: {date}")
        statement = select(ParsedNews).where(func.date(ParsedNews.created_at) == date)
        result = await self.session.execute(statement)
        news_items = result.scalars().all()
        logger.info(f"Found {len(news_items)} news items from day '{date}'")
        return news_items

    async def get_latest_pick_news_for_account(self, email: str) -> list[ParsedNews]:
        """Get all the latest pick news for an account."""
        logger.debug(f"Getting all latest pick news for account: {email}")
        latest_pick_subquery = (
            select(NewsPick.id)
            .join(Account, NewsPick.account_id == Account.id)  # type: ignore[arg-type]
            .where(Account.email == email)
            .order_by(NewsPick.created_at.desc())  # type: ignore[attr-defined]
            .limit(1)
            .scalar_subquery()
        )

        statement = (
            select(ParsedNews)
            .join(NewsPickItem, ParsedNews.id == NewsPickItem.parsed_news_id)  # type: ignore[arg-type]
            .where(NewsPickItem.pick_id == latest_pick_subquery)
            .order_by(ParsedNews.updated_at.desc())  # type: ignore[attr-defined]
            .options(
                joinedload(ParsedNews.topic),
                joinedload(ParsedNews.tags),
            )
        )

        result = await self.session.execute(statement)
        parsed_news_items = result.scalars().unique().all()

        logger.info(f"Found {len(parsed_news_items)} parsed news items from latest pick for user '{email}'")
        return list(parsed_news_items)


class AsyncAccountRepositoryWithID(AsyncBaseRepositoryWithID[Account]):
    """Async repository for Account model."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Account)
        logger.info("AsyncAccountRepository initialized")

    async def update_prompt(self, email: str, prompt: str) -> Account | None:
        """Updates prompt for an account by email."""
        logger.debug(f"Updating prompt for email: {email}")
        statement = select(Account).where(Account.email == email)
        result = await self.session.execute(statement)
        account = result.scalars().first()
        if account:
            account.prompt = prompt
            await self.session.flush()
            await self.session.refresh(account)
            logger.info(f"Updated prompt for email: {email}")
        else:
            logger.warn(f"Account with email {email} not found")
        return account

    async def get_by_email(self, email: str) -> Account | None:
        """Get account by email."""
        logger.debug(f"Getting account by email: {email}")
        statement = select(Account).where(Account.email == email)
        result = await self.session.execute(statement)
        account = result.scalars().first()
        logger.info(f"Retrieved account with email: {email}")
        return account

    async def delete_by_email(self, account_email: str) -> None:
        """Delete account by email."""
        logger.debug(f"Deleting account by email: {account_email}")
        statement = select(Account).where(Account.email == account_email)
        result = await self.session.execute(statement)
        account = result.scalars().first()
        if account:
            await self.session.delete(account)
            await self.session.commit()
            logger.info(f"Deleted account with email: {account_email}")
        else:
            logger.warn(f"Account with email {account_email} not found")

    async def create_deletion_token(
        self,
        email: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        expiry_hours: int = 24,
    ) -> TokenGenerationResponse:
        """
        Create a deletion token for an account.

        Args:
            email: Email of the account to delete
            ip_address: IP address of the requester
            user_agent: User agent string of the requester
            expiry_hours: Hours until token expires (default 24)

        Returns:
            Tuple of (plain_token, token_record)

        Raises:
            AccountNotFoundException: If account with email doesn't exist
        """
        logger.debug(f"Creating deletion token for email: {email}")

        # Find account
        account = await self.get_by_email(email)
        if not account:
            logger.warn(f"Account with email {email} not found for deletion token creation")
            raise AccountNotFoundException(email=email)

        # Generate token
        tokens = TokenGenerator.generate_and_hash()
        token_hash = tokens["hash_token"]
        plain_token = tokens["plain_token"]
        expires_at = TokenGenerator.get_expiration_time(hours=expiry_hours)

        token_record = AccountDeletionToken(
            account_id=account.id,
            token_hash=token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else None,  # Truncate to 500 chars
        )

        self.session.add(token_record)
        await self.session.flush()
        await self.session.refresh(token_record)

        logger.info(f"Created deletion token for account ID: {account.id}, expires at: {expires_at.isoformat()}")

        return {"token_record": token_record, "plain_token": plain_token}

    async def verify_and_delete_account(
        self,
        plain_token: str,
    ) -> None:
        """
        Verify deletion token and delete account if valid.

        Args:
            plain_token: The plain text token from the email link

        Raises:
            TokenNotFoundException: If token doesn't exist
            TokenAlreadyUsedException: If token was already used
            TokenExpiredException: If token has expired
            AccountNotFoundException: If account doesn't exist
            AccountDeletionFailedException: If deletion fails for any reason
        """
        logger.debug("Verifying deletion token and attempting account deletion")

        # Hash the token to find it in database
        token_hash = TokenGenerator.hash_token(plain_token)

        # Find token
        statement = select(AccountDeletionToken).where(AccountDeletionToken.token_hash == token_hash)
        result = await self.session.execute(statement)
        token_record = result.scalars().first()
        if token_record is None:
            raise TokenNotFoundException()
        try:
            TokenGenerator.validate_token(token_record)
            account = await self.session.get(Account, token_record.account_id)
            if not account:
                logger.error(f"Account with ID {token_record.account_id} not found")
                raise AccountNotFoundException()

            logger.info(f"Starting deletion process for account ID: {account.id}, email: {account.email}")

            # Mark token as used
            token_record.used_at = datetime.datetime.utcnow()
            # Finally delete the Account
            await self.delete_by_email(account_email=account.email)
            # Flush changes to database
            await self.session.flush()

            logger.info(f"Successfully deleted account ID: {account.id}, email: {account.email}")

        except (TokenNotFoundException, TokenAlreadyUsedException, TokenExpiredException, AccountNotFoundException):
            # Re-raise our custom exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Failed to delete account: {str(e)}", exc_info=True)
            raise AccountDeletionFailedException(reason=str(e)) from e
