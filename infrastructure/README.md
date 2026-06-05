# Infrastructure

**Current deployment:** Heroku (API) + Vercel/Cloudflare Pages (frontend).  
See **[docs/HEROKU.md](../docs/HEROKU.md)** for the active setup guide.

## What to use

| Path | Status |
|------|--------|
| `docs/HEROKU.md` | **Active** — production deployment |
| `docker-compose.yml` | **Active** — local development |
| `infrastructure/terraform/` | **Archived** — ECS/RDS/Redis Terraform (not deployed) |
| `infrastructure/archive/` | **Archived** — AWS setup guides from the original plan |

## Why archive the AWS Terraform?

The Terraform stack targets multi-environment AWS (VPC, NAT gateways, ECS Fargate, RDS, ElastiCache, ALB) at roughly **$130+/month per environment**. That is appropriate for serious production scale, not a friends-only playground (~$12/month on Heroku).

The code is kept in the repo in case you want to revisit it later. **Do not run `terraform apply`** unless you intentionally move back to AWS and accept the cost/complexity.

## If you return to AWS later

1. Read `infrastructure/archive/START_HERE.md` for context.
2. Prefer a **simplified** layout (single EC2/Lightsail + Docker Compose) over the full ECS stack for small traffic.
3. Set `EMAIL_BACKEND=ses` on AWS; use `EMAIL_BACKEND=sendgrid` on Heroku.
