from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


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
    topic_id: Optional[int]  # topics are stable
    tags: List[str]  # new tags can be created
    content: str


class NewsUpdate(NewsCreate):
    id: int


class NewsResponseBasic(NewsBase):
    id: int
    # TODO: Fix the issue when new article isn't connected to topic
    topic: Optional[TopicResponse]
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    class Config:
        orm_mode = True


class InputNewsDetailed(BaseModel):
    publication_date: datetime
    title: str
    author: str
    source_site: str
    source_url: str


class NewsResponseDetailed(NewsResponseBasic):
    content: str
    input_news: list[InputNewsDetailed]
