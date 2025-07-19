import json
import os
import pathlib
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Any, Iterable

import instructor
import structlog
from instructor import AsyncInstructor
from pydantic import BaseModel
import google.generativeai as genai

from core.converters import orm_list_to_pydantic
from features.api_service.database.repository import AsyncTagRepository
from features.api_service.services.news_service import NewsService
from features.api_service.services.schemas import TagResponse, TopicResponse, NewsResponseDetailed, NewsCreate, \
    NewsUpdate
from features.api_service.services.topic_service import TopicService
from features.input_news_processing.ai_library.abstract_model import AbstractAIModel
from features.input_news_processing.archive.abstract_archive import AbstractArchive
from features.input_news_processing.converters import input_news_list_to_schema
from features.input_news_processing.services.ai_prompts import CREATION_PROMPT, CONNECTION_PROMPT, \
    PICTURE_SEARCH_PROMPT, INITIAL_CONNECTION_PROMPT, INITIAL_GENERATION_PROMPT, NEW_GENERATION_PROMPT, \
    NEW_CONNECTION_PROMPT
from features.input_news_processing.services.input_news_service import InputNewsService
from features.input_news_processing.services.schemas import ParsedNewsWithInputNews, ConnectionResult, \
    CreationResult, InputNewsWithID, ImageDetail, InitConnectionResult, InitGenerationResult

logger = structlog.get_logger()


class TempFileStorage(BaseModel):
    recent_parsed_news: Path
    topics: Path
    tags: Path
    recent_input_news: Path


