# TODO: Implement cascade on_delete also in DB itself not only in SQLModel logic
from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, Column, Integer
from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, Relationship, SQLModel


class BaseModel(SQLModel):
    """Base model with common utility methods."""

    @classmethod
    def schema_name(cls) -> str:
        """Return the table name for the model."""
        return cls.__tablename__  # type: ignore[return-value]


class BaseModelWithID(BaseModel):
    id: int | None = Field(default=None, primary_key=True)


class Topic(BaseModelWithID, table=True):
    __tablename__ = "topics"
    name: str = Field(index=True)
    description: str | None = Field(default=None)

    news_items: Mapped[list["ParsedNews"]] = Relationship(
        sa_relationship=relationship(back_populates="topic", lazy="selectin")
    )


class ParsedNewsTagLink(BaseModel, table=True):
    __tablename__ = "parsed_news_tag_link"

    news_item_id: int | None = Field(default=None, foreign_key="parsed_news.id", primary_key=True)
    tag_id: int | None = Field(default=None, foreign_key="tags.id", primary_key=True)


class Tag(BaseModelWithID, table=True):
    __tablename__ = "tags"

    text: str = Field()

    news_items: Mapped[list["ParsedNews"]] = Relationship(
        link_model=ParsedNewsTagLink,
        back_populates="tags",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete",
            "passive_deletes": True,
        },
    )


class ParsedNews(BaseModelWithID, table=True):
    __tablename__ = "parsed_news"
    title: str = Field()
    description: str = Field()
    content: str = Field()
    image_url: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    view_count: int = Field(default=0, sa_column_kwargs={"server_default": "0"})
    importancy: int = Field(
        default=5, sa_column=Column(Integer, CheckConstraint("importancy <= 10"), server_default="5", nullable=False)
    )
    tags: Mapped[list["Tag"]] = Relationship(
        back_populates="news_items",
        link_model=ParsedNewsTagLink,
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete",
            "passive_deletes": True,
        },
    )

    topic_id: int | None = Field(default=None, foreign_key="topics.id")
    topic: Mapped[Optional["Topic"]] = Relationship(
        sa_relationship=relationship(back_populates="news_items", lazy="selectin")
    )

    input_news: Mapped[list["InputNews"]] = Relationship(
        back_populates="parsed_news_relation",
        sa_relationship_kwargs={"lazy": "selectin"},
    )


class InputNews(BaseModelWithID, table=True):
    __tablename__ = "input_news"

    tags: str | None = Field(default=None)  # This is a string field, not a relationship
    category: str = Field()
    source_url: str = Field()
    source_site: str = Field()
    summary: str = Field()
    author: str = Field()
    content: str = Field()
    title: str = Field()

    parsed_news: int | None = Field(default=None, foreign_key="parsed_news.id", nullable=True)

    parsed_news_relation: Mapped[Optional["ParsedNews"]] = Relationship(
        back_populates="input_news", sa_relationship_kwargs={"lazy": "selectin"}
    )

    received_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    publication_date: datetime | None = Field(default=None)
