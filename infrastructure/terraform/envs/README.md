# Environment-Specific Terraform Configuration

This directory contains environment-specific configurations for dev, staging, and production.

## Structure

```
envs/
├── dev/
│   ├── backend.hcl          # Terraform state backend config
│   └── terraform.tfvars     # Environment variables
├── staging/
│   ├── backend.hcl
│   └── terraform.tfvars
└── production/
    ├── backend.hcl
    └── terraform.tfvars
```

## Usage

### Initialize for an Environment

```bash
# From infrastructure/terraform directory
cd ../..  # Go to project root
cd infrastructure/terraform

# Initialize with dev backend
terraform init -backend-config=envs/dev/backend.hcl

# Plan with dev variables
terraform plan -var-file=envs/dev/terraform.tfvars

# Apply
terraform apply -var-file=envs/dev/terraform.tfvars
```

### Switch Environments

```bash
# For staging
terraform init -reconfigure -backend-config=envs/staging/backend.hcl
terraform plan -var-file=envs/staging/terraform.tfvars
terraform apply -var-file=envs/staging/terraform.tfvars

# For production
terraform init -reconfigure -backend-config=envs/production/backend.hcl
terraform plan -var-file=envs/production/terraform.tfvars
terraform apply -var-file=envs/production/terraform.tfvars
```

## Important Notes

1. **Never commit sensitive data** - Use AWS Secrets Manager for passwords and API keys
2. **Always review plan** before applying, especially for production
3. **Use separate AWS accounts** for production if possible (best practice)
4. **Backup before major changes** in production

