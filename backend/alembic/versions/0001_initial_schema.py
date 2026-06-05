"""Initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

roundtype = postgresql.ENUM(
    "group_stage",
    "round_of_32",
    "round_of_16",
    "quarter_finals",
    "semi_finals",
    "third_place",
    "final",
    name="roundtype",
    create_type=False,
)
gamestatus = postgresql.ENUM(
    "scheduled",
    "live",
    "finished",
    "cancelled",
    "postponed",
    name="gamestatus",
    create_type=False,
)


def upgrade() -> None:
    roundtype.create(op.get_bind(), checkfirst=True)
    gamestatus.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=True),
        sa.Column("email_verified", sa.Boolean(), nullable=False),
        sa.Column("email_verification_token", sa.String(), nullable=True),
        sa.Column("email_verification_expires", sa.DateTime(), nullable=True),
        sa.Column("password_reset_token", sa.String(), nullable=True),
        sa.Column("password_reset_expires", sa.DateTime(), nullable=True),
        sa.Column("cognito_user_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.create_index(op.f("ix_users_email_verified"), "users", ["email_verified"], unique=False)
    op.create_index(
        op.f("ix_users_email_verification_token"),
        "users",
        ["email_verification_token"],
        unique=True,
    )
    op.create_index(
        op.f("ix_users_password_reset_token"),
        "users",
        ["password_reset_token"],
        unique=True,
    )
    op.create_index(op.f("ix_users_cognito_user_id"), "users", ["cognito_user_id"], unique=True)

    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("country_code", sa.String(length=3), nullable=False),
        sa.Column("flag_emoji", sa.String(length=10), nullable=True),
        sa.Column("fifa_ranking", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_teams_id"), "teams", ["id"], unique=False)
    op.create_index(op.f("ix_teams_name"), "teams", ["name"], unique=True)
    op.create_index(op.f("ix_teams_country_code"), "teams", ["country_code"], unique=True)

    op.create_table(
        "stadiums",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_stadiums_id"), "stadiums", ["id"], unique=False)
    op.create_index(op.f("ix_stadiums_name"), "stadiums", ["name"], unique=False)

    op.create_table(
        "rounds",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("round_type", roundtype, nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_rounds_id"), "rounds", ["id"], unique=False)
    op.create_index(op.f("ix_rounds_name"), "rounds", ["name"], unique=True)
    op.create_index(op.f("ix_rounds_round_type"), "rounds", ["round_type"], unique=False)
    op.create_index(op.f("ix_rounds_order"), "rounds", ["order"], unique=False)

    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_groups_id"), "groups", ["id"], unique=False)
    op.create_index(op.f("ix_groups_name"), "groups", ["name"], unique=True)

    op.create_table(
        "group_teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_group_teams_id"), "group_teams", ["id"], unique=False)
    op.create_index(op.f("ix_group_teams_group_id"), "group_teams", ["group_id"], unique=False)
    op.create_index(op.f("ix_group_teams_team_id"), "group_teams", ["team_id"], unique=False)

    op.create_table(
        "games",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("home_team_id", sa.Integer(), nullable=False),
        sa.Column("away_team_id", sa.Integer(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("match_date", sa.Date(), nullable=True),
        sa.Column("match_time", sa.Time(), nullable=True),
        sa.Column("timezone", sa.String(length=50), nullable=True),
        sa.Column("status", gamestatus, nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("home_penalty_score", sa.Integer(), nullable=True),
        sa.Column("away_penalty_score", sa.Integer(), nullable=True),
        sa.Column("stadium_id", sa.Integer(), nullable=True),
        sa.Column("round_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.Column("is_knockout", sa.Boolean(), nullable=False),
        sa.Column("match_number", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["away_team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["home_team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["round_id"], ["rounds.id"]),
        sa.ForeignKeyConstraint(["stadium_id"], ["stadiums.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_games_id"), "games", ["id"], unique=False)
    op.create_index(op.f("ix_games_home_team_id"), "games", ["home_team_id"], unique=False)
    op.create_index(op.f("ix_games_away_team_id"), "games", ["away_team_id"], unique=False)
    op.create_index(op.f("ix_games_scheduled_at"), "games", ["scheduled_at"], unique=False)
    op.create_index(op.f("ix_games_match_date"), "games", ["match_date"], unique=False)
    op.create_index(op.f("ix_games_status"), "games", ["status"], unique=False)
    op.create_index(op.f("ix_games_stadium_id"), "games", ["stadium_id"], unique=False)
    op.create_index(op.f("ix_games_round_id"), "games", ["round_id"], unique=False)
    op.create_index(op.f("ix_games_group_id"), "games", ["group_id"], unique=False)
    op.create_index(op.f("ix_games_is_knockout"), "games", ["is_knockout"], unique=False)

    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("predicted_home_score", sa.Integer(), nullable=False),
        sa.Column("predicted_away_score", sa.Integer(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("exact_score_points", sa.Integer(), nullable=True),
        sa.Column("correct_result_points", sa.Integer(), nullable=True),
        sa.Column("correct_goal_difference_points", sa.Integer(), nullable=True),
        sa.Column("is_calculated", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_predictions_id"), "predictions", ["id"], unique=False)
    op.create_index(op.f("ix_predictions_user_id"), "predictions", ["user_id"], unique=False)
    op.create_index(op.f("ix_predictions_game_id"), "predictions", ["game_id"], unique=False)
    op.create_index(op.f("ix_predictions_points"), "predictions", ["points"], unique=False)
    op.create_index(op.f("ix_predictions_is_calculated"), "predictions", ["is_calculated"], unique=False)
    op.create_index("idx_user_game_unique", "predictions", ["user_id", "game_id"], unique=True)

    op.create_table(
        "leagues",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("is_private", sa.Boolean(), nullable=False),
        sa.Column("invite_code", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_leagues_id"), "leagues", ["id"], unique=False)
    op.create_index(op.f("ix_leagues_name"), "leagues", ["name"], unique=False)
    op.create_index(op.f("ix_leagues_created_by"), "leagues", ["created_by"], unique=False)
    op.create_index(op.f("ix_leagues_is_private"), "leagues", ["is_private"], unique=False)
    op.create_index(op.f("ix_leagues_invite_code"), "leagues", ["invite_code"], unique=True)

    op.create_table(
        "league_members",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("league_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("total_points", sa.Integer(), nullable=False),
        sa.Column("joined_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["league_id"], ["leagues.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_league_members_id"), "league_members", ["id"], unique=False)
    op.create_index(op.f("ix_league_members_league_id"), "league_members", ["league_id"], unique=False)
    op.create_index(op.f("ix_league_members_user_id"), "league_members", ["user_id"], unique=False)
    op.create_index(op.f("ix_league_members_total_points"), "league_members", ["total_points"], unique=False)
    op.create_index("idx_league_user_unique", "league_members", ["league_id", "user_id"], unique=True)

    op.create_table(
        "league_invitations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("league_id", sa.Integer(), nullable=False),
        sa.Column("inviter_id", sa.Integer(), nullable=False),
        sa.Column("invitee_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("responded_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["invitee_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["inviter_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["league_id"], ["leagues.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_league_invitations_id"), "league_invitations", ["id"], unique=False)
    op.create_index(op.f("ix_league_invitations_league_id"), "league_invitations", ["league_id"], unique=False)
    op.create_index(op.f("ix_league_invitations_inviter_id"), "league_invitations", ["inviter_id"], unique=False)
    op.create_index(op.f("ix_league_invitations_invitee_id"), "league_invitations", ["invitee_id"], unique=False)
    op.create_index(op.f("ix_league_invitations_status"), "league_invitations", ["status"], unique=False)


def downgrade() -> None:
    op.drop_table("league_invitations")
    op.drop_table("league_members")
    op.drop_table("leagues")
    op.drop_table("predictions")
    op.drop_table("games")
    op.drop_table("group_teams")
    op.drop_table("groups")
    op.drop_table("rounds")
    op.drop_table("stadiums")
    op.drop_table("teams")
    op.drop_table("users")

    gamestatus.drop(op.get_bind(), checkfirst=True)
    roundtype.drop(op.get_bind(), checkfirst=True)
