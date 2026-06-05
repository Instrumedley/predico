# Terraform State Storage Explained

## One Bucket, Multiple State Files ✅

**Yes, one S3 bucket serves all 3 environments - and that's actually the IDEAL setup!**

### How It Works

One S3 bucket stores **multiple state files**, one per environment, using different **keys** (paths):

```
predico-terraform-state-083413069771/
├── dev/terraform.tfstate          ← Dev environment state
├── staging/terraform.tfstate      ← Staging environment state
└── production/terraform.tfstate   ← Production environment state
```

### Why This Is Better

✅ **Cost Effective**: One bucket instead of three (minimal cost difference, but simpler)
✅ **Centralized Management**: All state files in one place
✅ **Easier Backups**: One bucket to backup/version
✅ **Simpler IAM**: One bucket policy instead of three
✅ **Standard Practice**: This is how Terraform is designed to work

### How Environments Are Separated

Each environment has a **different key** (path) in the same bucket:

- **Dev**: `dev/terraform.tfstate`
- **Staging**: `staging/terraform.tfstate`
- **Production**: `production/terraform.tfstate`

The `key` in each `backend.hcl` file is different, which keeps environments completely isolated.

### State Locking

The DynamoDB table (`predico-terraform-locks`) handles locking for **all environments**:
- When Terraform runs for dev, it locks `dev/terraform.tfstate`
- When Terraform runs for staging, it locks `staging/terraform.tfstate`
- They don't interfere with each other because they use different keys

### Security

Even though they're in the same bucket, environments are isolated:
- Different state files (can't accidentally modify wrong environment)
- Different keys prevent cross-environment access
- IAM policies can restrict access per environment if needed

## Alternative (Not Recommended)

You *could* create separate buckets:
- `predico-terraform-state-dev-083413069771`
- `predico-terraform-state-staging-083413069771`
- `predico-terraform-state-production-083413069771`

But this adds complexity without benefits:
- More buckets to manage
- More IAM policies
- More backup configurations
- No real security benefit (keys already isolate environments)

## Conclusion

**One bucket, multiple keys = Best Practice** ✅

This is the standard Terraform pattern and what we're using.

