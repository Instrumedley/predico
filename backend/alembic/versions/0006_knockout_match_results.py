"""Add knockout_match_results table."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0006_knockout_results"
down_revision: Union[str, None] = "0005_user_last_login"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knockout_match_results",
        sa.Column("match_number", sa.Integer(), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("winner_team_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["winner_team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("match_number"),
    )
    op.create_index(
        op.f("ix_knockout_match_results_winner_team_id"),
        "knockout_match_results",
        ["winner_team_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_knockout_match_results_winner_team_id"), table_name="knockout_match_results")
    op.drop_table("knockout_match_results")
