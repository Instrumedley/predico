# Fix Migration Revision IDs

If you're getting an error about revision IDs being too long, follow these steps:

## Option 1: Reset Database (Development Only - Deletes All Data)

```bash
# Stop containers and remove volumes
docker compose down -v

# Start fresh
docker compose up -d
```

## Option 2: Manually Fix Alembic Version Table

If you want to keep your data, manually update the alembic_version table:

```bash
# Connect to the database
docker compose exec postgres psql -U predico_user -d predico_db

# Then run these SQL commands:
DELETE FROM alembic_version;
```

Then restart the backend:

```bash
docker compose restart backend
```

## Option 3: Use Alembic Stamp

```bash
# Stamp the database with the initial revision
docker compose exec backend alembic stamp 000_init

# Then run migrations
docker compose exec backend alembic upgrade head
```

