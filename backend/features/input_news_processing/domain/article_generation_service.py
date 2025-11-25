import json
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Any

import structlog
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.converters import orm_list_to_pydantic
from core.domain.news_service import NewsService
from core.domain.schemas import (
    ParsedNewsCreate,
    ParsedNewsResponseDetailed,
    ParsedNewsUpdate,
    TagResponse,
)
from core.domain.topic_service import TopicService
from core.repository import AsyncTagRepositoryWithID
from features.input_news_processing.ai_library.get_model import get_ai_model
from features.input_news_processing.archive.abstract_archive import AbstractArchive
from features.input_news_processing.converters import input_news_list_to_schema
from features.input_news_processing.domain.ai_prompts import (
    INITIAL_CONNECTION_PROMPT,
    INITIAL_GENERATION_PROMPT,
    NEW_CONNECTION_PROMPT,
    NEW_GENERATION_PROMPT,
    PICTURE_SEARCH_PROMPT,
)
from features.input_news_processing.domain.input_news_service import InputNewsService
from features.input_news_processing.domain.schemas import (
    ImageDetail,
    InitConnectionResult,
    InitGenerationResult,
)

logger = structlog.get_logger()


class TempFileStorage(BaseModel):
    recent_parsed_news: Path
    topics: Path
    tags: Path
    recent_input_news: Path


