from typing import List, Optional
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from database.repository import AsyncTopicRepository
from database.models import Topic
from schemas import TopicResponse, TopicCreate
from services.converters import orm_to_pydantic, orm_list_to_pydantic


class TopicService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.topic_repo = AsyncTopicRepository(session)

    async def get_all_topics(self) -> List[TopicResponse]:
        """Get all topics"""
        topics = await self.topic_repo.get_all()
        return orm_list_to_pydantic(topics, TopicResponse)

    async def get_topic_by_id(self, topic_id: int) -> TopicResponse:
        """Get a specific topic by ID"""
        topic = await self.topic_repo.get_by_id(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")
        return orm_to_pydantic(topic, TopicResponse)

    async def create_topic(self, topic_data: TopicCreate) -> TopicResponse:
        """Create a new topic"""
        # Convert Pydantic model to dict
        topic_dict = topic_data.dict()
        # Create topic using repository
        topic = await self.topic_repo.add(topic_dict)
        return orm_to_pydantic(topic, TopicResponse)