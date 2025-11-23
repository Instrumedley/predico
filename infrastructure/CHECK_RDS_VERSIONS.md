# Checking Available PostgreSQL Versions in eu-north-1

If you get version errors, you can check what versions are available:

## Method 1: AWS CLI

```bash
aws rds describe-db-engine-versions \
  --engine postgres \
  --region eu-north-1 \
  --profile predico \
  --query 'DBEngineVersions[?contains(EngineVersion, `15.`)].EngineVersion' \
  --output table
```

This will show all PostgreSQL 15.x versions available in eu-north-1.

## Method 2: AWS Console

1. Go to RDS → Databases → Create database
2. Select PostgreSQL
3. Check the "Engine version" dropdown - it shows available versions

## Method 3: Use Latest Available

You can also let Terraform use the latest available by removing the specific version:

```hcl
engine         = "postgres"
# engine_version = "15.5"  # Comment out to use latest
```

But specifying a version is better for reproducibility.

## Common Available Versions (as of 2024)

- PostgreSQL 15.5, 15.6, 15.7 (commonly available)
- PostgreSQL 14.x (older but stable)
- PostgreSQL 16.x (newer, may not be in all regions)

## If 15.5 Doesn't Work

Try these in order:
1. `15.5`
2. `15.6`
3. `15.7`
4. Or check with the AWS CLI command above

