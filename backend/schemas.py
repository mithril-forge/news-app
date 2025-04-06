from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Topic schemas
class TopicBase(BaseModel):
    name: str
    description: Optional[str] = None


class TopicCreate(TopicBase):
    pass


class TopicResponse(TopicBase):
    id: int

    class Config:
        orm_mode = True


# Tag schemas
class TagBase(BaseModel):
    text: str


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: int

    class Config:
        orm_mode = True


# News schemas
class NewsBase(BaseModel):
    title: str
    description: str
    content: str
    image_url: Optional[str] = None


class NewsCreate(NewsBase):
    topic_id: Optional[int] = None
    tags: Optional[List[str]] = []


class NewsResponse(NewsBase):
    id: int
    topic_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    class Config:
        orm_mode = True


class NewsWithTopicResponse(NewsResponse):
    topic: Optional[TopicResponse] = None

    class Config:
        orm_mode = True


# Input News schemas
class InputNewsBase(BaseModel):
    source: str
    description: str
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class InputNewsCreate(InputNewsBase):
    pass


class InputNewsResponse(InputNewsBase):
    id: int
    received_at: datetime
    processed_at: Optional[datetime] = None
    parsed_news: Optional[int] = None

    class Config:
        orm_mode = True