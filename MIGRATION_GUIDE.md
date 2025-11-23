# Database Migration Guide

This guide explains how to run database migrations for the Predico project.

## Migration File Created

A migration file has been created at:
```
backend/alembic/versions/001_add_email_verification_fields.py
```

This migration adds the following fields to the `users` table:
- `email_verified` (Boolean, default False)
- `email_verification_token` (String, nullable, unique, indexed)
- `password_reset_token` (String, nullable, unique, indexed)
- `password_reset_expires` (DateTime, nullable)

## Running Migrations

### Option 1: Using Docker Compose (Recommended)

The docker-compose.yml is configured to automatically run migrations on backend startup:

```bash
# Start all services (migrations run automatically)
docker-compose up -d

# Check backend logs to see migration output
docker-compose logs backend
```

### Option 2: Manual Migration in Docker

If you need to run migrations manually:

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Check current migration version
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history
```

### Option 3: Local Development (without Docker)

If running locally without Docker:

1. **Install dependencies:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL
   ```

3. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

## Verifying Migration

### Using pgAdmin

1. Connect to the database (see DOCKER_SETUP.md for connection details)
2. Navigate to: `predico_db` → `Schemas` → `public` → `Tables` → `users`
3. Right-click on `users` → "View/Edit Data" → "All Rows"
4. Check the columns - you should see:
   - `email_verified`
   - `email_verification_token`
   - `password_reset_token`
   - `password_reset_expires`

### Using SQL Query

```sql
-- Check if columns exist
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- Check indexes
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'users';
```

### Using psql Command Line

```bash
# Connect to database
docker-compose exec postgres psql -U predico_user -d predico_db

# Check table structure
\d users

# Check migration version
SELECT * FROM alembic_version;
```

## Creating New Migrations

When you modify models, create a new migration:

```bash
# In Docker
docker-compose exec backend alembic revision --autogenerate -m "Description of changes"

# Locally
alembic revision --autogenerate -m "Description of changes"
```

Then review the generated migration file in `backend/alembic/versions/` before applying it.

## Rolling Back Migrations

⚠️ **Warning**: Only rollback in development. Never rollback in production without backing up data first.

```bash
# Rollback one migration
docker-compose exec backend alembic downgrade -1

# Rollback to specific revision
docker-compose exec backend alembic downgrade <revision_id>

# Rollback all migrations
docker-compose exec backend alembic downgrade base
```

## Troubleshooting

### Migration Fails

1. **Check database connection:**
   ```bash
   docker-compose ps postgres
   docker-compose logs postgres
   ```

2. **Check backend logs:**
   ```bash
   docker-compose logs backend
   ```

3. **Verify DATABASE_URL:**
   ```bash
   docker-compose exec backend env | grep DATABASE_URL
   ```

### "Table already exists" Error

If you get errors about tables already existing, the database might have been created manually. You can:

1. **Mark migration as complete without running it:**
   ```bash
   docker-compose exec backend alembic stamp head
   ```

2. **Or reset the database (⚠️ deletes all data):**
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

### Migration Out of Sync

If your database schema doesn't match your models:

1. **Generate a new migration:**
   ```bash
   docker-compose exec backend alembic revision --autogenerate -m "Sync schema"
   ```

2. **Review the migration file carefully**

3. **Apply it:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

## Next Steps

After running migrations:

1. ✅ Verify the `users` table has the new columns
2. ✅ Test signup functionality
3. ✅ Check that email verification tokens are being stored
4. ✅ Test password reset functionality

