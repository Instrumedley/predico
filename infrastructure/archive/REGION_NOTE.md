# Important: AWS Region Configuration

## Region: eu-north-1 (Stockholm, Sweden)

All infrastructure is configured to use **eu-north-1 (Stockholm, Sweden)** by default.

### Why This Region?

- ✅ **Lower Latency**: Closer to your location and European users
- ✅ **GDPR Compliance**: Data stays in EU
- ✅ **Cost**: Generally similar or slightly lower than US regions
- ✅ **Service Availability**: All required services are available

### Services Available in eu-north-1

✅ **Available:**
- ECS Fargate
- RDS PostgreSQL
- ElastiCache Redis
- Application Load Balancer
- ECR (Container Registry)
- S3
- CloudFront
- Secrets Manager
- ACM (SSL Certificates)
- VPC and Networking

### Important Notes

1. **S3 Bucket Names**: Must be globally unique across all AWS regions
2. **ACM Certificates**: Must be in the same region as ALB (eu-north-1)
3. **CloudFront**: Can use certificates from any region, but ALB certificates must be in eu-north-1
4. **Cost**: Prices may vary slightly from US regions, but generally competitive

### If You Need to Change Region

If you want to use a different region:

1. Update `variables.tf`: Change default `aws_region`
2. Update all `envs/*/backend.hcl` files: Change `region`
3. Update all `envs/*/terraform.tfvars` files: Change `aws_region`
4. Update `.github/workflows/ci-cd.yml`: Change `AWS_REGION` env var
5. Update `infrastructure/scripts/setup-aws.sh`: Change default region

### Region-Specific Considerations

**eu-north-1 Specific:**
- Some newer AWS services might have limited availability
- Check service availability before deploying if using cutting-edge features
- For World Cup predictions, EU region is ideal for European users

### Multi-Region (Future)

If you want to expand globally later:
- You can deploy to multiple regions
- Use Route 53 for global routing
- Replicate RDS across regions for disaster recovery
- Use CloudFront for global CDN

For now, **eu-north-1 is perfect** for your use case!

