# Git Hooks Setup

This project uses **Husky** and **Commitlint** to enforce commit message conventions and run pre-commit checks.

## Setup (One-time)

After cloning the repository, run:

```bash
npm install
```

This will install Husky and set up the git hooks automatically.

## Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `build`: Build system changes
- `ci`: CI/CD changes
- `chore`: Other changes (dependencies, etc.)
- `revert`: Revert a previous commit

### Examples

```bash
feat(auth): add email verification flow
fix(api): resolve database connection timeout
docs(readme): update setup instructions
chore(deps): update terraform to 1.6.0
```

### Subject Rules

- Maximum 72 characters
- Use imperative mood ("add" not "added" or "adds")
- No period at the end
- First letter lowercase

## Pre-commit Hooks

Before each commit, the following checks run automatically:

- **TypeScript/TSX files**: ESLint with auto-fix
- **Terraform files**: `terraform fmt` (formatting)

If any check fails, the commit is blocked. Fix the issues and try again.

## Commitizen (Optional)

For an interactive commit message builder:

```bash
npm run commit
```

This will guide you through creating a properly formatted commit message.

## Bypassing Hooks (Not Recommended)

If you absolutely need to bypass hooks (emergency fixes only):

```bash
git commit --no-verify -m "message"
```

⚠️ **Warning**: Only use this in emergencies. The hooks are there for a reason!

## Troubleshooting

**Hooks not running?**
```bash
npm run prepare  # Reinstall hooks
```

**Commit message rejected?**
- Check the format matches Conventional Commits
- Subject must be ≤ 72 characters
- Use one of the allowed types

**Pre-commit checks failing?**
- Fix the linting/formatting issues
- Or temporarily disable specific checks in `.lintstagedrc.json`

