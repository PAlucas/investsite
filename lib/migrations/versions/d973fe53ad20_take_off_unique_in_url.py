"""take off unique in url

Revision ID: d973fe53ad20
Revises: 155d468173ca
Create Date: 2025-05-03 18:16:46.443250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd973fe53ad20'
down_revision: Union[str, None] = '155d468173ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use the correct PostgreSQL syntax to drop a constraint
    op.execute('ALTER TABLE infomoney_news DROP CONSTRAINT IF EXISTS infomoney_news_url_key')


def downgrade() -> None:
    # Add the unique constraint back if needed
    op.execute('ALTER TABLE infomoney_news ADD CONSTRAINT infomoney_news_url_key UNIQUE (url)')
