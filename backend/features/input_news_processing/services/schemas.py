from datetime import datetime
from typing import Optional, Any

from pydantic import BaseModel, field_validator, model_validator

from features.api_service.services.schemas import NewsResponseDetailed, NewsCreate, NewsUpdate


class InputNewsBase(BaseModel):
    tags: list[str]
    category: str
    publication_date: datetime
    author: str
    source_site: str
    source_url: str
    content: str
    title: str
    summary: str

class InputNewsWithID(InputNewsBase):
    id: int

class ParsedNewsWithInputNews(NewsResponseDetailed):
    input_news: list[InputNewsWithID]


# TODO: Check encoding of the answers, sometimes they are in unicode, we need to tackle it in that case
class ConnectionResult(BaseModel):
    input_news_ids: list[int]
    parsed_news: NewsUpdate

class CreationResult(BaseModel):
    input_news_ids: list[int]
    parsed_news: NewsCreate
    """
    # TODO: Do it automatically so when adding new params, it won't break
    @model_validator(mode='after')
    def decode_unicode_fields(self) -> 'ConnectionResult':
        Process all fields after the model is created
        self.parsed_news.content = self.parsed_news.content.encode().decode("unicode_escape")
        self.parsed_news.title = self.parsed_news.title.encode().decode("unicode_escape")
        self.parsed_news.description = self.parsed_news.description.encode().decode("unicode_escape")
        self.parsed_news.tags = [tag.encode().decode("unicode_escape") for tag in self.parsed_news.tags]
    """

class ImageDetail(BaseModel):
    link: str
    source_text: str
    license: str
