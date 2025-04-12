from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TopicBase(BaseModel):
    name: str


class TopicCreate(TopicBase):
    description: Optional[str] = None


class TopicResponse(TopicBase):
    id: int

    class Config:
        orm_mode = True


class TagBase(BaseModel):
    text: str


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int

    class Config:
        orm_mode = True


class NewsBase(BaseModel):
    title: str
    description: str
    image_url: str


class NewsCreate(NewsBase):
    topic_id: int # topics are stabls
    tags: List[str] # new tags can be created
    content: str


class NewsResponseBasic(NewsBase):
    id: int
    topic: TopicResponse
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    class Config:
        orm_mode = True


class NewsResponseDetailed(NewsResponseBasic):
    content: str