class ArticleGenerationService:
    def __init__(self, session, archive: AbstractArchive, ai_model: AbstractAIModel):
        self.session = session
        self.topic_service = TopicService(session=session)
        self.input_news_service = InputNewsService(session=session, archive=archive)
        self.tag_repository = AsyncTagRepository(session=session)
        self.parsed_news_service = NewsService(session=session)
        self.ai_model = ai_model
        logger.info("ArticleGenerationService initialized")

    @staticmethod
    def save_pydantic_lists_as_files(**kwargs: list[BaseModel]) -> dict[str, Path]:
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

            temp_file = tempfile.NamedTemporaryFile(
                suffix='.json',
                mode='w+',
                delete=False
            )

            json.dump(data, temp_file, indent=2)
            temp_file.close()

            paths_mapping[list_name] = Path(temp_file.name)
            logger.info(f"Saved {list_name} to file: {temp_file.name} ({len(model_list)} items)")

        logger.info(f"Successfully saved {len(kwargs)} lists to temporary files")
        return paths_mapping

    async def prepare_actual_data_for_ai(self, delta: timedelta, include_parsed: bool = True) -> dict[str, Path]:
        """ Prepares needed data for the AI queries. It can be adjusted by delta by which the news are taken"""
        logger.info(f"Preparing data for AI with delta: {delta}, include_parsed: {include_parsed}")
        recent_parsed_news = []
        recent_input_news = await self.input_news_service.get_input_news_by_delta(delta=delta,
                                                                                  has_parsed_news=False)
        if include_parsed:
            recent_parsed_news = await self.input_news_service.get_parsed_with_input_news(delta=delta)
        existing_topics = await self.topic_service.get_all_topics()
        existing_tags = orm_list_to_pydantic(await self.tag_repository.get_all(), TagResponse)

        logger.debug(
            f"Data counts - input news: {len(recent_input_news)}, parsed news: {len(recent_parsed_news)}, topics: {len(existing_topics)}, tags: {len(existing_tags)}")

        files = self.save_pydantic_lists_as_files(tags_list=existing_tags, topics_list=existing_topics,
                                                  recent_parsed_news=recent_parsed_news,
                                                  recent_input_news=recent_input_news)
        logger.info("Successfully prepared data for AI")
        return files

    async def generate_picture_for_news(self, news_id: int) -> NewsResponseDetailed:
        """ Tries to search and link picture for the existing news"""
        logger.info(f"Generating picture for news ID: {news_id}")
        news = await self.parsed_news_service.get_news_by_id(news_id=news_id)
        # TODO: Add support also for noniterable params
        news_as_file = self.save_pydantic_lists_as_files(news_detail=[news])
        # TODO: Fix search, somehow it doesn't work with the ChatGPT model here, but in the web UI it searches good for the query
        # TODO: I guess the issue can be that in UI AI works with multiple models and we query only one, please research and fix
        logger.debug(f"Requesting image search for news: {news.title}")
        image_result = await self.ai_model.prompt_model(files=news_as_file, prompt=PICTURE_SEARCH_PROMPT,
                                                        response_model=list[ImageDetail])
        result_list = list(image_result)
        if len(result_list) == 0:
            logger.warn(f"No image results found for news ID: {news_id}")
        else:
            logger.info(f"Found {len(result_list)} image results for news ID: {news_id}")
        logger.debug(f"Image search results: {result_list}")

    async def initial_connect_new_input_news(self, input_news_ids: list[int], parsed_news_hours_delta: int = 72) -> \
            list[int]:
        parsed_news_delta = timedelta(hours=parsed_news_hours_delta)
        recent_input_news = await self.input_news_service.get_input_news_by_ids_lite(input_news_ids=input_news_ids,
                                                                                     has_parsed_news=False)
        recent_parsed_news = await self.parsed_news_service.get_parsed_news_summary(delta=parsed_news_delta)
        files = self.save_pydantic_lists_as_files(parsed_news=recent_parsed_news,
                                                  input_news=recent_input_news)
        result = await self.ai_model.prompt_model(files=files, prompt=INITIAL_CONNECTION_PROMPT,
                                                  response_model=list[InitConnectionResult])
        parsed_news_ids = set(news.id for news in recent_parsed_news)
        input_news_ids = set(news.id for news in recent_input_news)

        result = [
            res for res in result
            if res.parsed_news_id in parsed_news_ids
               and all(input_news_id in input_news_ids for input_news_id in res.input_news_ids)
        ]
        for connection_result in result:
            for input_id in connection_result.input_news_ids:
                await self.input_news_service.connect_input_with_parsed(input_id=input_id,
                                                                        parsed_id=connection_result.parsed_news_id)
        return [conn_result.parsed_news_id for conn_result in result if len(conn_result.input_news_ids) > 0]

    async def pick_corresponding_input_news(self, input_news_ids: list[int], news_limit: int = 20) -> list[list[int]]:
        """"""
        recent_input_news = await self.input_news_service.get_input_news_by_ids_lite(input_news_ids=input_news_ids,
                                                                                     has_parsed_news=False)
        files = self.save_pydantic_lists_as_files(recent_input_news=recent_input_news)
        result = await self.ai_model.prompt_model(files=files, prompt=INITIAL_GENERATION_PROMPT,
                                                  response_model=list[InitGenerationResult])
        input_news_ids = set(news.id for news in recent_input_news)
        result = [
            res for res in result
            if all(news_id in input_news_ids for news_id in res.input_news_ids) and len(res.input_news_ids) > 0
        ]
        logger.debug(f"Initial generation results: {result}")
        result = sorted(result, key=lambda x: x.importancy, reverse=True)[:news_limit]
        logger.info(f"Returning generation results after importancy filtering/sorting: {result}")
        return [gen_result.input_news_ids for gen_result in result]

    async def create_new_article(self, input_news_ids: list[int]) -> NewsResponseDetailed:
        """ """
        input_news_list = await self.input_news_service.input_news_repo.get_by_ids(ids=input_news_ids)
        input_news_pydantic = input_news_list_to_schema(input_news_list=input_news_list)
        existing_topics = await self.topic_service.get_all_topics()
        existing_tags = orm_list_to_pydantic(await self.tag_repository.get_all(), TagResponse)
        files = self.save_pydantic_lists_as_files(input_news_list=input_news_pydantic, existing_tags=existing_tags,
                                                  existing_topics=existing_topics)
        result = await self.ai_model.prompt_model(files=files, prompt=NEW_GENERATION_PROMPT,
                                                  response_model=NewsCreate)

        saved_news = await self.parsed_news_service.create_news(news_data=result)
        for input_id in input_news_ids:
            await self.input_news_service.connect_input_with_parsed(input_id=input_id, parsed_id=saved_news.id)
        logger.info(
            f"Created and connected news: {saved_news.title} (ID: {saved_news.id}) with input_ids {input_news_ids}")
        return saved_news

    async def enrich_existing_article(self, parsed_news_id: int) -> NewsResponseDetailed:
        """ """
        parsed_news = await self.parsed_news_service.get_news_by_id(news_id=parsed_news_id)
        existing_topics = await self.topic_service.get_all_topics()
        existing_tags = orm_list_to_pydantic(await self.tag_repository.get_all(), TagResponse)
        files = self.save_pydantic_lists_as_files(parsed_news=[parsed_news], existing_topics=existing_topics,
                                                  existing_tags=existing_tags)
        result = await self.ai_model.prompt_model(files=files, prompt=NEW_CONNECTION_PROMPT,
                                                  response_model=NewsUpdate)
        saved_news = await self.parsed_news_service.update_news(news_data=result)
        return saved_news
