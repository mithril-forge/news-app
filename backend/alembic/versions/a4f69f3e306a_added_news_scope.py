"""added news scope

Revision ID: a4f69f3e306a
Revises: c98f0fb7c230
Create Date: 2025-08-30 23:03:13.805138

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a4f69f3e306a'
down_revision: Union[str, None] = 'c98f0fb7c230'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create the enum type first
    news_scope_enum = sa.Enum('FOREIGN', 'DOMESTIC', name='newsscope')
    news_scope_enum.create(op.get_bind())

    # Then add the column using the enum
    op.add_column('parsed_news', sa.Column('news_scope', news_scope_enum, nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the column first
    op.drop_column('parsed_news', 'news_scope')

    # Then drop the enum type
    news_scope_enum = sa.Enum('FOREIGN', 'DOMESTIC', name='newsscope')
    news_scope_enum.drop(op.get_bind())