import logging
from typing import List

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from core.converters import orm_list_to_pydantic, orm_to_pydantic
from features.api_service.repository import AsyncTopicRepository
from features.api_service.services.schemas import TopicResponse, TopicCreate

logger = logging.getLogger(__name__)

class TopicService:
   def __init__(self, session: AsyncSession):
       self.session = session
       self.topic_repo = AsyncTopicRepository(session)
       logger.debug("TopicService initialized")

   async def get_all_topics(self) -> List[TopicResponse]:
       """Get all topics"""
       logger.info("Fetching all topics")
       topics = await self.topic_repo.get_all()
       logger.debug(f"Retrieved {len(topics)} topics")
       return orm_list_to_pydantic(topics, TopicResponse)

   async def get_topic_by_id(self, topic_id: int) -> TopicResponse:
       """Get a specific topic by ID"""
       logger.info(f"Fetching topic by ID: {topic_id}")
       topic = await self.topic_repo.get_by_id(topic_id)
       if not topic:
           logger.warning(f"Topic with ID {topic_id} not found")
           raise HTTPException(status_code=404, detail="Topic not found")
       return orm_to_pydantic(topic, TopicResponse)

   async def create_topic(self, topic_data: TopicCreate) -> TopicResponse:
       """Create a new topic"""
       logger.info(f"Creating new topic: {topic_data.name}")
       topic_dict = topic_data.dict()
       topic = await self.topic_repo.add(topic_dict)
       logger.info(f"Created topic with ID: {topic.id}")
       return orm_to_pydantic(topic, TopicResponse)