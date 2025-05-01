import io
import json
import logging
import zipfile
from datetime import datetime, timedelta
from typing import List, Optional

from features.input_news_processing.archive.abstract_archive import AbstractArchive
from features.input_news_processing.archive.local_archive import LocalArchive
from features.input_news_processing.database.repository import AsyncInputNewsRepository

from features.api_service.database.repository import AsyncParsedNewsRepository
from features.input_news_processing.converters import parsed_news_list_with_input, input_news_list_to_schema, \
    input_schema_list_to_orm, input_news_to_schema
from features.input_news_processing.services.schemas import ParsedNewsWithInputNews, InputNewsBase, \
    InputNewsWithID
from features.input_news_processing.testing_data.common import mock_data

logger = logging.getLogger(__name__)


class InputNewsService:
    def __init__(self, session, archive: AbstractArchive):
        self.session = session
        self.input_news_repo = AsyncInputNewsRepository(session=session)
        self.parsed_news_repo = AsyncParsedNewsRepository(session=session)
        self.archive = archive
        logger.debug("InputNewsService initialized")

    async def add_or_update_input_news_batch(self, input_news_list: List[InputNewsBase]) -> List[InputNewsWithID]:
        """
        Add a batch of input news items to the database.

        Args:
            input_news_list: List of InputNewsMetadata instances

        Returns:
            List of IDs of the added/updated news items
        """
        logger.info(f"Adding batch of {len(input_news_list)} input news items")
        orm_models = input_schema_list_to_orm(input_news_list)
        result_models = []
        for model in orm_models:
            existing = await self.input_news_repo.get_by_source_url(model.source_url)

            if existing:
                logger.debug(f"Updating existing input news with source_url: {model.source_url}")
                for key, value in model.dict(exclude={"id"}).items():
                    if value is not None:
                        setattr(existing, key, value)
                updated = await self.input_news_repo.update(existing)
                result_models.append(updated)
            else:
                # Add new model
                logger.debug(f"Adding new input news with title: {model.title}")
                new_model = await self.input_news_repo.add(model.dict(exclude={"id"}))
                result_models.append(new_model)

        logger.info(f"Successfully processed {len(result_models)} input news items")
        return input_news_list_to_schema(result_models)

    async def scrap_and_save_input_news(self, delta: timedelta) -> list[InputNewsWithID]:
        """ Query latest news from the corresponding websites by delta and update them in DB or create news ones"""
        input_news = await self.scrap_input_news(delta=delta)
        return await self.add_or_update_input_news_batch(input_news_list=input_news)

    async def clear_old_input_news(self, delta: timedelta) -> None:
        """
        Function that will archive older input news from DB that weren't used for any parsed news.
        The implementation would be probably by some JSON dump.
        """
        old_input_news = await self.input_news_repo.get_by_time_delta(delta=delta, newer=False, has_parsed_news=False)
        snapshot = self.input_news_repo.create_snapshot(old_input_news)
        json_str = json.dumps(snapshot, indent=2, default=str)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("input_news.json", json_str)
        zip_buffer.seek(0)
        zip_bytes = zip_buffer.getvalue()
        self.archive.save_file(file_content=zip_bytes, suffix=".zip")
        for input_news in old_input_news:
            await self.input_news_repo.remove(id=input_news.id)

    async def scrap_input_news(self, delta: timedelta) -> list[InputNewsBase]:
        """
        Function that will call external function to scrap input news from websites by delta and return them.
        Right now implemented with mock testing data.
        """
        return next(mock_data, [])

    async def get_input_news_by_delta(self, delta: timedelta, has_parsed_news: Optional[bool] = None) -> list[
        InputNewsWithID]:
        """
        Retrieves input news within a specified time period.
        Args:
            delta: Time period to look back from current time
            has_parsed_news: Filter by whether news has connected parsed news or not (None takes all)
        """
        result = await self.input_news_repo.get_by_time_delta(delta=delta, has_parsed_news=has_parsed_news)
        return input_news_list_to_schema(input_news_list=result)

    async def get_parsed_with_input_news(self, delta: timedelta) -> list[ParsedNewsWithInputNews]:
        """
        Retrieves parsed news with their associated input news within a specified time period.
        """
        result = await self.parsed_news_repo.get_by_time_delta(delta=delta)
        return parsed_news_list_with_input(parsed_news_list=result)

    async def connect_input_with_parsed(self, parsed_id: int, input_id: int) -> InputNewsWithID:
        """
        Links a parsed news entry with its original input news entry.
        """
        db_result = await self.input_news_repo.update_parsed_news_id(input_id=input_id, parsed_news_id=parsed_id)
        return input_news_to_schema(db_result)

    async def get_latest_timestamp(self) -> Optional[datetime]:
        """
        Returns latest timestamp of the input news
        """
        return await self.input_news_repo.get_latest_received_timestamp()