# Terraform backend configuration for remote state
# This file should be configured per environment

terraform {
  backend "s3" {
    # This will be overridden by backend config files
    # See infrastructure/terraform/envs/ directory
    bucket         = "predico-terraform-state"
    key            = "terraform.tfstate"
    region         = "eu-north-1"  # Stockholm, Sweden
    encrypt        = true
    dynamodb_table = "predico-terraform-locks"
  }
}

