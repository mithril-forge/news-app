"""accent function

Revision ID: f3296fb75839
Revises: 16e54104edeb
Create Date: 2025-11-09 17:10:19.033446

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f3296fb75839"
down_revision: str | None = "16e54104edeb"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS unaccent;")
