# TODO: Implement cascade on_delete also in DB itself not only in SQLModel logic
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, Relationship, SQLModel


class BaseModel(SQLModel):
    """Base model with common utility methods."""

    @classmethod
    def schema_name(cls) -> str:
        """Return the table name for the model."""
        return cls.__tablename__


class Topic(BaseModel, table=True):
    __tablename__ = "topics"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)

    news_items: Mapped[list["ParsedNews"]] = Relationship(
        sa_relationship=relationship(back_populates="topic", lazy="selectin")
    )


class ParsedNewsTagLink(BaseModel, table=True):
    __tablename__ = "parsed_news_tag_link"

    news_item_id: Optional[int] = Field(
        default=None, foreign_key="parsed_news.id", primary_key=True
    )
    tag_id: Optional[int] = Field(default=None, foreign_key="tags.id", primary_key=True)


class Tag(BaseModel, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)
    text: str = Field()

    news_items: Mapped[List["ParsedNews"]] = Relationship(
        link_model=ParsedNewsTagLink,
        back_populates="tags",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete",
            "passive_deletes": True,
        },
    )


class ParsedNews(BaseModel, table=True):
    __tablename__ = "parsed_news"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field()
    description: str = Field()
    content: str = Field()
    image_url: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    view_count: int = Field(default=0, sa_column_kwargs={"server_default": "0"})

    tags: Mapped[List["Tag"]] = Relationship(
        back_populates="news_items",
        link_model=ParsedNewsTagLink,
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete",
            "passive_deletes": True,
        },
    )

    topic_id: Optional[int] = Field(default=None, foreign_key="topics.id")
    topic: Mapped[Optional["Topic"]] = Relationship(
        sa_relationship=relationship(back_populates="news_items", lazy="selectin")
    )

    input_news: Mapped[List["InputNews"]] = Relationship(
        back_populates="parsed_news_relation",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class InputNews(BaseModel, table=True):
    __tablename__ = "input_news"

    id: Optional[int] = Field(default=None, primary_key=True)
    tags: Optional[str] = Field(
        default=None
    )  # This is a string field, not a relationship
    category: str = Field()
    source_url: str = Field()
    source_site: str = Field()
    summary: str = Field()
    author: str = Field()
    content: str = Field()
    title: str = Field()

    parsed_news: Optional[int] = Field(
        default=None, foreign_key="parsed_news.id", nullable=True
    )

    parsed_news_relation: Mapped[Optional["ParsedNews"]] = Relationship(
        back_populates="input_news", sa_relationship_kwargs={"lazy": "selectin"}
    )

    received_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    publication_date: Optional[datetime] = Field(default=None)
