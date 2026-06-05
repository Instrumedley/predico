# Updating Terraform

## Update via Homebrew (Recommended)

Since you installed via Homebrew, update it the same way:

```bash
# First, update Homebrew itself
brew update

# Then upgrade Terraform
brew upgrade terraform

# Verify the new version
terraform version
```

## If Homebrew Version is Still Old

Sometimes Homebrew formulas lag behind. You can:

### Option 1: Use Homebrew Tap (Latest Version)

```bash
# Add HashiCorp tap (official source)
brew tap hashicorp/tap

# Install/upgrade from tap
brew install hashicorp/tap/terraform

# Or upgrade if already installed
brew upgrade hashicorp/tap/terraform
```

### Option 2: Check Homebrew Formula

```bash
# Check what version Homebrew has
brew info terraform

# If it's outdated, you might need to wait for Homebrew to update
# Or use the tap method above
```

## Important Note

**Your current version (1.5.7) is actually fine!** 

Our Terraform configuration requires `>= 1.5.0`, and 1.5.7 meets that requirement. The warning is just informational - you don't *need* to update right now.

However, if you want the latest features and security updates, updating is recommended.

## After Updating

Verify it works:
```bash
terraform version
```

Then continue with your deployment:
```bash
cd infrastructure/terraform
export AWS_PROFILE=predico
terraform init -backend-config=envs/dev/backend.hcl
```

## Troubleshooting

**"brew: command not found"**
- Homebrew might not be in your PATH
- Try: `/opt/homebrew/bin/brew` (Apple Silicon) or `/usr/local/bin/brew` (Intel)

**Still getting old version after update**
- Try: `brew uninstall terraform && brew install terraform`
- Or use the HashiCorp tap method above

