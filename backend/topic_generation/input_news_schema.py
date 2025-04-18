from datetime import datetime

from pydantic import BaseModel

class InputNewsMetadata(BaseModel):
    tags: list[str]
    category: str
    publication_date: datetime
    author: str
    source_site: str
    source_url: str
    content: str
    title: str
    summary: str