from datetime import datetime

from pydantic import BaseModel


class TopicCreate(BaseModel):
    name: str
    description: str | None = None


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


class ParsedInputNewsTitles(BaseModel):
    id: int
    title: str
    input_news_titles: list[str]


class ParsedNewsCreate(BaseModel):
    title: str
    description: str
    image_url: str
    topic_id: int | None
    tags: list[str]
    content: str


class ParsedNewsUpdate(BaseModel):
    title: str
    description: str
    image_url: str
    topic_id: int | None
    tags: list[str]
    content: str
    id: int


class ParsedNewsBasic(BaseModel):
    title: str
    description: str
    image_url: str
    id: int
    # TODO: Fix the issue when new article isn't connected to topic
    topic: TopicResponse | None
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = []

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
    topic: TopicResponse | None
    created_at: datetime
    updated_at: datetime
    tags: list[TagResponse] = []
    content: str
    input_news: list[InputNewsWithoutContent]


class AccountDetails(BaseModel):
    id: int
    email: str
    prompt: str
