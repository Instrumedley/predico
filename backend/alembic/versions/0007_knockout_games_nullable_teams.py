"""Allow nullable team FKs on games and unique match_number for knockout rows."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0007_knockout_games"
down_revision: Union[str, None] = "0006_knockout_results"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("games", "home_team_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("games", "away_team_id", existing_type=sa.Integer(), nullable=True)
    op.create_index(
        "ix_games_match_number_unique",
        "games",
        ["match_number"],
        unique=True,
        postgresql_where=sa.text("match_number IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_games_match_number_unique", table_name="games")
    op.alter_column("games", "away_team_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("games", "home_team_id", existing_type=sa.Integer(), nullable=False)
