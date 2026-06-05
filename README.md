# Predico - World Cup Predictions Platform

A scalable web platform for making predictions on World Cup games, competing with friends in private leagues, and tracking global leaderboards.

## 🏗️ Architecture Overview

This project is designed to handle millions of users with high traffic during the World Cup. The architecture follows best practices for scalability, reliability, and maintainability.

### Tech Stack

- **Backend**: Python 3.11 + FastAPI (async)
- **Frontend**: TypeScript + React 18 + Vite
- **Database**: PostgreSQL 15
- **Cache**: Redis 7 (local dev only; optional)
- **Production**: Heroku (API + Postgres) + Vercel (frontend)
- **Local**: Docker Compose

### Architecture Components

```
┌─────────────────┐
│   Cloudflare    │  (CDN & DDoS Protection)
└────────┬────────┘
         │
┌────────▼────────┐
│  Application    │  (HTTPS)
│  Load Balancer  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│Frontend│ │Backend│
│  ECS   │ │  ECS  │
└────┬───┘ └───┬───┘
     │         │
     │    ┌────┴────┐
     │    │         │
     │ ┌──▼──┐  ┌──▼──┐
     │ │Redis│  │ RDS │
     │ └─────┘  └─────┘
     │
┌────▼────┐
│   S3    │  (Static Assets)
│CloudFront│
└─────────┘
```

## 📁 Project Structure

```
predico/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core config, security, logging
│   │   ├── db/             # Database models and connection
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── alembic/            # Database migrations
│   └── requirements.txt
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── contexts/      # React contexts
│   │   ├── hooks/         # Custom hooks
│   │   ├── types/         # TypeScript types
│   │   └── utils/         # Utility functions
│   └── package.json
│
├── infrastructure/         # Archived AWS Terraform (see infrastructure/README.md)
│   └── terraform/
│
├── docs/
│   └── HEROKU.md           # Production deployment guide
│
└── docker-compose.yml      # Local development setup
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 15 (or use Docker)
- Redis 7 (or use Docker)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd predico
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Copy environment file
   cp .env.example .env
   # Edit .env with your configuration
   
   # Run database migrations
   alembic upgrade head
   
   # Start the server
   uvicorn app.main:app --reload
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   
   # Copy environment file
   cp .env.example .env
   
   # Start development server
   npm run dev
   ```

4. **Using Docker Compose (Backend Services)**
   ```bash
   # From project root
   docker-compose up -d
   
   # This will start:
   # - PostgreSQL on port 5432
   # - Redis on port 6379
   # - Backend API on port 8000
   
   # Frontend runs separately (see below)
   ```

5. **Start Frontend (Separate Terminal)**
   ```bash
   cd frontend
   npm install  # First time only
   npm run dev
   
   # Frontend will be available at http://localhost:3000
   ```

### Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## 🚀 Production deployment

Production runs on **Heroku** (API) and **Vercel** (frontend), ~$12/month.

See **[docs/HEROKU.md](docs/HEROKU.md)** for step-by-step setup: Procfile, config vars, SendGrid email, and frontend deploy.

Local staging uses `docker-compose.yml`. AWS Terraform in `infrastructure/` is archived and not used.

## 📊 Scalability (future)

- **Horizontal Scaling**: ECS Fargate with auto-scaling based on CPU/memory metrics
- **Database**: RDS with read replicas capability and connection pooling
- **Caching**: Redis for session management and frequently accessed data
- **CDN**: CloudFront for static assets and API responses
- **Load Balancing**: Application Load Balancer with health checks
- **Async Processing**: FastAPI async endpoints for high concurrency

## 🔒 Security

- HTTPS/TLS encryption
- Database encryption at rest
- Secrets management via AWS Secrets Manager
- Security groups with least privilege
- CORS configuration
- JWT authentication
- Password hashing with bcrypt

## 📝 Next Steps

1. **Database Models**: Design and implement database schema
   - Users
   - Games/Matches
   - Predictions
   - Leagues
   - League Members
   - Rankings

2. **API Endpoints**: Implement RESTful API endpoints
   - Authentication (signup, login, logout)
   - User management
   - Game management
   - Prediction CRUD
   - League management
   - Leaderboard queries

3. **Frontend Pages**: Build React components and pages
   - Landing page
   - Login/Signup
   - Dashboard
   - Predictions interface
   - League management
   - Leaderboard views

4. **Testing**: Add comprehensive tests
   - Unit tests
   - Integration tests
   - E2E tests

5. **CI/CD**: Set up continuous integration and deployment
   - GitHub Actions / GitLab CI
   - Automated testing
   - Automated deployments

## 📚 Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)

## 🤝 Contributing

This is a private project. Please follow the coding standards and submit pull requests for review.

## 📄 License

[Your License Here]

