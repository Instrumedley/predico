# Branch Strategy & Deployment

## Environments

| Where | Purpose | Cost |
|-------|---------|------|
| **Local** (`docker-compose`) | Development & testing | $0 |
| **Heroku** (`main` branch) | Production for friends | ~$12/mo |
| **Vercel** (`main` branch) | Production frontend | $0 |

There is **no cloud staging environment** — staging happens locally. That keeps the budget at ~$12/month.

Full deploy instructions: **[docs/HEROKU.md](docs/HEROKU.md)**

## Branch workflow

| Branch | What happens |
|--------|----------------|
| `main` | Default branch; merge feature PRs here |
| Feature branches | PR → `main`; CI runs tests |

### Deploy to production

**Backend (Heroku):**

```bash
git push heroku main
# or, if your branch is not main:
git push heroku main:main
```

**Frontend (Vercel):** auto-deploys when `main` is updated (if connected in Vercel dashboard).

### Local development

```bash
docker-compose up
# Frontend: http://localhost:3005
# API: http://localhost:8000
```

## CI (GitHub Actions)

Pull requests and pushes run **tests** via `.github/workflows/ci-cd.yml`.

AWS deploy jobs in that workflow are **legacy** from the archived Terraform setup. They are skipped unless AWS secrets are configured. Safe to ignore for Heroku deployment.

## Archived: multi-branch AWS workflow

An earlier plan mapped `staging` and `production` branches to separate AWS environments. That flow is documented in `infrastructure/archive/` but is **not active**. Do not push to `staging` / `production` branches expecting cloud deploys unless you restore AWS infrastructure.
