# Quick Start: AWS Multi-Environment Setup

## TL;DR - Get Started in 5 Steps

### 1. Create IAM User (5 minutes)
- AWS Console → IAM → Users → Add user
- Name: `predico-terraform`
- Access: Programmatic access
- Permissions: AdministratorAccess
- **Save the credentials!**

### 2. Configure AWS CLI (1 minute)
```bash
aws configure
# Enter your IAM user credentials
```

### 3. Run Setup Script (2 minutes)
```bash
cd infrastructure/scripts
./setup-aws.sh
```

### 4. Deploy Dev Environment (20 minutes)
```bash
cd infrastructure/terraform
terraform init -backend-config=envs/dev/backend.hcl
terraform plan -var-file=envs/dev/terraform.tfvars
terraform apply -var-file=envs/dev/terraform.tfvars
```

### 5. Set Up GitHub Actions (5 minutes)
- Add secrets to GitHub: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ACCOUNT_ID`
- Push to `develop` branch to trigger dev deployment

## Architecture Summary

**Backend Hosting**: ECS Fargate (Serverless containers)
- No EC2 to manage
- Auto-scales automatically
- Pay per use

**Database**: RDS PostgreSQL (Managed)
- Automatic backups
- High availability
- Easy scaling

**Environments**:
- **Local**: Docker Compose (your machine)
- **Dev**: Small instances, single AZ
- **Staging**: Medium instances, multi-AZ
- **Production**: Large instances, multi-AZ, custom domain

## Detailed Guides

- **Complete Step-by-Step**: See `STEP_BY_STEP_SETUP.md`
- **Architecture Details**: See `AWS_SETUP_GUIDE.md`
- **Deployment**: See `DEPLOYMENT.md`

## Cost Estimates

- **Dev**: ~$60-85/month
- **Staging**: ~$60-85/month  
- **Production**: ~$150-500/month (scales with traffic)

## Need Help?

1. Check `STEP_BY_STEP_SETUP.md` for detailed instructions
2. Review AWS Console for resource status
3. Check Terraform state: `terraform show`
4. Review GitHub Actions logs

