"""
Alembic environment configuration for database migrations.
"""
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection

from alembic import context

# Import your Base and models
from app.db.database import Base
# Import all models so Alembic can detect them
from app.db.models import (
    User,
    Team,
    Stadium,
    Round,
    Group,
    GroupTeam,
    Game,
    Prediction,
    League,
    LeagueMember,
    LeagueInvitation,
)

# this is the Alembic Config object
config = context.config

# Set the database URL from settings or environment
# Alembic needs a synchronous database URL (use psycopg2 instead of asyncpg)
try:
    from app.core.config import settings
    db_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
except Exception:
    # Fallback: try to get from environment or use default
    db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://predico_user:predico_password@localhost:5432/predico_db")
    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "+psycopg2")

# Only set if not already set in alembic.ini
if not config.get_main_option("sqlalchemy.url") or config.get_main_option("sqlalchemy.url") == "driver://user:pass@localhost/dbname":
    config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

