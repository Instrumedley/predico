"""Add members_start_at_zero to leagues and baseline columns to league_members.

Revision ID: 0008_league_reset_points
Revises: 0007_knockout_games
Create Date: 2026-06-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0008_league_reset_points"
down_revision: Union[str, None] = "0007_knockout_games"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "leagues",
        sa.Column("members_start_at_zero", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index(
        op.f("ix_leagues_members_start_at_zero"),
        "leagues",
        ["members_start_at_zero"],
        unique=False,
    )
    op.alter_column("leagues", "members_start_at_zero", server_default=None)

    op.add_column(
        "league_members",
        sa.Column("points_at_join", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "league_members",
        sa.Column("perfect_predictions_at_join", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("league_members", "points_at_join", server_default=None)
    op.alter_column("league_members", "perfect_predictions_at_join", server_default=None)


def downgrade() -> None:
    op.drop_column("league_members", "perfect_predictions_at_join")
    op.drop_column("league_members", "points_at_join")
    op.drop_index(op.f("ix_leagues_members_start_at_zero"), table_name="leagues")
    op.drop_column("leagues", "members_start_at_zero")
