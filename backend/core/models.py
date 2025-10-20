# TODO: Implement cascade on_delete also in DB itself not only in SQLModel logic
import uuid
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
    news_picks: Mapped[list["NewsPickItem"]] = Relationship(back_populates="parsed_news")


class ParsedNewsRelevancy(SQLModel, table=True):
    __tablename__ = "news_relevance"

    # Core fields from your original model
    id: int = Field(primary_key=True)
    title: str
    description: str
    topic_name: str | None
    topic_id: int | None
    tags: str
    updated_at: datetime
    view_count: int
    importancy: int
    relevance_score: float
    normalized_views: float
    time_decay_factor: float
    score_calculated_at: datetime


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


class Account(BaseModelWithID, table=True):
    __tablename__ = "accounts"
    email: str = Field(unique=True)
    prompt: str | None = Field(default=None)
    news_picks: Mapped[list["NewsPick"]] = Relationship(
        back_populates="account", sa_relationship_kwargs={"lazy": "selectin"}
    )
    account_deletion_tokens: Mapped[list["AccountDeletionToken"]] = Relationship(back_populates="account")


class AccountDeletionToken(BaseModelWithID, table=True):
    __tablename__ = "account_deletion_tokens"

    account_id: int = Field(foreign_key="accounts.id", index=True)
    token_hash: str = Field(max_length=64, unique=True, index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    expires_at: datetime = Field(nullable=False, index=True)
    used_at: datetime | None = Field(default=None, nullable=True)
    ip_address: str | None = Field(default=None, max_length=45)
    user_agent: str | None = Field(default=None, max_length=500)

    account: Mapped["Account"] = Relationship(
        sa_relationship_kwargs={
            "lazy": "selectin",
        }
    )


class NewsPick(BaseModelWithID, table=True):
    __tablename__ = "news_picks"
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    account_id: int | None = Field(default=None, foreign_key="accounts.id")
    account: Mapped["Account"] = Relationship(back_populates="news_picks")
    items: Mapped[list["NewsPickItem"]] = Relationship(
        back_populates="pick", sa_relationship_kwargs={"lazy": "selectin"}
    )
    description: str = Field()
    hash: str = Field(default_factory=lambda: uuid.uuid4().hex, unique=True)


class NewsPickItem(BaseModel, table=True):
    __tablename__ = "news_pick_items"
    pick_id: int = Field(foreign_key="news_picks.id", primary_key=True)
    pick: Mapped["NewsPick"] = Relationship(back_populates="items")
    parsed_news_id: int = Field(foreign_key="parsed_news.id", primary_key=True)
    parsed_news: Mapped["ParsedNews"] = Relationship(back_populates="news_picks")
