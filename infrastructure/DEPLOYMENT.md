# Deployment Guide

This guide walks you through deploying the Predico application to AWS.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Terraform** >= 1.5.0 installed
4. **Docker** installed (for building images)
5. **Domain name** (optional, for production)

## Step 1: Configure Terraform Variables

1. Navigate to the Terraform directory:
   ```bash
   cd infrastructure/terraform
   ```

2. Copy the example variables file:
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

3. Edit `terraform.tfvars` with your values:
   ```hcl
   aws_region            = "us-east-1"
   environment           = "dev"  # or "staging", "prod"
   project_name          = "predico"
   db_instance_class     = "db.t3.micro"  # Use larger instance for production
   db_allocated_storage  = 20
   db_max_allocated_storage = 100
   fargate_cpu           = 512
   fargate_memory        = 1024
   min_capacity          = 1
   max_capacity          = 10
   domain_name           = ""  # Set your domain for production
   ```

## Step 2: Initialize and Plan Terraform

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Review the plan:
   ```bash
   terraform plan
   ```

3. Apply the infrastructure:
   ```bash
   terraform apply
   ```

   This will create:
   - VPC with public/private/database subnets
   - RDS PostgreSQL instance
   - ElastiCache Redis cluster
   - ECS Fargate cluster
   - Application Load Balancer
   - ECR repositories for backend and frontend
   - S3 bucket and CloudFront distribution
   - Security groups and IAM roles

## Step 3: Get Infrastructure Outputs

After Terraform completes, note the outputs:

```bash
terraform output
```

Important outputs:
- `ecr_backend_repository_url` - ECR repository for backend
- `ecr_frontend_repository_url` - ECR repository for frontend
- `rds_endpoint` - Database connection endpoint
- `alb_dns_name` - Load balancer DNS name

## Step 4: Configure Database Secrets

1. Get the database password from Secrets Manager:
   ```bash
   aws secretsmanager get-secret-value \
     --secret-id predico/database/password \
     --query SecretString --output text
   ```

2. Construct the database URL:
   ```
   postgresql+asyncpg://predico_admin:<password>@<rds_endpoint>:5432/predico_db
   ```

3. Store application secrets in Secrets Manager:
   ```bash
   # Create a JSON secret with all application config
   aws secretsmanager create-secret \
     --name predico/app/secrets \
     --secret-string '{
       "DATABASE_URL": "postgresql+asyncpg://...",
       "SECRET_KEY": "your-secret-key-here",
       "REDIS_URL": "redis://<redis-endpoint>:6379/0"
     }'
   ```

## Step 5: Build and Push Docker Images

### Backend

1. Get ECR login:
   ```bash
   aws ecr get-login-password --region us-east-1 | \
     docker login --username AWS --password-stdin \
     <account-id>.dkr.ecr.us-east-1.amazonaws.com
   ```

2. Build and tag:
   ```bash
   cd ../../backend
   docker build -t predico-backend .
   docker tag predico-backend:latest \
     <ecr_backend_repository_url>:latest
   ```

3. Push to ECR:
   ```bash
   docker push <ecr_backend_repository_url>:latest
   ```

### Frontend

1. Build and tag:
   ```bash
   cd ../frontend
   docker build -t predico-frontend .
   docker tag predico-frontend:latest \
     <ecr_frontend_repository_url>:latest
   ```

2. Push to ECR:
   ```bash
   docker push <ecr_frontend_repository_url>:latest
   ```

## Step 6: Update ECS Services

The ECS services are created by Terraform, but you may need to force a new deployment after pushing images:

```bash
aws ecs update-service \
  --cluster predico-cluster \
  --service predico-backend-service \
  --force-new-deployment

aws ecs update-service \
  --cluster predico-cluster \
  --service predico-frontend-service \
  --force-new-deployment
```

## Step 7: Run Database Migrations

1. Connect to the ECS task or use a temporary container:
   ```bash
   # Option 1: Run migrations via ECS exec (if enabled)
   aws ecs execute-command \
     --cluster predico-cluster \
     --task <task-id> \
     --container backend \
     --command "alembic upgrade head" \
     --interactive

   # Option 2: Use a temporary container
   docker run --rm \
     -e DATABASE_URL="<database-url>" \
     predico-backend:latest \
     alembic upgrade head
   ```

## Step 8: Configure Cloudflare (Optional)

If using Cloudflare:

1. Add your domain to Cloudflare
2. Point DNS records to the ALB:
   - A record: `@` -> ALB IP (or use CNAME if supported)
   - A record: `www` -> ALB IP
3. Enable Cloudflare proxy for DDoS protection
4. Configure SSL/TLS mode to "Full" or "Full (strict)"

## Step 9: Verify Deployment

1. Check ECS service status:
   ```bash
   aws ecs describe-services \
     --cluster predico-cluster \
     --services predico-backend-service predico-frontend-service
   ```

2. Check ALB target health:
   ```bash
   aws elbv2 describe-target-health \
     --target-group-arn <backend-target-group-arn>
   ```

3. Test the application:
   - Backend health: `http://<alb-dns-name>/health`
   - Frontend: `http://<alb-dns-name>/`
   - API docs: `http://<alb-dns-name>/api/docs`

## Monitoring and Logs

### View Logs

```bash
# Backend logs
aws logs tail /ecs/predico --follow

# Filter by service
aws logs filter-log-events \
  --log-group-name /ecs/predico \
  --log-stream-name-prefix backend
```

### CloudWatch Metrics

Monitor:
- ECS service CPU and memory utilization
- ALB request count and latency
- RDS connection count and CPU utilization
- Redis cache hit rate

## Scaling

Auto-scaling is configured based on CPU and memory utilization. You can manually adjust:

```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/predico-cluster/predico-backend-service \
  --min-capacity 2 \
  --max-capacity 20
```

## Troubleshooting

### ECS Tasks Not Starting

1. Check task definition:
   ```bash
   aws ecs describe-task-definition \
     --task-definition predico-backend
   ```

2. Check CloudWatch logs for errors

3. Verify security groups allow traffic

### Database Connection Issues

1. Verify RDS security group allows connections from ECS security group
2. Check database endpoint and credentials
3. Test connection from ECS task:
   ```bash
   aws ecs execute-command \
     --cluster predico-cluster \
     --task <task-id> \
     --container backend \
     --command "python -c 'import asyncpg; print(\"OK\")'" \
     --interactive
   ```

### High Costs

- Use smaller instance types for development
- Enable RDS auto-pause for dev environments
- Use Spot instances for ECS (not configured by default)
- Review CloudWatch log retention periods

## Cleanup

To destroy all infrastructure:

```bash
cd infrastructure/terraform
terraform destroy
```

**Warning**: This will delete all resources including databases. Make sure to backup data first!

