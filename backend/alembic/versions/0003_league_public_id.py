"""Add public_id UUID to leagues for opaque URLs.

Revision ID: 0003_league_public_id
Revises: 0002_league_invite_email_token
Create Date: 2026-05-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0003_league_public_id"
down_revision: Union[str, None] = "0002_league_invite_email_token"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("leagues", sa.Column("public_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("UPDATE leagues SET public_id = gen_random_uuid() WHERE public_id IS NULL")
    op.alter_column("leagues", "public_id", nullable=False)
    op.create_index(op.f("ix_leagues_public_id"), "leagues", ["public_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_leagues_public_id"), table_name="leagues")
    op.drop_column("leagues", "public_id")
