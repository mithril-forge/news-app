from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class TopicCreate(BaseModel):
    name: str
    description: Optional[str] = None


class TopicResponse(BaseModel):
    name: str
    id: int

    class Config:
        orm_mode = True


class TagResponse(BaseModel):
    id: int
    text: str

    class Config:
        orm_mode = True


class ParsedNewsSummary(BaseModel):
    id: int
    title: str
    description: str
    image_url: str


class ParsedNewsCreate(BaseModel):
    title: str
    description: str
    image_url: str
    topic_id: Optional[int]
    tags: List[str]
    content: str


class ParsedNewsUpdate(BaseModel):
    title: str
    description: str
    image_url: str
    topic_id: Optional[int]
    tags: List[str]
    content: str
    id: int


class ParsedNewsBasic(BaseModel):
    title: str
    description: str
    image_url: str
    id: int
    # TODO: Fix the issue when new article isn't connected to topic
    topic: Optional[TopicResponse]
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    class Config:
        orm_mode = True


class InputNewsWithoutContent(BaseModel):
    publication_date: datetime
    title: str
    author: str
    source_site: str
    source_url: str


class ParsedNewsResponseDetailed(BaseModel):
    title: str
    description: str
    image_url: str
    id: int
    topic: Optional[TopicResponse]
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []
    content: str
    input_news: list[InputNewsWithoutContent]
