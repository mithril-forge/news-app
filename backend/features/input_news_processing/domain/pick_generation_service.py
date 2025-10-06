import datetime
import os

import structlog
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.domain.account_service import AccountService
from core.domain.news_service import NewsService
from core.models import NewsPick, NewsPickItem
from core.redis_client import redis_client
from core.repository import AsyncBaseRepository, AsyncBaseRepositoryWithID
from features.input_news_processing.ai_library.gemini_model import GeminiAIModel
from features.input_news_processing.domain.ai_prompts import CUSTOM_ARTICLES_PROMPT
from features.input_news_processing.domain.article_generation_service import ArticleGenerationService

logger = structlog.get_logger()


class PickGenerationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.pick_repository = AsyncBaseRepositoryWithID[NewsPick](session, NewsPick)
        self.pick_items_repository = AsyncBaseRepository[NewsPickItem](session, NewsPickItem)

    async def save_pick(self, account_id: int | None, description: str) -> int:
        """Save pick to the database."""
        pick = await self.pick_repository.add({"account_id": account_id, "description": description})
        if pick.id is None:
            raise ValueError("Pick should have correct id")
        return pick.id

    async def connect_news_to_pick(self, pick_id: int, news_ids: list[int]) -> None:
        """Connect news to the pick."""
        for news_id in news_ids:
            await self.pick_items_repository.add({"pick_id": pick_id, "parsed_news_id": news_id})

    async def generate_pick_anonymous(self, prompt: str, news_age_in_hours: int, description: str | None = None) -> str:
        """
        Generate a news pick for an anonymous user based on the provided prompt.

        Args:
            prompt: The prompt text to guide the pick generation.
            news_age_in_hours: How old news to use and parse
            description: Description for the pick

        Returns:
            A dictionary containing the pick hash and a success message.
        """
        logger.info(f"Starting pick generation for anonymous user with prompt: {prompt[:50]}...")

        pick_hash = await self._invoke_pick_generation(
            prompt, account_id=None, news_age_in_hours=news_age_in_hours, description=description
        )

        return pick_hash

    async def generate_pick_logged_in_user(
        self, user_email: str, news_age_in_hours: int, bypass_daily_limit: bool = False, description: str | None = None
    ) -> str:
        """
        Generate a news pick for a logged-in user based on their stored prompt.

        Args:
            news_age_in_hours: age of the news in hours
            user_email: The email of the logged-in user.
            bypass_daily_limit: If True, skip daily limit checking (for system-generated picks).

        Returns:
            A dictionary containing the pick hash and a success message.
        """
        account_service = AccountService(self.session)
        account_details = await account_service.get_account_details(account_email=user_email)

        if not account_details or not account_details.prompt:
            raise HTTPException(status_code=400, detail="User must have a prompt set")

        prompt = account_details.prompt

        today = datetime.date.today()
        # Check daily limit for logged-in users (1 generation per day)
        # Skip daily limit for system-generated picks (when bypass_daily_limit is True)
        if not bypass_daily_limit:
            daily_limit_key = f"daily_generation_user_{user_email}_{today}"
            logger.info(f"Checking daily limit for user {user_email}: {daily_limit_key}")
            if redis_client.has_daily_limit(daily_limit_key):
                logger.warning(f"Daily limit reached for user {user_email}")
                raise HTTPException(
                    status_code=429, detail="Daily generation limit reached. You can generate only one pick per day."
                )

        logger.info(f"Starting pick generation for user {user_email} with prompt: {prompt[:50]}...")

        pick_hash = await self._invoke_pick_generation(
            prompt, account_id=account_details.id, news_age_in_hours=news_age_in_hours, description=description
        )

        # Update daily limits (only for user-initiated picks, not system-generated picks)
        if user_email and not bypass_daily_limit:
            redis_client.set_daily_limit(
                daily_limit_key,
                {"timestamp": datetime.datetime.now().isoformat(), "user_email": user_email, "pick_hash": pick_hash},
            )

        return pick_hash

    async def _invoke_pick_generation(
        self, user_prompt: str, account_id: int | None, news_age_in_hours: int, description: str | None = None
    ) -> str:
        """Invoke the AI model to generate a pick based on the user prompt and available news.

        Args:
            user_prompt: The prompt text to guide the pick generation.
            account_id: Account ID of the user (None for anonymous).

        Returns:
            A string representing the pick hash.
        """
        description = description or user_prompt
        use_mocked_ai = os.getenv("USE_MOCKED_AI", "false").lower() == "true"
        news_service = NewsService(session=self.pick_repository.session)

        try:
            news_age_timedelta = datetime.timedelta(hours=news_age_in_hours)
            logger.info(f"Fetching news from the last {news_age_in_hours} hours")
            parsed_news = await news_service.get_news_titles_by_time_delta(delta=news_age_timedelta)
            logger.info(f"Found {len(parsed_news) if parsed_news else 0} news items from the last 36 hours")

            if not parsed_news:
                logger.warning("No news available from the last 36 hours")
                raise HTTPException(status_code=404, detail="No recent news available from the last 36 hours")

            if use_mocked_ai:
                # Mocked version - just return first few article IDs instead of using AI, for testing
                news_ids = [news.id for news in parsed_news[:3]]
                logger.info(f"Mocked pick generation using first {len(news_ids)} articles: {news_ids}")
            else:
                # Real AI-based generation
                gemini_api_key = os.getenv("GEMINI_API_KEY")
                if gemini_api_key is None:
                    raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable not set")

                gemini_ai_model = GeminiAIModel(api_key=gemini_api_key)
                prompt_formatted = CUSTOM_ARTICLES_PROMPT.format(prompt=user_prompt)

                files = ArticleGenerationService.save_pydantic_lists_as_files(parsed_news=parsed_news)
                result = await gemini_ai_model.prompt_model(
                    files=files, prompt=prompt_formatted, response_model=list[int]
                )
                logger.info(f"Successfully generated pick with news ids: {result}")
                news_ids = result or []  # Use empty list if no results

            # Save the pick to the database
            pick_id = await self.save_pick(account_id=account_id, description=description)
            # Get the pick hash to return
            pick_result = await self.session.execute(select(NewsPick).where(NewsPick.id == pick_id))
            pick_hash = pick_result.scalar_one().hash

            # Only connect news if there are articles to connect
            if news_ids:
                await self.connect_news_to_pick(pick_id=pick_id, news_ids=news_ids)
            else:
                logger.warning(f"No news items matched the prompt, but pick was saved with ID: {pick_id}")

            logger.info(
                f"Successfully generated pick with ID {pick_id} and hash {pick_hash}, saved {len(news_ids)} articles"
            )
            return pick_hash
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error generating pick: {e}")
            raise HTTPException(status_code=500, detail=f"Error generating pick: {str(e)}") from e
