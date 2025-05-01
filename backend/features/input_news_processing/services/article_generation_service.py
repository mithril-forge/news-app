import json
import os
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
from features.input_news_processing.archive.abstract_archive import AbstractArchive
from features.input_news_processing.services.ai_prompts import CREATION_PROMPT, CONNECTION_PROMPT
from features.input_news_processing.services.input_news_service import InputNewsService
from features.input_news_processing.services.schemas import ParsedNewsWithInputNews, InputNewsSchema, ConnectionResult, \
    CreationResult


class TempFileStorage(BaseModel):
    recent_parsed_news: Path
    topics: Path
    tags: Path
    recent_input_news: Path


class ArticleGenerationService:
    def __init__(self, session, archive: AbstractArchive):
        self.session = session
        self.topic_service = TopicService(session=session)
        self.input_news_service = InputNewsService(session=session, archive=archive)
        self.tag_repository = AsyncTagRepository(session=session)
        self.parsed_news_service = NewsService(session=session)

    @staticmethod
    def save_pydantic_lists_as_files(tags_list: list[TagResponse], topics_list: list[TopicResponse],
                                     recent_parsed_news: list[ParsedNewsWithInputNews],
                                     recent_input_news: list[InputNewsSchema]) -> TempFileStorage:
        """
        Dumps data to the files and returns their paths, this is step to convert data from Pydantic models
        to files that are supported by Gemini and other AI models
        """
        paths_mapping: dict[str, Path] = {}
        model_lists = {
            "recent_parsed_news": recent_parsed_news,
            "topics": topics_list,
            "tags": tags_list,
            "recent_input_news": recent_input_news
        }

        for list_name, model_list in model_lists.items():
            data = [model.model_dump_json() for model in model_list]
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.json',
                mode='w+',
                delete=False
            )

            json.dump(data, temp_file, indent=2)
            temp_file.close()

            paths_mapping[list_name] = Path(temp_file.name)

        return TempFileStorage(**paths_mapping)

    @staticmethod
    async def prepare_gemini_client(model_name: str = "gemini-2.5-pro-exp-03-25") -> AsyncInstructor:
        """ Prepares model encapsulate by instructor library for structured output."""
        gemini_api_key = os.environ["GEMINI_API_KEY"]
        if gemini_api_key is None:
            raise ValueError("You need to provide GEMINI_API_KEY")
        genai.configure(api_key=gemini_api_key)
        client = instructor.from_gemini(
            client=genai.GenerativeModel(
                model_name=model_name
                # model_name="gemini-2.0-pro-exp-02-05",
            ),
            mode=instructor.Mode.GEMINI_JSON,
            use_async=True  # Ensure async is enabled
        )
        return client

    @staticmethod
    def upload_files_gemini(file_storage: TempFileStorage) -> dict[str, genai.types.File]:
        """Uploads a file synchronously and returns the File objects"""
        results: dict[str, genai.types.File] = {}
        for key, file_path in file_storage.model_dump().items():
            if not file_path.exists():
                raise ValueError(f"File path {file_path} not found")
            file_obj = genai.upload_file(path=file_path, display_name=key, mime_type='text/plain')
            print(f"File uploaded successfully: URI = {file_obj.uri}")
            results[key] = file_obj
        return results

    async def prepare_actual_data_for_ai(self, delta: timedelta) -> TempFileStorage:
        """ Prepares needed data for the AI queries. It can be adjusted by delta by which the news are taken"""
        recent_input_news = await self.input_news_service.get_input_news_by_delta(delta=delta,
                                                                                  has_parsed_news=False)
        recent_parsed_news = await self.input_news_service.get_parsed_with_input_news(delta=delta)
        existing_topics = await self.topic_service.get_all_topics()
        existing_tags = orm_list_to_pydantic(await self.tag_repository.get_all(), TagResponse)
        file_storage = self.save_pydantic_lists_as_files(tags_list=existing_tags, topics_list=existing_topics,
                                                         recent_parsed_news=recent_parsed_news,
                                                         recent_input_news=recent_input_news)
        return file_storage

    async def creates_new_news(self, delta: timedelta) -> list[NewsResponseDetailed]:
        """
        Loads present data from DB, prepares gemini client with files and then prompt.
        Result should be newly created parsed news from Gemini model.
        """
        file_storage = await self.prepare_actual_data_for_ai(delta=delta)
        gemini_client = await self.prepare_gemini_client()
        gemini_files = self.upload_files_gemini(file_storage=file_storage)
        contents = [
            CREATION_PROMPT
        ]
        contents.extend(gemini_files.values())
        result = await gemini_client.chat.completions.create(response_model=Iterable[CreationResult],
                                                             messages=[{"role": "user", "content": contents}])
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
        file_storage = await self.prepare_actual_data_for_ai(delta=delta)
        gemini_client = await self.prepare_gemini_client()
        gemini_files = self.upload_files_gemini(file_storage=file_storage)
        contents = [
            CONNECTION_PROMPT
        ]
        contents.extend(gemini_files.values())
        result = await gemini_client.chat.completions.create(response_model=Iterable[ConnectionResult],
                                                             messages=[{"role": "user", "content": contents}])
        print(f"Result of the creation query is: {result=}")
        updated_news_list = []
        for news_data in result:
            saved_news = await self.parsed_news_service.update_news(news_data=news_data.parsed_news)
            if saved_news is None:
                continue
            for input_id in news_data.input_news_ids:
                await self.input_news_service.connect_input_with_parsed(input_id=input_id, parsed_id=saved_news.id)
            updated_news_list.append(updated_news_list)
        return updated_news_list
