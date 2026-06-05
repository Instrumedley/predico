# Installing Terraform

## macOS Installation

### Option 1: Using Homebrew (Recommended - Easiest)

```bash
# Install Homebrew if you don't have it
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Terraform
brew install terraform

# Verify installation
terraform version
```

### Option 2: Manual Installation

1. **Download Terraform:**
   - Go to: https://www.terraform.io/downloads
   - Download the macOS AMD64 or Apple Silicon version (depending on your Mac)
   - Extract the zip file

2. **Move to PATH:**
   ```bash
   # For Intel Macs
   sudo mv terraform /usr/local/bin/
   
   # For Apple Silicon Macs (M1/M2/M3)
   sudo mv terraform /opt/homebrew/bin/
   ```

3. **Verify:**
   ```bash
   terraform version
   ```

### Option 3: Using tfenv (Version Manager)

If you want to manage multiple Terraform versions:

```bash
# Install tfenv
brew install tfenv

# Install latest Terraform
tfenv install latest

# Use latest
tfenv use latest

# Verify
terraform version
```

## Verify Installation

After installation, verify it works:

```bash
terraform version
```

You should see something like:
```
Terraform v1.6.0
on darwin_amd64
```

## Requirements

- **Terraform version**: >= 1.5.0 (required by our configuration)
- **macOS**: Any recent version

## Troubleshooting

**"command not found" after installation:**
- Make sure Terraform is in your PATH
- Try: `which terraform` to see if it's found
- Restart your terminal

**"Permission denied":**
- Use `sudo` when moving files to system directories
- Or install via Homebrew (no sudo needed)

**Apple Silicon (M1/M2/M3) Macs:**
- Use Homebrew (it handles architecture automatically)
- Or download the ARM64 version manually

## Next Steps

Once Terraform is installed, continue with:

```bash
cd infrastructure/terraform
export AWS_PROFILE=predico
terraform init -backend-config=envs/dev/backend.hcl
```

