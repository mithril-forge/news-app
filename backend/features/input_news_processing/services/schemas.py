from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from features.api_service.services.schemas import NewsResponseDetailed, NewsCreate

# TODO: Split usages with ID and without
class InputNewsSchema(BaseModel):
    id: Optional[int] = None
    tags: list[str]
    category: str
    publication_date: datetime
    author: str
    source_site: str
    source_url: str
    content: str
    title: str
    summary: str



class ParsedNewsWithInputNews(NewsResponseDetailed):
    input_news: list[InputNewsSchema]


class ConnectionResult(BaseModel):
    input_news_ids: list[int]
    parsed_news: NewsCreate
