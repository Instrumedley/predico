#!/bin/bash
# AWS Initial Setup Script
# This script helps set up the initial AWS resources needed for Terraform

set -e

echo "🚀 Predico AWS Setup Script"
echo "============================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed.${NC}"
    echo "Please install it from: https://aws.amazon.com/cli/"
    exit 1
fi

# Check for profile
AWS_PROFILE=${AWS_PROFILE:-predico}
echo "Using AWS profile: ${AWS_PROFILE}"
echo ""

# Check if AWS credentials are configured
if ! aws sts get-caller-identity --profile "${AWS_PROFILE}" --no-cli-pager &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured for profile '${AWS_PROFILE}'.${NC}"
    echo "Please run: aws configure --profile ${AWS_PROFILE}"
    exit 1
fi

echo -e "${GREEN}✅ AWS CLI is installed and configured${NC}"
echo ""

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile "${AWS_PROFILE}" --query Account --output text --no-cli-pager)
AWS_REGION=${AWS_REGION:-eu-north-1}  # Stockholm, Sweden
BUCKET_NAME="predico-terraform-state-${AWS_ACCOUNT_ID}"

echo "AWS Account ID: ${AWS_ACCOUNT_ID}"
echo "AWS Region: ${AWS_REGION}"
echo "State Bucket: ${BUCKET_NAME}"
echo ""

read -p "Continue with setup? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Step 1: Create S3 bucket for Terraform state
echo ""
echo "📦 Step 1: Creating S3 bucket for Terraform state..."
if aws s3 ls "s3://${BUCKET_NAME}" --profile "${AWS_PROFILE}" 2>&1 | grep -q 'NoSuchBucket'; then
    aws s3 mb "s3://${BUCKET_NAME}" --region "${AWS_REGION}" --profile "${AWS_PROFILE}"
    echo -e "${GREEN}✅ Created S3 bucket: ${BUCKET_NAME}${NC}"
else
    echo -e "${YELLOW}⚠️  Bucket ${BUCKET_NAME} already exists${NC}"
fi

# Enable versioning
echo "Enabling versioning..."
aws s3api put-bucket-versioning \
    --bucket "${BUCKET_NAME}" \
    --versioning-configuration Status=Enabled \
    --region "${AWS_REGION}" \
    --profile "${AWS_PROFILE}" 2>/dev/null || echo -e "${YELLOW}⚠️  Versioning already enabled${NC}"

# Enable encryption
echo "Enabling encryption..."
aws s3api put-bucket-encryption \
    --bucket "${BUCKET_NAME}" \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }' \
    --region "${AWS_REGION}" \
    --profile "${AWS_PROFILE}" 2>/dev/null || echo -e "${YELLOW}⚠️  Encryption already enabled${NC}"

# Block public access
echo "Blocking public access..."
aws s3api put-public-access-block \
    --bucket "${BUCKET_NAME}" \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" \
    --region "${AWS_REGION}" \
    --profile "${AWS_PROFILE}" 2>/dev/null || echo -e "${YELLOW}⚠️  Public access already blocked${NC}"

# Step 2: Create DynamoDB table for state locking
echo ""
echo "🔒 Step 2: Creating DynamoDB table for state locking..."
TABLE_NAME="predico-terraform-locks"
if aws dynamodb describe-table --table-name "${TABLE_NAME}" --region "${AWS_REGION}" --profile "${AWS_PROFILE}" --no-cli-pager &>/dev/null; then
    echo -e "${YELLOW}⚠️  Table ${TABLE_NAME} already exists${NC}"
else
    aws dynamodb create-table \
        --table-name "${TABLE_NAME}" \
        --attribute-definitions AttributeName=LockID,AttributeType=S \
        --key-schema AttributeName=LockID,KeyType=HASH \
        --billing-mode PAY_PER_REQUEST \
        --region "${AWS_REGION}" \
        --profile "${AWS_PROFILE}" \
        --no-cli-pager
    
    echo "Waiting for table to be active..."
    aws dynamodb wait table-exists --table-name "${TABLE_NAME}" --region "${AWS_REGION}" --profile "${AWS_PROFILE}"
    echo -e "${GREEN}✅ Created DynamoDB table: ${TABLE_NAME}${NC}"
fi

# Step 3: Update backend configuration files
echo ""
echo "📝 Step 3: Updating backend configuration files..."
# Get the script directory and navigate to infrastructure root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRASTRUCTURE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

for env in dev staging production; do
    BACKEND_FILE="${INFRASTRUCTURE_DIR}/terraform/envs/${env}/backend.hcl"
    if [ -f "${BACKEND_FILE}" ]; then
        # Update bucket name in backend files (match any spacing around =)
        # macOS sed requires different syntax than Linux
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s|bucket[[:space:]]*=[[:space:]]*\"predico-terraform-state\"|bucket = \"${BUCKET_NAME}\"|" "${BACKEND_FILE}"
        else
            # Linux
            sed -i "s|bucket[[:space:]]*=[[:space:]]*\"predico-terraform-state\"|bucket = \"${BUCKET_NAME}\"|" "${BACKEND_FILE}"
        fi
        echo -e "${GREEN}✅ Updated ${BACKEND_FILE}${NC}"
    else
        echo -e "${YELLOW}⚠️  File not found: ${BACKEND_FILE}${NC}"
    fi
done

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Review and update backend.hcl files if needed"
echo "2. Run: cd infrastructure/terraform"
echo "3. Initialize Terraform: terraform init -backend-config=envs/dev/backend.hcl"
echo "4. Plan: terraform plan -var-file=envs/dev/terraform.tfvars"
echo "5. Apply: terraform apply -var-file=envs/dev/terraform.tfvars"
echo ""
echo "Your AWS Account ID: ${AWS_ACCOUNT_ID}"
echo "Add this to GitHub Secrets as AWS_ACCOUNT_ID"

