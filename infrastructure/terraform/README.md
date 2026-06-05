# Archived — AWS ECS / Terraform (not deployed)

This Terraform configuration provisions a full AWS stack:

- VPC with NAT gateways
- ECS Fargate (backend + frontend)
- RDS PostgreSQL
- ElastiCache Redis
- Application Load Balancer
- S3 + CloudFront

**Do not apply** for the current Heroku deployment. See `infrastructure/README.md` and `docs/HEROKU.md`.

To use this in the future, start with `../archive/START_HERE.md` and review costs before applying.
