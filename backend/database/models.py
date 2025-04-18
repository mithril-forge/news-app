from datetime import datetime
from typing import List, Optional, Dict, Any  # Import Dict and Any for raw_data

from sqlalchemy.dialects.postgresql import JSONB  # Import JSONB for PostgreSQL
from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, Relationship, SQLModel, Column  # Import Column


class Topic(SQLModel, table=True):
    __tablename__ = "topics"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)

    news_items: Mapped[list["ParsedNews"]] = Relationship(sa_relationship=relationship(back_populates="topic", lazy='selectin'))




class ParsedNewsTagLink(SQLModel, table=True):
    __tablename__ = "parsed_news_tag_link"

    news_item_id: Optional[int] = Field(
        default=None, foreign_key="parsed_news.id", primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tags.id", primary_key=True
    )


class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    text: str = Field()

    news_items: Mapped[List["ParsedNews"]] = Relationship(link_model=ParsedNewsTagLink, back_populates="tags",sa_relationship_kwargs={'lazy': 'selectin'} )



class ParsedNews(SQLModel, table=True):
    __tablename__ = "parsed_news"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field()
    description: str = Field()
    content: str = Field()
    image_url: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    tags: Mapped[List[Tag]] = Relationship(back_populates="news_items", link_model=ParsedNewsTagLink, sa_relationship_kwargs={'lazy': 'selectin'})

    topic_id: Optional[int] = Field(default=None, foreign_key="topics.id")

    topic: Mapped[Optional[Topic]] = Relationship(sa_relationship=relationship(back_populates="news_items", lazy='selectin'), )




class InputNews(SQLModel, table=True):
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