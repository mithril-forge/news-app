from sqlalchemy.dialects.postgresql import JSONB  # Import JSONB for PostgreSQL
from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, Relationship, SQLModel, Column  # Import Column

class BaseModel(SQLModel):
    """Base model with common utility methods."""

    @classmethod
    def schema_name(cls) -> str:
        """Return the table name for the model."""
        return cls.__tablename__
