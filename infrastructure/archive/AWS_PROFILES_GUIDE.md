# AWS CLI Profiles Guide

## What are AWS Profiles?

AWS CLI profiles allow you to store multiple sets of credentials and configurations. This is perfect when you work on multiple projects or have separate work/personal AWS accounts.

## Your Setup

- **Default profile**: Your work project (unchanged)
- **Predico profile**: This project (`predico`)

## How to Configure the Predico Profile

```bash
aws configure --profile predico
```

Enter:
- **AWS Access Key ID**: Your predico-terraform access key
- **AWS Secret Access Key**: Your predico-terraform secret key
- **Default region**: `eu-north-1`
- **Default output format**: `json`

**Your default profile remains untouched!** ✅

## How to Use Profiles

### Option 1: Use `--profile` flag (Recommended)

Add `--profile predico` to every AWS CLI command:

```bash
# Use predico profile
aws s3 ls --profile predico
aws sts get-caller-identity --profile predico

# Use default profile (your work project)
aws s3 ls --profile default
# or just
aws s3 ls  # Uses default if no profile specified
```

### Option 2: Set Environment Variable (For Current Session)

Set the profile for your current terminal session:

```bash
# Switch to predico profile
export AWS_PROFILE=predico
aws s3 ls  # Now uses predico profile

# Switch back to default
unset AWS_PROFILE
aws s3 ls  # Now uses default profile
```

### Option 3: Use in Scripts

You can set the profile in scripts:

```bash
#!/bin/bash
export AWS_PROFILE=predico
aws s3 ls
```

## For This Project

### Setup Script

The `setup-aws.sh` script automatically uses the `predico` profile:

```bash
cd infrastructure/scripts
./setup-aws.sh
```

Or specify a different profile:
```bash
AWS_PROFILE=predico ./setup-aws.sh
```

### Terraform

Terraform will use the AWS profile from your environment. You can:

1. **Set for current session:**
   ```bash
   export AWS_PROFILE=predico
   cd infrastructure/terraform
   terraform init -backend-config=envs/dev/backend.hcl
   ```

2. **Or use in each command:**
   ```bash
   AWS_PROFILE=predico terraform init -backend-config=envs/dev/backend.hcl
   ```

3. **Or add to your shell config** (`.zshrc` or `.bashrc`):
   ```bash
   # For predico project directory
   if [[ "$PWD" == *"predico"* ]]; then
       export AWS_PROFILE=predico
   fi
   ```

## Verify Which Profile You're Using

```bash
# Check current profile
aws configure list

# Check identity
aws sts get-caller-identity
```

## Profile Storage

Profiles are stored in:
- **Credentials**: `~/.aws/credentials`
- **Config**: `~/.aws/config`

Example `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = AKIA...  # Your work project
aws_secret_access_key = ...

[predico]
aws_access_key_id = AKIA...  # This project
aws_secret_access_key = ...
```

Example `~/.aws/config`:
```ini
[default]
region = us-east-1
output = json

[predico]
region = eu-north-1
output = json
```

## Quick Reference

| Task | Command |
|------|---------|
| Configure predico profile | `aws configure --profile predico` |
| Use predico for session | `export AWS_PROFILE=predico` |
| Use predico for one command | `aws s3 ls --profile predico` |
| Switch back to default | `unset AWS_PROFILE` |
| Check current profile | `aws configure list` |
| List all profiles | `cat ~/.aws/credentials` |

## Best Practices

1. ✅ **Always use `--profile` flag** when switching between projects
2. ✅ **Don't modify your default profile** if it's for work
3. ✅ **Use environment variables** in scripts for clarity
4. ✅ **Verify profile** before running destructive commands: `aws sts get-caller-identity --profile predico`

## Troubleshooting

**"Unable to locate credentials"**
- Make sure you've run: `aws configure --profile predico`
- Check: `cat ~/.aws/credentials` to see if `[predico]` section exists

**"Wrong account"**
- Verify profile: `aws sts get-caller-identity --profile predico`
- Check you're using the right profile

**"Region mismatch"**
- Check config: `cat ~/.aws/config`
- Override: `aws s3 ls --profile predico --region eu-north-1`

