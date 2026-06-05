# Quick Examples: Using AWS Profile

## How to Add `--profile predico` to Commands

Simply add `--profile predico` at the end of any AWS CLI command:

### Basic Syntax
```bash
aws <command> <options> --profile predico
```

### Real Examples

**1. Check your identity:**
```bash
aws sts get-caller-identity --profile predico
```

**2. List S3 buckets:**
```bash
aws s3 ls --profile predico
```

**3. Create S3 bucket:**
```bash
aws s3 mb s3://my-bucket --profile predico
```

**4. List DynamoDB tables:**
```bash
aws dynamodb list-tables --profile predico
```

**5. Check ECS clusters:**
```bash
aws ecs list-clusters --profile predico
```

### For This Project's Setup Script

The setup script already uses the profile automatically, so you don't need to add it:

```bash
cd infrastructure/scripts
./setup-aws.sh
```

The script will automatically use `--profile predico` for all AWS commands.

### For Terraform

Terraform reads from your environment. You have two options:

**Option 1: Set environment variable (recommended)**
```bash
export AWS_PROFILE=predico
cd infrastructure/terraform
terraform init -backend-config=envs/dev/backend.hcl
```

**Option 2: Add to each terraform command**
```bash
AWS_PROFILE=predico terraform init -backend-config=envs/dev/backend.hcl
```

### Quick Test

Try this to verify your profile is working:

```bash
aws sts get-caller-identity --profile predico
```

You should see:
```json
{
    "UserId": "...",
    "Account": "083413069771",
    "Arn": "arn:aws:iam::083413069771:user/predico-terraform"
}
```

If you see your `predico-terraform` user, it's working! ✅

