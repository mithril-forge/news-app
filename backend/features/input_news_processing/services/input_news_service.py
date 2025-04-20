import logging
from datetime import datetime, timedelta
from typing import List, Optional

from features.input_news_processing.database.repository import AsyncInputNewsRepository

from features.api_service.database.repository import AsyncParsedNewsRepository
from features.input_news_processing.converters import parsed_news_list_with_input, input_news_list_to_schema, \
    input_schema_list_to_orm
from features.input_news_processing.services.schemas import ParsedNewsWithInputNews, InputNewsSchema
from features.input_news_processing.testing_data.common import mock_data

logger = logging.getLogger(__name__)


class InputNewsService:
    def __init__(self, session):
        self.session = session

        self.input_news_repo = AsyncInputNewsRepository(session=session)
        self.parsed_news_repo = AsyncParsedNewsRepository(session=session)
        logger.debug("InputNewsService initialized")

    async def add_input_news_batch(self, input_news_list: List[InputNewsSchema]) -> List[int]:
        """
        Add a batch of input news items to the database.

        Args:
            input_news_list: List of InputNewsMetadata instances

        Returns:
            List of IDs of the added/updated news items
        """
        logger.info(f"Adding batch of {len(input_news_list)} input news items")
        orm_models = input_schema_list_to_orm(input_news_list)
        result_ids = []
        for model in orm_models:
            try:
                existing = await self.input_news_repo.get_by_source_url(model.source_url)

                if existing:
                    logger.debug(f"Updating existing input news with source_url: {model.source_url}")
                    for key, value in model.dict(exclude={"id"}).items():
                        if value is not None:
                            setattr(existing, key, value)
                    updated = await self.input_news_repo.update(existing)
                    result_ids.append(updated.id)
                else:
                    # Add new model
                    logger.debug(f"Adding new input news with title: {model.title}")
                    new_model = await self.input_news_repo.add(model.dict(exclude={"id"}))
                    result_ids.append(new_model.id)
            except Exception as e:
                logger.error(f"Error adding input news {model.title}: {str(e)}")
                # Continue with the next item rather than failing the whole batch
                continue

        logger.info(f"Successfully processed {len(result_ids)} out of {len(input_news_list)} input news items")
        return result_ids

    async def parse_input_news(self, from_date: datetime, to_date: datetime) -> None:
        # Logic to fetch and store input news
        input_news = await self._fetch_raw_news(from_date, to_date)
        await self.add_input_news_batch(input_news_list=input_news)

    async def clear_old_input_news(self, older_than: datetime) -> None:
        # Logic to archive old input news
        pass

    async def _fetch_raw_news(self, from_date: datetime, to_date: datetime) -> list[InputNewsSchema]:
        # Implementation to get news data, currently mocked
        # In a real implementation, this might call an external API or data source
        return next(mock_data, [])

    async def get_input_news_from_time(self, delta: timedelta, has_parsed_news: Optional[bool] = None) -> list[InputNewsSchema]:
        result = await self.input_news_repo.get_by_time_delta(delta=delta, has_parsed_news=has_parsed_news)
        return input_news_list_to_schema(input_news_list=result)

    async def get_parsed_with_input_news(self, delta: timedelta) -> list[ParsedNewsWithInputNews]:
        result = await self.parsed_news_repo.get_by_time_delta(delta=delta)
        return parsed_news_list_with_input(parsed_news_list=result)