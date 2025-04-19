from datetime import datetime
from typing import List, Optional, Dict, Any  # Import Dict and Any for raw_data

from sqlalchemy.dialects.postgresql import JSONB  # Import JSONB for PostgreSQL
from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, Relationship, SQLModel, Column  # Import Column

from core.models import BaseModel


class InputNews(BaseModel, table=True):
    __tablename__ = "input_news"

    id: Optional[int] = Field(default=None, primary_key=True)
    tags: Optional[str] = Field(default=None)
    category: str = Field()
    source_url: str = Field()
    source_site: str = Field()
    summary: str = Field()
    author: str = Field()
    content: str = Field()
    title: str = Field()
    parsed_news: Optional[int] = Field(foreign_key="parsed_news.id",
                                        nullable=True)  # Fixed foreign key reference
    received_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    publication_date: Optional[datetime] = Field(default=None)  # Made optional with default=None