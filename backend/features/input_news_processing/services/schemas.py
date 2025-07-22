from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Topic(BaseModel):
    name: str
    id: int

    class Config:
        orm_mode = True


class Tag(BaseModel):
    id: int
    text: str

    class Config:
        orm_mode = True


class InputNewsWithoutContent(BaseModel):
    id: int
    tags: list[str]
    category: str
    publication_date: datetime
    author: str
    source_site: str
    source_url: str
    title: str
    summary: str


class InputNews(BaseModel):
    tags: list[str]
    category: str
    publication_date: datetime
    author: str
    source_site: str
    source_url: str
    title: str
    summary: str
    content: str


class InputNewsWithID(BaseModel):
    tags: list[str]
    category: str
    publication_date: datetime
    author: str
    source_site: str
    source_url: str
    title: str
    summary: str
    content: str
    id: int


class ParsedNewsWithInputNews(BaseModel):
    title: str
    description: str
    image_url: str
    id: int
    topic: Topic | None
    created_at: datetime
    updated_at: datetime
    tags: list[Tag] = []
    content: str
    input_news: list[InputNewsWithID]


class InitConnectionResult(BaseModel):
    parsed_news_id: int
    input_news_ids: list[int]


class InitGenerationResult(BaseModel):
    input_news_ids: list[int]
    # TODO: Try to limit the number from 0 to 10
    importancy: int


class ImageDetail(BaseModel):
    link: str
    source_text: str
    license: str
