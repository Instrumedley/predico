"""Add last_login to users.

Revision ID: 0005_user_last_login
Revises: 0004_league_join_locked
Create Date: 2026-06-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_user_last_login"
down_revision: Union[str, None] = "0004_league_join_locked"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("last_login", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "last_login")
