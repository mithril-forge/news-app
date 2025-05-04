import json
import os
import pathlib
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Any, Iterable

import instructor
from instructor import AsyncInstructor
from pydantic import BaseModel
import google.generativeai as genai

from core.converters import orm_list_to_pydantic
from features.api_service.database.repository import AsyncTagRepository
from features.api_service.services.news_service import NewsService
from features.api_service.services.schemas import TagResponse, TopicResponse, NewsResponseDetailed
from features.api_service.services.topic_service import TopicService
from features.input_news_processing.ai_library.abstract_model import AbstractAIModel
from features.input_news_processing.archive.abstract_archive import AbstractArchive
from features.input_news_processing.services.ai_prompts import CREATION_PROMPT, CONNECTION_PROMPT, PICTURE_SEARCH_PROMPT
from features.input_news_processing.services.input_news_service import InputNewsService
from features.input_news_processing.services.schemas import ParsedNewsWithInputNews, ConnectionResult, \
    CreationResult, InputNewsWithID, ImageDetail


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
        paths_mapping: dict[str, Path] = {}
        for list_name, model_list in kwargs.items():
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

        return paths_mapping

    async def prepare_actual_data_for_ai(self, delta: timedelta) -> dict[str, Path]:
        """ Prepares needed data for the AI queries. It can be adjusted by delta by which the news are taken"""
        recent_input_news = await self.input_news_service.get_input_news_by_delta(delta=delta,
                                                                                  has_parsed_news=False)
        recent_parsed_news = await self.input_news_service.get_parsed_with_input_news(delta=delta)
        existing_topics = await self.topic_service.get_all_topics()
        existing_tags = orm_list_to_pydantic(await self.tag_repository.get_all(), TagResponse)
        files = self.save_pydantic_lists_as_files(tags_list=existing_tags, topics_list=existing_topics,
                                                  recent_parsed_news=recent_parsed_news,
                                                  recent_input_news=recent_input_news)
        return files

    async def creates_new_news(self, delta: timedelta) -> list[NewsResponseDetailed]:
        """
        Loads present data from DB, prepares gemini client with files and then prompt.
        Result should be newly created parsed news from Gemini model.
        """
        files = await self.prepare_actual_data_for_ai(delta=delta)
        result = await self.ai_model.prompt_model(files=files, prompt=CREATION_PROMPT,
                                                  response_model=Iterable[CreationResult])
        print(f"Result of the creation query is: {result=}")
        saved_news_list = []
        for news_data in result:
            saved_news = await self.parsed_news_service.create_news(news_data=news_data.parsed_news)
            for input_id in news_data.input_news_ids:
                await self.input_news_service.connect_input_with_parsed(input_id=input_id, parsed_id=saved_news.id)
            saved_news_list.append(saved_news)
        return saved_news_list

    async def connect_existing_news(self, delta: timedelta) -> list[NewsResponseDetailed]:
        """
        Loads present data from DB, prepares gemini client with files and then prompt.
        Result should be only connected parsed news from Gemini model.
        """
        files = await self.prepare_actual_data_for_ai(delta=delta)
        result = await self.ai_model.prompt_model(files=files, prompt=CONNECTION_PROMPT,
                                                  response_model=Iterable[ConnectionResult])
        print(f"Result of the creation query is: {result=}")
        updated_news_list = []
        for news_data in result:
            saved_news = await self.parsed_news_service.update_news(news_data=news_data.parsed_news)
            if saved_news is None:
                continue
            for input_id in news_data.input_news_ids:
                await self.input_news_service.connect_input_with_parsed(input_id=input_id, parsed_id=saved_news.id)
            updated_news_list.append(saved_news)
        return updated_news_list

    async def generate_picture_for_news(self, news_id: int) -> NewsResponseDetailed:
        """ Tries to search and link picture for the existing news"""
        news = await self.parsed_news_service.get_news_by_id(news_id=news_id)
        # TODO: Add support also for noniterable params
        news_as_file = self.save_pydantic_lists_as_files(news_detail=[news])
        # TODO: Fix search, somehow it doesn't work with the ChatGPT model here, but in the web UI it searches good for the query
        # TODO: I guess the issue can be that in UI AI works with multiple models and we query only one, please research and fix
        image_result = await self.ai_model.prompt_model(files=news_as_file, prompt=PICTURE_SEARCH_PROMPT, response_model=Iterable[ImageDetail])
        if len(list(image_result)) == 0:
            print(f"No results for the news {news_id}")
        print(image_result)
