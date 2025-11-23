# AWS Multi-Environment Setup Guide

This guide walks you through setting up a complete CI/CD pipeline with multiple environments (local → dev → staging → production) in AWS.

## Architecture Overview

### Services We're Using

1. **ECS Fargate** - Serverless containers for backend (no EC2 to manage)
2. **RDS PostgreSQL** - Managed database service
3. **ElastiCache Redis** - Managed Redis for caching
4. **Application Load Balancer (ALB)** - Routes traffic to ECS tasks
5. **ECR** - Container registry for Docker images
6. **S3 + CloudFront** - Static assets and CDN
7. **Secrets Manager** - Secure storage for passwords and API keys
8. **GitHub Actions** - CI/CD pipeline (or AWS CodePipeline)

### Why This Architecture?

- **Serverless Containers (Fargate)**: No EC2 instances to manage, auto-scales, pay only for what you use
- **Managed Database (RDS)**: Automatic backups, high availability, easy scaling
- **Multi-Environment**: Separate infrastructure for dev/staging/prod with proper isolation

## Step-by-Step Setup

### Phase 1: Initial AWS Setup (One-Time)

#### Step 1.1: Create IAM User for Terraform

**Why**: Never use root account credentials. Create a dedicated IAM user with limited permissions.

1. Go to AWS Console → IAM → Users → "Add users"
2. Username: `predico-terraform`
3. Access type: "Programmatic access" (for API/CLI)
4. Permissions: Attach policy `AdministratorAccess` (or create custom policy - see below)
5. **Save the Access Key ID and Secret Access Key** - you'll need these!

**Custom IAM Policy** (more secure, recommended):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestTag/ManagedBy": "terraform"
        }
      }
    }
  ]
}
```

#### Step 1.2: Configure AWS CLI

```bash
# Install AWS CLI if not already installed
# macOS: brew install awscli
# Or download from: https://aws.amazon.com/cli/

# Configure with your IAM user credentials
aws configure

# Enter:
# AWS Access Key ID: [from Step 1.1]
# AWS Secret Access Key: [from Step 1.1]
# Default region: eu-north-1 (Stockholm, Sweden)
# Default output format: json
```

#### Step 1.3: Create S3 Bucket for Terraform State

**Why**: Store Terraform state remotely so multiple people/environments can work together.

```bash
# Create bucket for Terraform state (must be globally unique)
aws s3 mb s3://predico-terraform-state-$(whoami) --region eu-north-1

# Enable versioning (important for state files)
aws s3api put-bucket-versioning \
  --bucket predico-terraform-state-$(whoami) \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket predico-terraform-state-$(whoami) \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Create DynamoDB table for state locking (prevents concurrent modifications)
aws dynamodb create-table \
  --table-name predico-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region eu-north-1
```

**Note**: Replace `$(whoami)` with your username or a unique identifier.

### Phase 2: Terraform Multi-Environment Setup

#### Step 2.1: Restructure Terraform for Multiple Environments

We'll use Terraform workspaces to manage multiple environments.

#### Step 2.2: Update Terraform Backend Configuration

Update `infrastructure/terraform/main.tf` to use remote state (we'll do this in code).

### Phase 3: Deploy Dev Environment (First)

#### Step 3.1: Configure Dev Environment

```bash
cd infrastructure/terraform

# Create dev workspace
terraform workspace new dev

# Or select existing
terraform workspace select dev
```

#### Step 3.2: Create Dev Variables File

```bash
cp terraform.tfvars.example terraform.tfvars.dev
```

Edit `terraform.tfvars.dev`:
```hcl
aws_region            = "eu-north-1"  # Stockholm, Sweden
environment           = "dev"
project_name          = "predico"
db_instance_class     = "db.t3.micro"  # Small for dev
db_allocated_storage  = 20
db_max_allocated_storage = 100
fargate_cpu           = 256  # Smaller for dev
fargate_memory        = 512
min_capacity          = 1
max_capacity          = 3
domain_name           = ""  # No domain for dev
```

#### Step 3.3: Initialize and Deploy Dev

```bash
terraform init

# Review what will be created
terraform plan -var-file=terraform.tfvars.dev

# Apply (creates all infrastructure)
terraform apply -var-file=terraform.tfvars.dev
```

This will take 15-20 minutes to create all resources.

### Phase 4: Set Up CI/CD Pipeline

We'll use GitHub Actions for CI/CD.

#### Step 4.1: Create GitHub Secrets

In your GitHub repository → Settings → Secrets and variables → Actions:

Add these secrets:
- `AWS_ACCESS_KEY_ID` - Your IAM user access key
- `AWS_SECRET_ACCESS_KEY` - Your IAM user secret key
- `AWS_REGION` - `eu-north-1` (Stockholm, Sweden)

#### Step 4.2: Create GitHub Actions Workflow

We'll create workflow files that:
- Run tests on every push
- Deploy to dev on merge to `develop` branch
- Deploy to staging on merge to `staging` branch
- Deploy to production on merge to `main` branch (with manual approval)

### Phase 5: Deploy Staging and Production

Repeat Phase 3 with different variable files for staging and production.

## Environment-Specific Configurations

### Dev Environment
- Small instance sizes
- Single AZ (cheaper)
- No domain required
- Auto-scaling: 1-3 tasks
- RDS: db.t3.micro

### Staging Environment
- Medium instance sizes
- Multi-AZ for high availability
- Optional domain
- Auto-scaling: 2-5 tasks
- RDS: db.t3.small

### Production Environment
- Larger instance sizes
- Multi-AZ required
- Custom domain required
- Auto-scaling: 3-20 tasks
- RDS: db.t3.medium or larger
- Enhanced monitoring
- Backup retention: 30 days

## Cost Estimates (Monthly)

### Dev Environment
- ECS Fargate: ~$15-30
- RDS: ~$15-20
- ALB: ~$16
- ElastiCache: ~$10-15
- S3/CloudFront: ~$5
- **Total: ~$60-85/month**

### Staging Environment
- Similar to dev: ~$60-85/month

### Production Environment
- ECS Fargate: ~$50-200 (depends on traffic)
- RDS: ~$50-150
- ALB: ~$16
- ElastiCache: ~$30-50
- S3/CloudFront: ~$10-50
- **Total: ~$150-500/month** (scales with usage)

## Next Steps

1. Follow Phase 1 (Initial AWS Setup)
2. We'll restructure Terraform for multi-environment
3. Deploy dev environment
4. Set up CI/CD pipeline
5. Deploy staging and production

Let me know when you've completed Phase 1, and we'll proceed to the next steps!

