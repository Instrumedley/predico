# Git Hooks

This repository uses git hooks to enforce development workflows.

## Pre-Push Hook

The `.git/hooks/pre-push` hook prevents direct pushes to the `main` branch.

### What It Does

- ✅ **Blocks** direct pushes to `main` branch
- ✅ **Allows** pushes to all other branches (feature branches, staging, production, etc.)
- ✅ **Allows** PR merges (GitHub merges happen server-side, so the hook doesn't run)

### How It Works

When you try to push to `main`:
```bash
git push origin main
```

The hook will:
1. Detect you're on the `main` branch
2. Block the push with a helpful error message
3. Show you the correct workflow

### Setting Up (For New Clones)

If someone clones the repository, they need to set up the hook:

```bash
# The hook is in .git/hooks/ which is not tracked by git
# So you need to manually copy it or use a tool like husky

# Option 1: Manual copy (if the hook file exists in repo)
cp .githooks/pre-push .git/hooks/pre-push
chmod +x .git/hooks/pre-push

# Option 2: Use husky (if installed)
npm run prepare  # This sets up all hooks
```

### Bypassing (Not Recommended)

If you absolutely need to bypass (emergency only):

```bash
git push origin main --no-verify
```

⚠️ **Warning**: Only use in emergencies. The hook is there for a reason!

### Testing

Try pushing to main to test:
```bash
git checkout main
# Make a small change
git commit --allow-empty -m "test: testing pre-push hook"
git push origin main  # Should be blocked
```

### For Team Members

When setting up the project:
1. Clone the repository
2. Copy the hook: `cp .githooks/pre-push .git/hooks/pre-push`
3. Make it executable: `chmod +x .git/hooks/pre-push`
4. Or run `npm run prepare` if husky is set up

