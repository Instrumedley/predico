# Step-by-Step AWS Multi-Environment Setup

This is your complete guide to set up the Predico project in AWS with dev, staging, and production environments.

## Architecture Overview

**We're using:**
- ✅ **ECS Fargate** (Serverless containers) - Hosts your backend API
- ✅ **RDS PostgreSQL** (Managed database) - Your database
- ✅ **ElastiCache Redis** - Caching layer
- ✅ **Application Load Balancer** - Routes traffic
- ✅ **ECR** - Stores Docker images
- ✅ **S3 + CloudFront** - Static assets
- ✅ **GitHub Actions** - CI/CD pipeline

**This is NOT fully serverless** (like Lambda), but uses **serverless containers** (Fargate) which means:
- No EC2 instances to manage
- Auto-scales based on demand
- Pay only for what you use
- Still runs Docker containers

## Phase 1: Initial AWS Setup (Do This First)

### Step 1.1: Create IAM User for Terraform

**⚠️ IMPORTANT: Never use root account credentials for Terraform!**

1. Go to [AWS Console](https://console.aws.amazon.com)
2. Navigate to **IAM** → **Users** → **Add users**
3. **Step 1: Specify user details**
   - Username: `predico-terraform`
   - Access type: Check **"Access key - Programmatic access"** ✅
   - Click **"Next: Permissions"**
4. **Step 2: Set permissions**
   - Select the third option: **"Attach policies directly"** (radio button)
   - In the search box that appears, type: `AdministratorAccess`
   - Check the box ✅ next to **"AdministratorAccess"** policy
   - Click **"Next: Review"**
5. **Step 3: Review and create**
   - Review the settings
   - Click **"Create user"**
6. **Step 4: Create Access Key** (if not shown automatically)
   - After user creation, you'll be on the user's summary page
   - Find **"Access key 1"** section
   - Click **"Create access key"** button
   - Select **"Command Line Interface (CLI)"** as the use case
   - Check the confirmation checkbox
   - Click **"Next"** → **"Create access key"**
   - **⚠️ CRITICAL: Save these credentials immediately!**
     - **Access Key ID**: `AKIA...` (copy this)
     - **Secret Access Key**: `...` (copy this - **only shown once!**)
   - Click **"Download .csv"** to save them securely

### Step 1.2: Configure AWS CLI (Using a Profile)

**If you already have AWS CLI configured for another project**, we'll use a **named profile** to keep configurations separate.

```bash
# Configure a named profile for this project
aws configure --profile predico

# Enter:
# AWS Access Key ID: [paste from Step 1.1]
# AWS Secret Access Key: [paste from Step 1.1]
# Default region name: eu-north-1 (Stockholm, Sweden)
# Default output format: json

# Verify it works
aws sts get-caller-identity --profile predico
```

**This creates a profile called `predico`** - your default profile remains unchanged!

**How to use profiles:**
- **Use predico profile**: Add `--profile predico` to commands, OR set `export AWS_PROFILE=predico`
- **Use default profile**: Use `--profile default` or `unset AWS_PROFILE`
- **Check current profile**: `aws configure list` (shows current profile)

**Example:**
```bash
# Use predico profile
aws s3 ls --profile predico

# Switch to predico for current session
export AWS_PROFILE=predico
aws s3 ls  # Now uses predico profile

# Switch back to default
unset AWS_PROFILE
aws s3 ls  # Now uses default profile
```

You should see your account ID and user ARN when verifying.

### Step 1.3: Run Setup Script

We've created a script to set up the initial AWS resources:

```bash
cd infrastructure/scripts
./setup-aws.sh
```

This script will:
- Create S3 bucket for Terraform state
- Enable versioning and encryption
- Create DynamoDB table for state locking
- Update backend configuration files

**Or manually** (if script doesn't work):

```bash
# Get your AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="predico-terraform-state-${AWS_ACCOUNT_ID}"

# Create S3 bucket
aws s3 mb s3://${BUCKET_NAME} --region eu-north-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ${BUCKET_NAME} \
  --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
  --bucket ${BUCKET_NAME} \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# Create DynamoDB table for locking
aws dynamodb create-table \
  --table-name predico-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region eu-north-1
```

### Step 1.4: Update Backend Configuration

After running the script, update the backend.hcl files with your bucket name:

```bash
# Get your account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Update all backend files
find infrastructure/terraform/envs -name "backend.hcl" -exec sed -i '' "s/predico-terraform-state/predico-terraform-state-${AWS_ACCOUNT_ID}/g" {} \;
```

## Phase 2: Deploy Dev Environment

### Step 2.1: Initialize Terraform for Dev

```bash
cd infrastructure/terraform

# Initialize with dev backend configuration
terraform init -backend-config=envs/dev/backend.hcl
```

### Step 2.2: Review What Will Be Created

```bash
# Plan the deployment
terraform plan -var-file=envs/dev/terraform.tfvars
```

Review the output carefully. It will show all resources that will be created.

### Step 2.3: Deploy Dev Environment

```bash
# Apply the configuration (creates all resources)
terraform apply -var-file=envs/dev/terraform.tfvars

# Type "yes" when prompted
```

**⏱️ This will take 15-20 minutes** to create all resources.

### Step 2.4: Save Important Outputs

After deployment completes:

```bash
# Get important values
terraform output

# Save these for later:
# - ecr_backend_repository_url
# - ecr_frontend_repository_url
# - alb_dns_name
# - rds_endpoint
```

## Phase 3: Set Up GitHub Actions CI/CD

### Step 3.1: Add GitHub Secrets

Go to your GitHub repository:
1. **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**
3. Add these secrets:

   - **Name**: `AWS_ACCESS_KEY_ID`
     **Value**: Your IAM user access key from Step 1.1

   - **Name**: `AWS_SECRET_ACCESS_KEY`
     **Value**: Your IAM user secret key from Step 1.1

   - **Name**: `AWS_ACCOUNT_ID`
     **Value**: Your AWS account ID (get it with `aws sts get-caller-identity --query Account --output text`)

### Step 3.2: Create Branch Structure

```bash
# Create branches for different environments
git checkout -b develop
git push -u origin develop

git checkout -b staging
git push -u origin staging

# Main branch is already production
```

### Step 3.3: Test CI/CD

The GitHub Actions workflow will:
- **On push to `develop`**: Deploy to dev environment
- **On push to `staging`**: Deploy to staging environment  
- **On push to `main`**: Deploy to production (requires approval)

Push a change to test:

```bash
git checkout develop
# Make a small change
git add .
git commit -m "test: CI/CD pipeline"
git push
```

Check GitHub Actions tab to see the pipeline run.

## Phase 4: Deploy Staging Environment

### Step 4.1: Initialize Terraform for Staging

```bash
cd infrastructure/terraform

# Reinitialize with staging backend
terraform init -reconfigure -backend-config=envs/staging/backend.hcl
```

### Step 4.2: Deploy Staging

```bash
terraform plan -var-file=envs/staging/terraform.tfvars
terraform apply -var-file=envs/staging/terraform.tfvars
```

## Phase 5: Deploy Production Environment

### Step 5.1: Get a Domain (Optional but Recommended)

1. Register a domain (Route 53, Namecheap, etc.)
2. Update `envs/production/terraform.tfvars`:
   ```hcl
   domain_name = "yourdomain.com"
   ```

### Step 5.2: Initialize Terraform for Production

```bash
cd infrastructure/terraform

# Reinitialize with production backend
terraform init -reconfigure -backend-config=envs/production/backend.hcl
```

### Step 5.3: Deploy Production

```bash
# Review carefully!
terraform plan -var-file=envs/production/terraform.tfvars

# Apply (be careful - this is production!)
terraform apply -var-file=envs/production/terraform.tfvars
```

## Phase 6: Configure GitHub Environments

For production deployments to require approval:

1. Go to GitHub repository → **Settings** → **Environments**
2. Click **"New environment"**
3. Name: `production`
4. Enable **"Required reviewers"** (add yourself)
5. Save

Now production deployments will require manual approval in GitHub Actions.

## Quick Reference Commands

### Switch Between Environments

```bash
cd infrastructure/terraform

# Dev
terraform init -reconfigure -backend-config=envs/dev/backend.hcl
terraform plan -var-file=envs/dev/terraform.tfvars

# Staging
terraform init -reconfigure -backend-config=envs/staging/backend.hcl
terraform plan -var-file=envs/staging/terraform.tfvars

# Production
terraform init -reconfigure -backend-config=envs/production/backend.hcl
terraform plan -var-file=envs/production/terraform.tfvars
```

### View Resources

```bash
# List all resources
terraform state list

# Show specific resource
terraform state show aws_ecs_cluster.main

# Get outputs
terraform output
```

### Destroy Environment (⚠️ Careful!)

```bash
# Only for dev/staging - NEVER for production without backup!
terraform destroy -var-file=envs/dev/terraform.tfvars
```

## Troubleshooting

### "Bucket already exists"
- S3 bucket names are globally unique
- Use a different name or add your account ID

### "Access Denied"
- Check IAM user has correct permissions
- Verify AWS credentials: `aws sts get-caller-identity`

### "State locked"
- Another Terraform operation is running
- Or previous operation crashed
- Check DynamoDB table: `aws dynamodb scan --table-name predico-terraform-locks`

### Terraform state out of sync
```bash
# Refresh state
terraform refresh -var-file=envs/dev/terraform.tfvars
```

## Cost Monitoring

Set up billing alerts:

1. AWS Console → **Billing** → **Billing preferences**
2. Enable **"Receive Billing Alerts"**
3. **CloudWatch** → **Alarms** → **Create alarm**
4. Metric: `EstimatedCharges`
5. Threshold: Set your budget limit

## Next Steps After Setup

1. ✅ Configure domain and SSL certificates
2. ✅ Set up monitoring and alerts
3. ✅ Configure backup schedules
4. ✅ Set up log aggregation
5. ✅ Configure auto-scaling policies
6. ✅ Set up database read replicas (for production)

## Support

If you get stuck:
1. Check AWS CloudWatch logs
2. Check Terraform state: `terraform show`
3. Review AWS Console for resource status
4. Check GitHub Actions logs for CI/CD issues

