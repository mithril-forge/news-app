import datetime

import structlog
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.converters import (
    news_list_to_response,
    news_list_to_titles_response,
    news_to_detailed_response,
    orm_list_to_pydantic,
    relevance_parsed_news_list_to_basic_response,
)
from core.domain.account_service import AccountService
from core.domain.schemas import (
    NewsPickResponse,
    ParsedInputNewsTitles,
    ParsedNewsBasic,
    ParsedNewsCreate,
    ParsedNewsResponseDetailed,
    ParsedNewsSummary,
    ParsedNewsUpdate,
    TagResponse,
)
from core.models import Account, NewsPick
from core.repository import (
    AsyncParsedNewsRepositoryWithID,
    AsyncTagRepositoryWithID,
    AsyncTopicRepositoryWithID,
)

logger = structlog.get_logger()


class NewsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.news_repo = AsyncParsedNewsRepositoryWithID(session)
        self.topic_repo = AsyncTopicRepositoryWithID(session)
        self.tag_repo = AsyncTagRepositoryWithID(session)
        logger.info("NewsService initialized")

    async def refresh_materialized_view(self) -> None:
        """Refreshes materialized view so order of articles is generated and updated"""
        await self.news_repo.refresh_materialized_view()

    async def get_tags(self) -> list[TagResponse]:
        logger.debug("Getting all tags")
        tag_models = await self.tag_repo.get_all()
        result = orm_list_to_pydantic(tag_models, TagResponse)
        logger.info(f"Retrieved {len(result)} tags")
        logger.debug(f"Tags: {[tag.model_dump_json() for tag in result]}")
        return result

    async def get_latest_news(self, skip: int, limit: int) -> list[ParsedNewsBasic]:
        """Get the latest N news items"""
        logger.info(f"Fetching latest news (skip={skip}, limit={limit})")
        latest_news = await self.news_repo.get_latest(skip=skip, limit=limit)
        logger.debug(f"Retrieved {len(latest_news)} latest news items")
        return news_list_to_response(latest_news)

    async def get_latest_news_by_relevancy(self, skip: int, limit: int) -> list[ParsedNewsBasic]:
        """Get the latest N news items"""
        logger.info(f"Fetching latest news (skip={skip}, limit={limit})")
        latest_news = await self.news_repo.get_latest_by_relevance(skip=skip, limit=limit)
        logger.debug(f"Retrieved {len(latest_news)} latest news items")
        return relevance_parsed_news_list_to_basic_response(latest_news)

    async def get_most_popular_news(self, period: datetime.timedelta, limit: int) -> list[ParsedNewsBasic]:
        logger.info(f"Fetching {limit} most popular news for {period}")
        popular_news = await self.news_repo.get_most_viewed_news_by_period(period=period, limit=limit)
        result = news_list_to_response(popular_news)
        logger.info(f"Retrieved {len(result)} most popular news items")
        return result

    async def get_news_by_id(self, news_id: int) -> ParsedNewsResponseDetailed:
        """Get a specific news item by ID"""
        logger.info(f"Fetching news by ID: {news_id}")
        news = await self.news_repo.get_with_tags(news_id)
        if not news:
            logger.warning(f"News with ID {news_id} not found")
            raise HTTPException(status_code=404, detail="News not found")

        result = news_to_detailed_response(news)
        logger.info(f"Successfully retrieved news by ID: {news_id}")
        logger.debug(f"News content: {result.model_dump_json(exclude={'content', 'description'})}")
        return result

    async def add_view_to_news(self, news_id: int) -> None:
        """Add view to the news"""
        logger.debug(f"Adding view to news ID: {news_id}")
        await self.news_repo.add_view_to_news(news_id=news_id)
        logger.debug(f"Successfully added view to news ID: {news_id}")

    async def get_news_by_topic(self, topic_id: int, limit: int, skip: int) -> list[ParsedNewsBasic]:
        """Get all news for a specific topic"""
        logger.info(f"Fetching news for topic ID {topic_id} (skip={skip}, limit={limit})")
        sorted_news = await self.news_repo.get_by_topic_id(topic_id=topic_id, limit=limit, skip=skip)
        logger.info(f"Fetched {len(sorted_news)} for topic {topic_id}")
        logger.debug(f"Retrieved news ids: {[news.id for news in sorted_news]}")
        return news_list_to_response(sorted_news)

    async def create_news(self, news_data: ParsedNewsCreate, importancy: int) -> ParsedNewsResponseDetailed:
        """Create a new news item with tags"""
        logger.info(f"Creating new article with title: {news_data.title}")
        logger.debug(f"News data creation content: {news_data.model_dump_json(exclude={'content', 'description'})}")
        tag_texts = news_data.tags or []
        logger.debug(f"News tags: {', '.join(tag_texts) if tag_texts else 'None'}")

        # TODO: Image url ignored now and made static
        news_dict = news_data.dict(exclude={"tags", "image_url"})
        news_dict["image_url"] = (
            "https://st2.depositphotos.com/4431055/11871/i/600/depositphotos_118715222-stock-photo-businessman-reading-newspaper.jpg"
        )
        news_dict["importancy"] = importancy
        news = await self.news_repo.prepare_with_tags(news_dict, tag_texts)
        logger.info(f"Created news item with ID: {news.id}")
        news_id = news.id
        if news_id is None:
            raise ValueError(f"News {news} doesn't have properly set id.")
        complete_news = await self.news_repo.get_with_tags(news_id)
        if complete_news is None:
            raise ValueError(f"News for ID {news_id} not found even when it should be newly created")
        result = news_to_detailed_response(complete_news)
        logger.info(f"Successfully created and retrieved complete news item with ID: {news.id}")
        logger.debug(f"News data: {news_data.model_dump_json(exclude={'content', 'description'})}")
        return result

    async def update_news(self, news_data: ParsedNewsUpdate) -> ParsedNewsResponseDetailed:
        """
        Update an existing news item including its tags

        Args:
            news_data: News data with updated fields and tags

        Returns:
            Updated news item with detailed information

        Raises:
            HTTPException: If news item not found
        """
        logger.info(f"Updating news item with ID: {news_data.id}")
        logger.debug(f"Update news_data content: {news_data.model_dump_json(exclude={'content', 'description'})}")
        existing_news = await self.news_repo.get_by_id(news_data.id)
        if not existing_news:
            raise ValueError(f"News with ID {news_data.id} not found for update")

        # TODO: Image url due to unsupported images right now, this will be fixed
        update_data = news_data.dict(exclude={"tags", "id", "image_url"})

        tag_texts = news_data.tags or []
        logger.debug(f"Updating news tags to: {', '.join(tag_texts) if tag_texts else 'None'}")

        # Call repository method to handle the update and tag linking
        await self.news_repo.update_with_tags(news_id=news_data.id, news_data=update_data, tag_texts=tag_texts)

        # Get the completely updated news with tags
        complete_news = await self.news_repo.get_with_tags(news_data.id)
        if complete_news is None:
            raise ValueError(f"News for ID {news_data.id} not found even when it should be newly updated")
        logger.info(f"Successfully updated news item with ID: {news_data.id}")
        result = news_to_detailed_response(complete_news)
        logger.debug(f"Updated news_data content: {news_data.model_dump_json(exclude={'content', 'description'})}")
        return result

    async def get_latest_timestamp(self) -> datetime.datetime | None:
        """
        Returns latest timestamp of the input news
        """
        logger.debug("Getting latest timestamp of the input news...")
        result = await self.news_repo.get_latest_received_timestamp()
        logger.info(f"Latest timestamp of input news retrieved: {result}")
        return result

    async def get_parsed_news_summary(
        self, parsed_news_delta: datetime.timedelta, input_news_delta: datetime.timedelta
    ) -> list[ParsedNewsSummary]:
        """
        Returns ParsedNews with minimal information about them - title, description and other information
        """
        result = await self.news_repo.get_by_time_delta(delta=parsed_news_delta, input_news_delta=input_news_delta)
        pydantic_structures = orm_list_to_pydantic(orm_list=result, pydantic_class=ParsedNewsSummary)
        return pydantic_structures

    async def get_news_titles_by_date(self, date: datetime.date) -> list[ParsedInputNewsTitles]:
        """Returns ParsedNews with minimal information about them - title, description and other information"""
        result = await self.news_repo.get_news_by_creation_day(date=date)
        pydantic_structures = news_list_to_titles_response(news_list=result)
        return pydantic_structures

    async def get_news_titles_by_time_delta(self, delta: datetime.timedelta) -> list[ParsedInputNewsTitles]:
        """Returns ParsedNews titles for pick generation within a time delta"""
        result = await self.news_repo.get_by_time_delta(delta=delta)
        pydantic_structures = news_list_to_titles_response(news_list=result)
        return pydantic_structures

    async def get_pick_by_hash(self, pick_hash: str) -> NewsPickResponse:
        """Get pick with articles and description by hash"""
        # Get the pick to retrieve the description
        result = await self.session.execute(select(NewsPick).where(NewsPick.hash == pick_hash))
        pick = result.scalar_one_or_none()

        if not pick:
            raise HTTPException(status_code=404, detail="Pick not found")

        # Get the news articles for this pick
        try:
            sorted_news = await self.news_repo.get_parsed_news_by_pick_hash(pick_hash=pick_hash)
            articles = news_list_to_response(sorted_news)
            logger.debug(f"Pick hash: {pick_hash} retrieved {len(articles)} articles")
        except Exception as e:
            # If we can't get articles but pick exists, return empty articles with the description
            logger.warning(f"Could not get articles for pick hash {pick_hash}: {e}")
            articles = []

        return NewsPickResponse(articles=articles, description=pick.description)

    async def get_latest_pick_for_user(self, account_email: str) -> NewsPickResponse:
        """Get latest pick with articles and description for user"""
        # Get the account
        account_result = await self.session.execute(select(Account).where(Account.email == account_email))
        account = account_result.scalar_one_or_none()

        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Get the latest pick for this account
        pick_result = await self.session.execute(
            select(NewsPick).where(NewsPick.account_id == account.id).order_by(NewsPick.created_at.desc()).limit(1)
        )
        latest_pick = pick_result.scalar_one_or_none()

        if not latest_pick:
            # Return empty response if no picks found
            return NewsPickResponse(articles=[], description="")

        # Get the news articles for this pick
        try:
            latest_news = await self.news_repo.get_latest_pick_news_for_account(email=account_email)
            articles = news_list_to_response(latest_news)
            logger.debug(f"Retrieved {len(articles)} articles for user: {account_email}")
        except Exception as e:
            # If we can't get articles but pick exists, return empty articles with the description
            logger.warning(f"Could not get articles for pick {latest_pick.id}: {e}")
            articles = []

        return NewsPickResponse(articles=articles, description=latest_pick.description)

    async def link_anonymous_pick_to_user(self, user_email: str, pick_hash: str) -> None:
        """Links an anonymous pick (by hash) to a user account."""

        logger.info(f"Linking anonymous pick {pick_hash} to user {user_email}")

        # Get account details to verify user exists
        account_service = AccountService(self.session)
        account_details = await account_service.get_account_details(account_email=user_email)

        if not account_details:
            raise HTTPException(status_code=404, detail="User account not found")

        # Find the anonymous pick by hash
        pick_result = await self.session.execute(
            select(NewsPick).where(NewsPick.hash == pick_hash, NewsPick.account_id.is_(None))
        )
        pick = pick_result.scalar_one_or_none()

        if not pick:
            raise HTTPException(status_code=404, detail="Anonymous pick not found or already linked")

        # Link the pick to the user account
        pick.account_id = account_details.id
        self.session.add(pick)
        await self.session.commit()

        logger.info(f"Successfully linked anonymous pick {pick_hash} to user {user_email}")
