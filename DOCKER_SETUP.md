# Docker Setup Guide

This guide explains how to run the Predico project using Docker Compose and connect to the database with pgAdmin.

## Prerequisites

- Docker Desktop installed and running
- pgAdmin installed (optional, for database management)

## Quick Start

### 1. Start All Services

From the project root directory, run:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port `5432`
- Redis cache on port `6379`
- Backend API on port `8000`

**Note:** Frontend runs separately using `npm run dev` (see below)

### 2. Check Service Status

```bash
docker-compose ps
```

You should see all services running:
```
NAME                STATUS              PORTS
predico-backend    Up                 0.0.0.0:8000->8000/tcp
predico-postgres   Up                 0.0.0.0:5432->5432/tcp
predico-redis      Up                 0.0.0.0:6379->6379/tcp
```

### 3. View Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f postgres
```

### 4. Run Database Migrations

The backend container should run migrations automatically on startup. If you need to run them manually:

```bash
# Execute migration command in backend container
docker-compose exec backend alembic upgrade head
```

Or if you need to create a new migration:

```bash
docker-compose exec backend alembic revision --autogenerate -m "Your migration message"
```

## Connecting to Database with pgAdmin

### Database Connection Details

When connecting from pgAdmin (or any PostgreSQL client), use these credentials:

- **Host**: `localhost` (or `127.0.0.1`)
- **Port**: `5432`
- **Database**: `predico_db`
- **Username**: `predico_user`
- **Password**: `predico_password`

### Steps to Connect in pgAdmin

1. **Open pgAdmin** and right-click on "Servers" in the left panel
2. **Select "Create" → "Server"**
3. **In the "General" tab:**
   - Name: `Predico Local` (or any name you prefer)
4. **In the "Connection" tab:**
   - Host name/address: `localhost`
   - Port: `5432`
   - Maintenance database: `predico_db`
   - Username: `predico_user`
   - Password: `predico_password`
   - Check "Save password" if you want
5. **Click "Save"**

### Viewing Database Schema

Once connected, you can:

1. **Expand the server** → `Databases` → `predico_db` → `Schemas` → `public` → `Tables`
2. **View all tables:**
   - `users` - User accounts
   - `teams` - National teams
   - `games` - World Cup matches
   - `predictions` - User predictions
   - `leagues` - Private leagues
   - `league_members` - League memberships
   - And more...

3. **Query the database:**
   - Right-click on any table → "View/Edit Data" → "All Rows"
   - Or use the Query Tool to run SQL queries

### Example Queries

```sql
-- View all users
SELECT id, email, username, email_verified, created_at FROM users;

-- View all tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check migration history
SELECT * FROM alembic_version;
```

## Useful Docker Commands

### Stop Services

```bash
docker-compose down
```

### Stop and Remove Volumes (⚠️ This deletes all data!)

```bash
docker-compose down -v
```

### Restart a Specific Service

```bash
docker-compose restart backend
docker-compose restart postgres
```

### Frontend Development

The frontend runs outside Docker for better development experience:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

The frontend will hot-reload on code changes and proxy API requests to `http://localhost:8000`.

### Access Container Shell

```bash
# Backend container
docker-compose exec backend bash

# PostgreSQL container
docker-compose exec postgres psql -U predico_user -d predico_db
```

### Rebuild Containers (after code changes)

```bash
docker-compose build
docker-compose up -d
```

## Environment Variables

The Docker Compose file uses these default values. You can override them by creating a `.env` file in the project root:

```env
# Database
POSTGRES_USER=predico_user
POSTGRES_PASSWORD=predico_password
POSTGRES_DB=predico_db

# Backend
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True
DATABASE_URL=postgresql+asyncpg://predico_user:predico_password@postgres:5432/predico_db
REDIS_URL=redis://redis:6379/0

# Frontend
VITE_API_BASE_URL=http://localhost:8000
```

## Troubleshooting

### Port Already in Use

If you get an error that a port is already in use:

1. **Check what's using the port:**
   ```bash
   # macOS/Linux
   lsof -i :5432
   lsof -i :8000
   lsof -i :3000
   ```

2. **Change the port in docker-compose.yml:**
   ```yaml
   ports:
     - "5433:5432"  # Use 5433 instead of 5432
   ```

### Database Connection Refused

1. **Check if PostgreSQL container is running:**
   ```bash
   docker-compose ps postgres
   ```

2. **Check PostgreSQL logs:**
   ```bash
   docker-compose logs postgres
   ```

3. **Restart the database:**
   ```bash
   docker-compose restart postgres
   ```

### Migration Errors

If migrations fail:

1. **Check backend logs:**
   ```bash
   docker-compose logs backend
   ```

2. **Run migrations manually:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

3. **If you need to reset the database:**
   ```bash
   # ⚠️ WARNING: This deletes all data!
   docker-compose down -v
   docker-compose up -d
   docker-compose exec backend alembic upgrade head
   ```

## Running the Frontend

The frontend runs separately (not in Docker) for easier development:

```bash
cd frontend
npm install  # First time only
npm run dev
```

The frontend will be available at: http://localhost:3000

## Accessing the Application

Once everything is running:

- **Frontend**: http://localhost:3000 (runs via `npm run dev`)
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Database**: localhost:5432

## Next Steps

1. **Run migrations** (if not done automatically):
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

2. **Verify database schema** in pgAdmin

3. **Test the application**:
   - Visit http://localhost:3000
   - Try signing up a new user
   - Check the `users` table in pgAdmin to see the new user

4. **Check logs** if something doesn't work:
   ```bash
   docker-compose logs -f
   ```

