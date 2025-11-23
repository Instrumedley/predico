# 🚀 Start Here: AWS Multi-Environment Setup

> **🌍 Region**: All infrastructure is configured for **eu-north-1 (Stockholm, Sweden)** by default.
> See `REGION_NOTE.md` for details.

## Quick Answer to Your Questions

### 1. **Are we going serverless?**
**Partially!** We're using:
- ✅ **ECS Fargate** = Serverless containers (no EC2 to manage, auto-scales)
- ✅ **RDS** = Managed database (not serverless, but fully managed)
- ✅ **ElastiCache** = Managed Redis (not serverless, but fully managed)

**Not fully serverless** (like AWS Lambda), but **serverless containers** which means:
- No servers to manage
- Auto-scales based on traffic
- Pay only for what you use
- Still runs your Docker containers

### 2. **Which services host backend and database?**
- **Backend**: **ECS Fargate** (serverless containers)
- **Database**: **RDS PostgreSQL** (managed database service)

### 3. **Is the pipeline accounted for?**
✅ **Yes!** I've created:
- Multi-environment Terraform structure (dev/staging/prod)
- GitHub Actions CI/CD pipeline
- Environment-specific configurations

### 4. **Do I need to do manual work in AWS?**
**Minimal!** You only need to:
1. Create IAM user (one-time, 5 minutes)
2. Run setup script (automated)
3. Deploy via Terraform (automated)

Everything else is automated through Terraform and GitHub Actions.

## Your Action Plan

### ✅ Step 1: Read the Complete Guide
Open `STEP_BY_STEP_SETUP.md` - it has everything you need with detailed instructions.

### ✅ Step 2: Initial AWS Setup (15 minutes)

1. **Create IAM User** (AWS Console)
   - IAM → Users → Add user
   - Name: `predico-terraform`
   - Access: **Programmatic access** (check the box)
   - Click "Next: Permissions"
   - **On "Set permissions" page:**
     - Select **"Attach policies directly"** (third option)
     - In the search box, type: `AdministratorAccess`
     - Check the box next to **"AdministratorAccess"** policy
   - Click "Next: Review"
   - Click "Create user"
   
2. **Create Access Key** (if not shown during user creation)
   - On the user's page, find **"Access key 1"** section
   - Click **"Create access key"** button
   - Select **"Command Line Interface (CLI)"** as use case
   - Check the confirmation box
   - Click **"Next"** → **"Create access key"**
   - **⚠️ CRITICAL: Copy and save both:**
     - **Access key ID**: `AKIA...`
     - **Secret access key**: `...` (shown only once!)
   - Click **"Download .csv"** or copy manually

2. **Configure AWS CLI** (Using a Profile)
   
   **Important**: If you already have AWS CLI configured for another project, we'll use a **named profile** to keep them separate.
   
   ```bash
   aws configure --profile predico
   # Enter your IAM user credentials:
   # AWS Access Key ID: [paste from Step 1]
   # AWS Secret Access Key: [paste from Step 1]
   # Default region name: eu-north-1
   # Default output format: json
   ```
   
   **This creates a profile called `predico`** - your default profile remains unchanged!
   
   **To use this profile:**
   - Add `--profile predico` to AWS CLI commands, OR
   - Set environment variable: `export AWS_PROFILE=predico`
   
   **To switch back to your work project:**
   - Use `--profile default` or unset: `unset AWS_PROFILE`

3. **Run Setup Script**
   ```bash
   cd infrastructure/scripts
   # The script will automatically use the 'predico' profile
   ./setup-aws.sh
   ```
   
   **Note**: The script uses the `predico` profile automatically. See `AWS_PROFILES_GUIDE.md` for more details on managing multiple AWS profiles.

### ✅ Step 3: Deploy Dev Environment (20 minutes)

```bash
cd infrastructure/terraform
terraform init -backend-config=envs/dev/backend.hcl
terraform plan -var-file=envs/dev/terraform.tfvars
terraform apply -var-file=envs/dev/terraform.tfvars
```

### ✅ Step 4: Set Up CI/CD (10 minutes)

1. Add GitHub Secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_ACCOUNT_ID`

2. Create branches:
   ```bash
   git checkout -b develop
   git push -u origin develop
   ```

3. Push to `develop` → Auto-deploys to dev!

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│         GitHub Repository                │
│  (main/staging/develop branches)        │
└──────────────┬──────────────────────────┘
               │
               │ GitHub Actions CI/CD
               │ (Tests → Build → Deploy)
               ▼
┌─────────────────────────────────────────┐
│              AWS Account                 │
│                                          │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   Dev Env    │  │ Staging Env  │    │
│  │              │  │              │    │
│  │ ECS Fargate  │  │ ECS Fargate  │    │
│  │ RDS (small)  │  │ RDS (medium) │    │
│  │ Redis        │  │ Redis        │    │
│  │ ALB          │  │ ALB          │    │
│  └──────────────┘  └──────────────┘    │
│                                          │
│  ┌──────────────┐                       │
│  │ Production   │                       │
│  │              │                       │
│  │ ECS Fargate  │                       │
│  │ RDS (large)  │                       │
│  │ Redis        │                       │
│  │ ALB + Domain │                       │
│  └──────────────┘                       │
└─────────────────────────────────────────┘
```

## What Gets Created Per Environment

Each environment (dev/staging/prod) gets:
- ✅ Separate VPC (isolated network)
- ✅ Separate RDS database
- ✅ Separate Redis cluster
- ✅ Separate ECS cluster
- ✅ Separate ALB
- ✅ Separate ECR repositories
- ✅ Separate S3 buckets
- ✅ Separate security groups

**Complete isolation** - no resource sharing between environments!

## Cost Breakdown

| Environment | Monthly Cost | What You Get |
|------------|--------------|--------------|
| **Dev** | ~$60-85 | Small instances, single AZ |
| **Staging** | ~$60-85 | Medium instances, multi-AZ |
| **Production** | ~$150-500 | Large instances, multi-AZ, auto-scaling |

*Costs scale with actual usage*

## Next Steps

1. **Read**: `STEP_BY_STEP_SETUP.md` for detailed instructions
2. **Follow**: Phase 1 (Initial AWS Setup)
3. **Deploy**: Dev environment first
4. **Test**: Push to `develop` branch to trigger CI/CD

## Need Help?

- **Quick Start**: See `QUICK_START.md`
- **Detailed Guide**: See `STEP_BY_STEP_SETUP.md`
- **Architecture**: See `AWS_SETUP_GUIDE.md`
- **Deployment**: See `DEPLOYMENT.md`

## Important Notes

⚠️ **Never use root account** - Always use IAM user
⚠️ **Save credentials** - IAM secret keys are shown only once
⚠️ **Review Terraform plan** - Always check before applying
⚠️ **Start with dev** - Test everything in dev before staging/prod

Ready to start? Open `STEP_BY_STEP_SETUP.md` and follow Phase 1!

