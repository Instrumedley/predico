"""Add email and token fields to league invitations.

Revision ID: 0002_league_invite_email_token
Revises: 0001_initial_schema
Create Date: 2026-05-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_league_invite_email_token"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("league_invitations", sa.Column("invitee_email", sa.String(), nullable=True))
    op.add_column("league_invitations", sa.Column("token", sa.String(), nullable=True))
    op.alter_column("league_invitations", "invitee_id", existing_type=sa.Integer(), nullable=True)
    op.create_index(op.f("ix_league_invitations_invitee_email"), "league_invitations", ["invitee_email"], unique=False)
    op.create_index(op.f("ix_league_invitations_token"), "league_invitations", ["token"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_league_invitations_token"), table_name="league_invitations")
    op.drop_index(op.f("ix_league_invitations_invitee_email"), table_name="league_invitations")
    op.alter_column("league_invitations", "invitee_id", existing_type=sa.Integer(), nullable=False)
    op.drop_column("league_invitations", "token")
    op.drop_column("league_invitations", "invitee_email")
