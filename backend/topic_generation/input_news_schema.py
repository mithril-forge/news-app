from datetime import datetime

from pydantic import BaseModel

class InputNewsMetadata(BaseModel):
    tags: list[str]
    category: str
    post_date: datetime
    source_site: str
    source_url: str
    content: str # maybe separated
    title: str # maybe separated