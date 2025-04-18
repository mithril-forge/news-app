import logging
from typing import List
from datetime import datetime

from database.repository import AsyncInputNewsRepository
from fastapi import HTTPException
from topic_generation.input_news_schema import InputNewsSchema
from services.converters import input_metadata_list_to_orm
from sqlmodel.ext.asyncio.session import AsyncSession

# Configure module logger
logger = logging.getLogger(__name__)


class InputNewsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.input_news_repo = AsyncInputNewsRepository(session)
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
        orm_models = input_metadata_list_to_orm(input_news_list)
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

