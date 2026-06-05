# Navigating AWS Environments (Dev/Staging/Production)

All resources in AWS are tagged and named with the environment prefix: `predico-{environment}-{resource-name}`

## Quick Navigation Guide

### 1. **ECS (Elastic Container Service)** - Your Applications

**Path**: AWS Console → ECS → Clusters

You'll see:
- `predico-dev-cluster`
- `predico-staging-cluster`
- `predico-production-cluster`

**To see services:**
1. Click on a cluster (e.g., `predico-dev-cluster`)
2. Go to **Services** tab
3. You'll see:
   - `predico-dev-backend-service`
   - `predico-dev-frontend-service`

**To see running tasks:**
- Click on a service → **Tasks** tab

### 2. **RDS (Relational Database Service)** - PostgreSQL Databases

**Path**: AWS Console → RDS → Databases

You'll see:
- `predico-dev-db`
- `predico-staging-db`
- `predico-production-db`

**To see details:**
- Click on a database to see:
  - Endpoint (connection string)
  - Status
  - Instance class
  - Storage

### 3. **ElastiCache** - Redis Cache

**Path**: AWS Console → ElastiCache → Redis clusters

You'll see:
- `predico-dev-redis`
- `predico-staging-redis`
- `predico-production-redis`

### 4. **ECR (Elastic Container Registry)** - Docker Images

**Path**: AWS Console → ECR → Repositories

You'll see repositories like:
- `predico-dev-backend`
- `predico-dev-frontend`
- `predico-staging-backend`
- `predico-staging-frontend`
- `predico-production-backend`
- `predico-production-frontend`

### 5. **Application Load Balancer (ALB)**

**Path**: AWS Console → EC2 → Load Balancers

You'll see:
- `predico-dev-alb`
- `predico-staging-alb`
- `predico-production-alb`

**To get the URL:**
- Click on an ALB → Copy the **DNS name**
- Example: `predico-dev-alb-123456789.eu-north-1.elb.amazonaws.com`

### 6. **VPC (Virtual Private Cloud)** - Networking

**Path**: AWS Console → VPC → Your VPCs

You'll see:
- `predico-dev-vpc`
- `predico-staging-vpc`
- `predico-production-vpc`

### 7. **S3 Buckets** - Storage

**Path**: AWS Console → S3 → Buckets

You'll see:
- `predico-assets-dev`
- `predico-assets-staging`
- `predico-assets-production`
- `predico-terraform-state-{account-id}` (shared across environments)

## Using Tags to Filter

All resources are tagged with:
- `Environment`: `dev`, `staging`, or `production`
- `Project`: `predico`
- `ManagedBy`: `terraform`

### Filter by Environment Tag

In most AWS services, you can filter by tags:

1. Look for **Tags** column or filter option
2. Filter by: `Environment = dev` (or staging/production)
3. This shows all resources for that environment

## Quick Access URLs

### Dev Environment
- **ECS Cluster**: https://eu-north-1.console.aws.amazon.com/ecs/v2/clusters/predico-dev-cluster
- **RDS**: https://eu-north-1.console.aws.amazon.com/rds/home?region=eu-north-1#database:id=predico-dev-db
- **ALB**: https://eu-north-1.console.aws.amazon.com/ec2/v2/home?region=eu-north-1#LoadBalancers:

### Staging Environment
- **ECS Cluster**: https://eu-north-1.console.aws.amazon.com/ecs/v2/clusters/predico-staging-cluster
- **RDS**: https://eu-north-1.console.aws.amazon.com/rds/home?region=eu-north-1#database:id=predico-staging-db

### Production Environment
- **ECS Cluster**: https://eu-north-1.console.aws.amazon.com/ecs/v2/clusters/predico-production-cluster
- **RDS**: https://eu-north-1.console.aws.amazon.com/rds/home?region=eu-north-1#database:id=predico-production-db

## Using AWS CLI

You can also list resources by environment using AWS CLI:

```bash
# List ECS clusters
aws ecs list-clusters --profile predico --region eu-north-1

# List RDS instances
aws rds describe-db-instances --profile predico --region eu-north-1 \
  --query 'DBInstances[?contains(DBInstanceIdentifier, `predico-dev`)].DBInstanceIdentifier'

# List resources by tag
aws resourcegroupstaggingapi get-resources \
  --profile predico \
  --region eu-north-1 \
  --tag-filters Key=Environment,Values=dev
```

## Resource Groups (Recommended)

Create resource groups for easier navigation:

1. **AWS Console** → **Resource Groups** → **Create resource group**
2. Choose **Tag-based**
3. Add tag: `Environment = dev`
4. Name it: `predico-dev-resources`
5. Repeat for staging and production

Then you can quickly see all resources for each environment in one place!

## Cost Tracking by Environment

**Path**: AWS Console → Cost Explorer → **Cost by tag**

Filter by `Environment` tag to see costs per environment:
- Dev costs
- Staging costs
- Production costs

## Monitoring

**CloudWatch Dashboards**:
- Each environment has its own metrics
- Filter by cluster/service name to see environment-specific metrics

**Path**: AWS Console → CloudWatch → Dashboards

## Quick Reference Table

| Service | Dev | Staging | Production |
|---------|-----|---------|------------|
| **ECS Cluster** | `predico-dev-cluster` | `predico-staging-cluster` | `predico-production-cluster` |
| **RDS Database** | `predico-dev-db` | `predico-staging-db` | `predico-production-db` |
| **Redis** | `predico-dev-redis` | `predico-staging-redis` | `predico-production-redis` |
| **ALB** | `predico-dev-alb` | `predico-staging-alb` | `predico-production-alb` |
| **VPC** | `predico-dev-vpc` | `predico-staging-vpc` | `predico-production-vpc` |
| **S3 Assets** | `predico-assets-dev` | `predico-assets-staging` | `predico-assets-production` |

## Pro Tip

Bookmark the main services you use frequently:
- ECS Clusters
- RDS Databases
- Load Balancers
- CloudWatch (for monitoring)

This makes switching between environments much faster!

