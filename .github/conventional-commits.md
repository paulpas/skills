# Conventional Commits Configuration

This document defines the conventional commits format used across this repository for automated changelog generation, version bumping, and release automation.

## Overview

We use the [Conventional Commits](https://www.conventionalcommits.org) specification to standardize commit messages. This enables:

- Automatic version bumping (MAJOR.MINOR.PATCH)
- Automated changelog generation
- Easier commit message review
- Consistent commit history

## Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

### Format Breakdown

```
feat(auth): add two-factor authentication

- Implement TOTP-based 2FA
- Update user settings UI
- Add 2FA recovery codes

Fixes: #123
```

| Part | Required | Description |
|------|----------|-------------|
| `type` | Yes | Type of change |
| `scope` | Optional | Scope of the change (file, module, component) |
| `description` | Yes | Short summary of the change |
| `body` | Optional | Detailed explanation |
| `footer` | Optional | Breaking changes, issue references |

## Commit Types

| Type | Description | Version Bump | Example |
|------|-------------|--------------|---------|
| `feat` | New feature | MINOR | `feat(api): add user profile endpoint` |
| `fix` | Bug fix | PATCH | `fix(api): handle null responses` |
| `docs` | Documentation only | None | `docs(readme): update installation guide` |
| `style` | Code formatting (no logic) | None | `style: format code with prettier` |
| `refactor` | Code refactoring | None | `refactor(auth): simplify login logic` |
| `perf` | Performance improvement | PATCH | `perf(api): optimize database queries` |
| `test` | Test additions/changes | None | `test(auth): add login tests` |
| `chore` | Build, deps, tooling | None | `chore: update dependencies` |
| `build` | Build system changes | None | `build: update webpack config` |
| `ci` | CI configuration | None | `ci: add GitHub Actions workflow` |
| `revert` | Revert previous commit | Depends | `revert: feat(auth): remove oauth` |

## Scope Guidelines

Use scope to indicate which part of the codebase was changed:

| Scope | Description |
|-------|-------------|
| `api` | API endpoints and controllers |
| `auth` | Authentication and authorization |
| `db` | Database models and migrations |
| `ui` | User interface components |
| `utils` | Utility functions and helpers |
| `config` | Configuration files |
| `deps` | Dependencies and packages |
| `test` | Test files and setup |
| `ci` | CI/CD pipelines |

## Breaking Changes

Breaking changes must be clearly indicated in the commit message:

### Method 1: Footer Notation

```
feat(api): change response format

BREAKING CHANGE: response structure changed from {id, name} to {identifier, full_name}
```

### Method 2: Exclamation Mark

```
feat(api)!: change response format
```

### Method 3: Type with Exclamation

```
feat!: remove deprecated authentication method
```

## Examples

### Feature Commit (MINOR)

```
feat(auth): add two-factor authentication support

- Implement TOTP-based 2FA
- Update user settings UI
- Add 2FA recovery codes

Closes: #456
```

### Bug Fix Commit (PATCH)

```
fix(api): handle null responses in payment gateway

- Add null check for payment provider responses
- Return fallback error message
- Add test coverage for null responses

Fixes: #789
```

### Documentation Commit (No Version Bump)

```
docs(readme): improve installation instructions

- Add step-by-step guide
- Include common issues
- Link to troubleshooting

Reviewed-by: @team-member
```

### Refactoring Commit (No Version Bump)

```
refactor(auth): simplify login logic

- Extract validation to separate function
- Remove nested conditionals
- Add JSDoc comments

Performance: 15% faster login validation
```

### Breaking Change Commit (MAJOR)

```
feat(api)!: change authentication header format

BREAKING CHANGE: Authorization header changed from 'Bearer token' to 'Token token'

Migration: Update all clients to use new header format
```

### Changelog Skipping

```
chore: update lockfile

#skip-changelog
```

## Commit Message Hooks

### Pre-commit Hook

A pre-commit hook validates commit messages against the conventional commits format. If the commit message doesn't match the expected format, the commit will be rejected with helpful error messages.

### Commit Message Template

The repository includes a commit message template:

```bash
# Configure git to use the template
git config commit.template .gitmessage

# Or for this repository only
export GIT_EDITOR="sed '1s/^/feat: /' "
```

## CI/CD Integration

### Commit Linting Job

```yaml
jobs:
  lint-commits:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: wagoid/commitlint-github-action@v5
        with:
          configFile: .commitlintrc.json
```

### Automated Version Bumping

When commits are merged to `main`, semantic-release analyzes commit messages and automatically:

1. Determines the version bump (MAJOR, MINOR, or PATCH)
2. Updates `package.json` version
3. Generates changelog from commits
4. Creates Git tag (v1.2.3)
5. Publishes to npm (if configured)

### Semantic-Release Configuration

```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    "@semantic-release/npm",
    "@semantic-release/github"
  ]
}
```

## Common Patterns

### Multi-Part Changes

For large features with multiple commits:

```
feat(auth): add two-factor authentication

Initial commit for 2FA support

feat(auth): add 2FA UI components
feat(auth): integrate TOTP validation
fix(auth): handle 2FA reset flow
test(auth): add 2FA test suite
```

### Revert Commits

```
revert: feat(api): remove deprecated endpoint

This reverts commit abc123.
Reason: endpoint needs to stay for backward compatibility
```

### Merge Commits (Auto-generated)

When merging pull requests, use squash merge or rebase merge to maintain clean history. The pull request title and description become the commit message.

## Tooling

### Commitlint

Install commitlint to enforce commit message format:

```bash
# Install dependencies
npm install --save-dev @commitlint/{config-conventional,cli}

# Configure commitlint
echo "module.exports = { extends: ['@commitlint/config-conventional'] }" > commitlint.config.js
```

### Husky Hook

```bash
# Add pre-commit hook
npx husky add .husky/commit-msg 'npx commitlint --edit "$1"'
```

## Related Documentation

- [Branching Strategy](./branching-strategy.md) - Git branching model
- [Semantic Versioning](https://semver.org) - Version number specification
- [Changelog Generation](https://github.com/conventional-changelog) - Changelog automation
