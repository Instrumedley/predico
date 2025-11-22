# Predico - World Cup Predictions Platform

A scalable web platform for making predictions on World Cup games, competing with friends in private leagues, and tracking global leaderboards.

## 🏗️ Architecture Overview

This project is designed to handle millions of users with high traffic during the World Cup. The architecture follows best practices for scalability, reliability, and maintainability.

### Tech Stack

- **Backend**: Python 3.11 + FastAPI (async)
- **Frontend**: TypeScript + React 18 + Vite
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Infrastructure**: AWS (ECS Fargate, RDS, ElastiCache, ALB, S3, CloudFront)
- **IaC**: Terraform
- **Containerization**: Docker

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
├── infrastructure/         # Terraform IaC
│   └── terraform/
│       ├── main.tf        # Main configuration
│       ├── vpc.tf         # VPC and networking
│       ├── rds.tf         # PostgreSQL database
│       ├── ecs.tf         # ECS cluster and services
│       ├── alb.tf         # Application Load Balancer
│       ├── s3.tf          # S3 and CloudFront
│       └── redis.tf       # ElastiCache Redis
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

4. **Using Docker Compose (Recommended)**
   ```bash
   # From project root
   docker-compose up -d
   
   # This will start:
   # - PostgreSQL on port 5432
   # - Redis on port 6379
   # - Backend API on port 8000
   # - Frontend on port 3000
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

## 🏗️ Infrastructure Deployment

### Prerequisites

- AWS CLI configured
- Terraform >= 1.5.0
- AWS account with appropriate permissions

### Deploy Infrastructure

1. **Navigate to Terraform directory**
   ```bash
   cd infrastructure/terraform
   ```

2. **Configure variables**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your values
   ```

3. **Initialize Terraform**
   ```bash
   terraform init
   ```

4. **Plan deployment**
   ```bash
   terraform plan
   ```

5. **Apply infrastructure**
   ```bash
   terraform apply
   ```

### Deploy Application

1. **Build and push Docker images to ECR**
   ```bash
   # Backend
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker build -t predico-backend ./backend
   docker tag predico-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/predico-backend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/predico-backend:latest
   
   # Frontend
   docker build -t predico-frontend ./frontend
   docker tag predico-frontend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/predico-frontend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/predico-frontend:latest
   ```

2. **Update ECS services** (Terraform will create ECS task definitions - you'll need to create services separately or add them to Terraform)

## 📊 Scalability Features

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

