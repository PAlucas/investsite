"""add_historical close and open

Revision ID: d845204190d5
Revises: cd855594244d
Create Date: 2025-05-08 20:49:20.655041

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd845204190d5'
down_revision: Union[str, None] = 'cd855594244d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('historical_stock_data', sa.Column('open_price', sa.String(length=20), nullable=False))
    op.add_column('historical_stock_data', sa.Column('close_price', sa.String(length=20), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('historical_stock_data', 'close_price')
    op.drop_column('historical_stock_data', 'open_price')
    # ### end Alembic commands ###