class ArticleGenerationService:
    def __init__(self, session: AsyncSession, archive: AbstractArchive) -> None:
        self.session = session
        self.topic_service = TopicService(session=session)
        self.input_news_service = InputNewsService(session=session, archive=archive)
        self.tag_repository = AsyncTagRepositoryWithID(session=session)
        self.parsed_news_service = NewsService(session=session)
        self.ai_model = get_ai_model()
        logger.info("ArticleGenerationService initialized")

    @staticmethod
    def save_pydantic_lists_as_files(**kwargs: list[Any]) -> dict[str, Path]:
        """
        Dumps data to files and returns their paths. This is a step to convert data from Pydantic models
        to files that are supported by Gemini and other AI models.

        Args:
            **kwargs: Named arguments where each value is a list of Pydantic BaseModel objects

        Returns:
            Dictionary mapping argument names to file paths where the data is stored
        """
        logger.debug(f"Saving {len(kwargs)} pydantic lists as files")
        paths_mapping: dict[str, Path] = {}
        for list_name, model_list in kwargs.items():
            logger.debug(f"Processing list: {list_name} with {len(model_list)} items")
            # Convert each model to a dict first, then the whole list will be properly serialized
            # TODO: model_dump is better, but problems with datetime
            data = [model.model_dump_json() for model in model_list]

            temp_file = tempfile.NamedTemporaryFile(suffix=".json", mode="w+", delete=False)

            json.dump(data, temp_file, indent=2)
            temp_file.close()

            paths_mapping[list_name] = Path(temp_file.name)
            logger.info(f"Saved {list_name} to file: {temp_file.name} ({len(model_list)} items)")

        logger.info(f"Successfully saved {len(kwargs)} lists to temporary files")
        return paths_mapping

    async def generate_and_attach_image_to_news(self, news_id: int) -> None:
        """
        Uses AI to search for relevant images and attach them to an existing news article.

        Args:
            news_id: The ID of the news article to generate images for

        Returns:
            Updated news article with attached images
        """
        logger.info(f"Generating picture for news ID: {news_id}")
        news = await self.parsed_news_service.get_news_by_id(news_id=news_id)
        # TODO: Add support also for noniterable params
        news_as_file = self.save_pydantic_lists_as_files(news_detail=[news])
        # TODO: Fix search, somehow it doesn't work with the ChatGPT model here,
        #  but in the web UI it searches good for the query
        # TODO: I guess the issue can be that in UI AI works with multiple models
        #  and we query only one, please research and fix
        logger.debug(f"Requesting image search for news: {news.title}")
        image_result = await self.ai_model.prompt_model(
            files=news_as_file,
            prompt=PICTURE_SEARCH_PROMPT,
            response_model=list[ImageDetail],
        )
        if image_result is None:
            raise ValueError(f"There is None result when generating new image for id {news_id}")
        result_list: list[ImageDetail] = list(image_result)
        if len(result_list) == 0:
            logger.warn(f"No image results found for news ID: {news_id}")
        else:
            logger.info(f"Found {len(result_list)} image results for news ID: {news_id}")
        logger.debug(f"Image search results: {result_list}")

    async def connect_input_news_to_existing_articles(
        self, input_news_ids: list[int], parsed_news_hours_delta: int = 24, input_news_hours_delta: int = 72
    ) -> list[int]:
        """
        Uses AI to identify which new input news items should be connected to existing parsed articles
        based on content similarity and relevance.

        Args:
            input_news_ids: List of input news IDs to process for connections
            parsed_news_hours_delta: Hours to look back for existing parsed news (default: 24)
            input_news_hours_delta: Allowed hours for all input news of parsed ones, if not sufficient, the parsed news
            won't be connected to any input news


        Returns:
            List of parsed news IDs that received new connections
        """
        logger.info(
            f"Connecting {len(input_news_ids)} input news items to existing articles, "
            f"looking back {parsed_news_hours_delta} hours"
        )

        parsed_news_delta = timedelta(hours=parsed_news_hours_delta)
        input_news_delta = timedelta(hours=input_news_hours_delta)
        recent_input_news = await self.input_news_service.get_input_news_by_ids_lite(
            input_news_ids=input_news_ids, has_parsed_news=False
        )
        recent_parsed_news = await self.parsed_news_service.get_parsed_news_summary(
            parsed_news_delta=parsed_news_delta, input_news_delta=input_news_delta
        )
        logger.debug(
            f"Retrieved {len(recent_input_news)} input news and {len(recent_parsed_news)} "
            f"parsed news for connection analysis"
        )

        files = self.save_pydantic_lists_as_files(parsed_news=recent_parsed_news, input_news=recent_input_news)
        logger.debug("Prepared data files for AI connection analysis")

        result = await self.ai_model.prompt_model(
            files=files,
            prompt=INITIAL_CONNECTION_PROMPT,
            response_model=list[InitConnectionResult],
        )
        if result is None:
            raise ValueError(f"AI model returned empty result when connecting new articles from ids {input_news_ids}")
        logger.debug(f"AI model returned {len(result)} connection suggestions")

        parsed_news_ids_set = set(news.id for news in recent_parsed_news)
        input_news_ids_set = set(news.id for news in recent_input_news)

        result = [
            res
            for res in result
            if res.parsed_news_id in parsed_news_ids_set
            and all(input_news_id in input_news_ids_set for input_news_id in res.input_news_ids)
        ]
        logger.debug(f"Filtered to {len(result)} valid connection results")

        connection_count = 0
        for connection_result in result:
            for input_id in connection_result.input_news_ids:
                await self.input_news_service.connect_input_with_parsed(
                    input_id=input_id, parsed_id=connection_result.parsed_news_id
                )
                connection_count += 1

        updated_parsed_ids = [
            conn_result.parsed_news_id for conn_result in result if len(conn_result.input_news_ids) > 0
        ]
        logger.info(
            f"Successfully created {connection_count} connections, updated {len(updated_parsed_ids)} parsed articles"
        )

        return updated_parsed_ids

    async def choose_input_news_for_new_articles(
        self, input_news_ids: list[int], news_limit: int = 20
    ) -> list[InitGenerationResult]:
        """
        Uses AI to analyze input news and group related articles together, ranked by importance.

        Args:
            input_news_ids: List of input news IDs to analyze and group
            news_limit: Maximum number of news groups to return (default: 20)

        Returns:
            List of grouped input news ID lists, ordered by importance
        """
        recent_input_news = await self.input_news_service.get_input_news_by_ids_lite(
            input_news_ids=input_news_ids, has_parsed_news=False
        )
        files = self.save_pydantic_lists_as_files(recent_input_news=recent_input_news)
        result = await self.ai_model.prompt_model(
            files=files,
            prompt=INITIAL_GENERATION_PROMPT,
            response_model=list[InitGenerationResult],
        )
        if result is None:
            raise ValueError(f"AI model returned empty result when creating new articles from ids {input_news_ids}")
        input_news_ids = [news.id for news in recent_input_news]
        result = [
            res
            for res in result
            if all(news_id in input_news_ids for news_id in res.input_news_ids) and len(res.input_news_ids) > 0
        ]
        logger.debug(f"Initial generation results: {result}")
        result = sorted(result, key=lambda x: x.importancy, reverse=True)[:news_limit]
        logger.info(f"Returning generation results after importancy filtering/sorting: {result}")
        final_groups = [gen_result for gen_result in result]
        return final_groups

    async def create_new_article_from_input_news(
        self, input_news_ids: list[int], importancy: int
    ) -> ParsedNewsResponseDetailed:
        """
        Creates a new parsed article by combining and processing multiple related input news items using AI.

        Args:
            input_news_ids: List of input news IDs to combine into a single article
            importancy: news importancy which will be used when showing the results
        Returns:
            The newly created parsed news article with all connections established
        """
        logger.info(f"Creating new article from {len(input_news_ids)} input news items: {input_news_ids}")

        input_news_list = await self.input_news_service.input_news_repo.get_by_ids(ids=input_news_ids)
        logger.debug(f"Retrieved {len(input_news_list)} input news records from database")

        input_news_pydantic = input_news_list_to_schema(input_news_list=input_news_list)
        existing_topics = await self.topic_service.get_all_topics()
        existing_tags = orm_list_to_pydantic(await self.tag_repository.get_all(), TagResponse)
        logger.debug(f"Prepared context data - topics: {len(existing_topics)}, tags: {len(existing_tags)}")

        files = self.save_pydantic_lists_as_files(
            input_news_list=input_news_pydantic,
            existing_tags=existing_tags,
            existing_topics=existing_topics,
        )
        logger.debug("Generated data files for AI article creation")

        result = await self.ai_model.prompt_model(
            files=files, prompt=NEW_GENERATION_PROMPT, response_model=ParsedNewsCreate
        )
        if result is None:
            raise ValueError(f"AI model didn't return proper result when creating new article from {input_news_ids}")
        logger.debug(f"AI model generated article: '{result.title}' with {len(result.content)} characters")

        saved_news = await self.parsed_news_service.create_news(news_data=result, importancy=importancy)
        logger.info(f"Successfully created new article: '{saved_news.title}' (ID: {saved_news.id})")

        for input_id in input_news_ids:
            await self.input_news_service.connect_input_with_parsed(input_id=input_id, parsed_id=saved_news.id)

        logger.info(f"Connected {len(input_news_ids)} input news items to new article (ID: {saved_news.id})")
        return saved_news

    async def enrich_existing_article(self, parsed_news_id: int) -> ParsedNewsResponseDetailed:
        """
        Enhances an existing parsed article by using AI to improve content, add tags, or update topics.

        Args:
            parsed_news_id: ID of the existing parsed news article to enrich

        Returns:
            The updated news article with AI-generated enhancements
        """
        logger.info(f"Enriching existing article with ID: {parsed_news_id}")

        parsed_news = await self.parsed_news_service.get_news_by_id(news_id=parsed_news_id)
        logger.debug(f"Retrieved article for enrichment: '{parsed_news.title}'")

        existing_topics = await self.topic_service.get_all_topics()
        existing_tags = orm_list_to_pydantic(await self.tag_repository.get_all(), TagResponse)
        logger.debug(f"Loaded context data - topics: {len(existing_topics)}, tags: {len(existing_tags)}")

        files = self.save_pydantic_lists_as_files(
            parsed_news=[parsed_news],
            existing_topics=existing_topics,
            existing_tags=existing_tags,
        )
        logger.debug("Prepared data files for AI article enrichment")

        result = await self.ai_model.prompt_model(
            files=files, prompt=NEW_CONNECTION_PROMPT, response_model=ParsedNewsUpdate
        )
        logger.debug(f"AI model generated enrichment updates for article ID: {parsed_news_id}")
        if result is None:
            raise ValueError(f"AI model didn't return proper result when enriching article {parsed_news_id}")
        saved_news = await self.parsed_news_service.update_news(news_data=result)
        logger.info(f"Successfully enriched article: '{saved_news.title}' (ID: {saved_news.id})")

        return saved_news
