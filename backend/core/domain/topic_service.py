from typing import List

import structlog
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from core.converters import orm_list_to_pydantic, orm_to_pydantic
from core.repository import AsyncTopicRepository
from core.domain.schemas import TopicResponse, TopicCreate

logger = structlog.get_logger()


class TopicService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.topic_repo = AsyncTopicRepository(session)
        logger.info("TopicService initialized")

    async def get_all_topics(self) -> List[TopicResponse]:
        """Get all topics"""
        logger.info("Fetching all topics")
        topics = await self.topic_repo.get_all()
        logger.debug(f"Retrieved topics: {[topic.name for topic in topics]}")
        result = orm_list_to_pydantic(topics, TopicResponse)
        logger.info(f"Successfully converted {len(result)} topics to response format")
        return result

    async def get_topic_by_id(self, topic_id: int) -> TopicResponse:
        """Get a specific topic by ID"""
        logger.info(f"Fetching topic by ID: {topic_id}")
        topic = await self.topic_repo.get_by_id(topic_id)
        if not topic:
            logger.warning(f"Topic with ID {topic_id} not found")
            raise HTTPException(status_code=404, detail="Topic not found")
        result = orm_to_pydantic(topic, TopicResponse)
        logger.info(f"Successfully retrieved topic by ID: {topic_id}")
        return result

    async def create_topic(self, topic_data: TopicCreate) -> TopicResponse:
        """Create a new topic"""
        logger.info(f"Creating new topic: {topic_data.name}")
        topic_dict = topic_data.dict()
        topic = await self.topic_repo.add(topic_dict)
        logger.info(f"Created topic with ID: {topic.id}")
        result = orm_to_pydantic(topic, TopicResponse)
        return result
