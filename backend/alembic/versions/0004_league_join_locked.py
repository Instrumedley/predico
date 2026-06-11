"""Add is_join_locked to leagues.

Revision ID: 0004_league_join_locked
Revises: 0003_league_public_id
Create Date: 2026-05-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_league_join_locked"
down_revision: Union[str, None] = "0003_league_public_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "leagues",
        sa.Column("is_join_locked", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index(op.f("ix_leagues_is_join_locked"), "leagues", ["is_join_locked"], unique=False)
    op.alter_column("leagues", "is_join_locked", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_leagues_is_join_locked"), table_name="leagues")
    op.drop_column("leagues", "is_join_locked")
