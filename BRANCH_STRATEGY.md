# Branch Strategy & Deployment

## Branch to Environment Mapping

| Branch | Environment | Auto-Deploy | Purpose |
|--------|-------------|-------------|---------|
| `main` | **Dev** | ✅ Yes | Default branch, frequent deployments |
| `develop` | **Dev** | ✅ Yes | Development work (alternative to main) |
| `staging` | **Staging** | ✅ Yes | Pre-production testing |
| `production` | **Production** | ✅ Yes | Production deployments (manual trigger) |

## Workflow

### Daily Development (Main Branch)
1. Create feature branch from `main`
2. Make changes and commit
3. Create PR to `main`
4. Merge PR → **Auto-deploys to Dev** ✅

### Staging Testing
1. Merge `main` → `staging` (or create PR)
2. Push to `staging` → **Auto-deploys to Staging** ✅

### Production Deployment
1. When ready for production:
   ```bash
   git checkout production
   git merge main  # or staging
   git push origin production
   ```
2. Push to `production` → **Auto-deploys to Production** ✅

## Why This Setup?

- **Main → Dev**: Keeps main branch active with frequent deployments
- **Production Branch**: Explicit control over production deployments
- **Standard Default**: Main remains the default branch (GitHub standard)
- **Safety**: Production deployments only happen when you push to `production` branch

## Important Notes

⚠️ **Production deployments are automatic** - there's no manual approval gate by default. If you want to add manual approval:

1. Go to GitHub → Settings → Environments
2. Create/Edit `production` environment
3. Enable "Required reviewers"
4. Add yourself as reviewer

Then production deployments will require manual approval in GitHub Actions.

## Quick Reference

```bash
# Deploy to dev (automatic on merge to main)
git checkout main
git merge feature-branch
git push origin main

# Deploy to staging
git checkout staging
git merge main
git push origin staging

# Deploy to production
git checkout production
git merge main  # or staging
git push origin production
```

