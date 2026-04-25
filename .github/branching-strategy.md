# Trunk-Based Development with Feature Flags

This document defines the trunk-based development branching strategy with feature flags for this repository.

## Overview

We use **Trunk-Based Development** with **Feature Flags** as our primary branching strategy. This enables:

- Continuous deployment to production
- Fast feedback cycles
- Minimal merge conflicts
- Progressive delivery of features

## Core Principles

1. **Mainline Development**: All developers commit directly to `main` (trunk)
2. **Short Branch Lifetimes**: Feature branches exist for hours/days, never weeks
3. **Feature Flags**: Incomplete features are hidden behind feature flags
4. **Small Commits**: Frequent, atomic commits to `main`

## Branching Model

```
main    ●───●───●───●───●───●───●───●
        │   │   │   │   │   │   │   │
        │   │   │   │   │   │   │   └─ Feature E (feature flag)
        │   │   │   │   │   │   └───── Feature D (feature flag)
        │   │   │   │   │   └───────── Feature C (feature flag)
        │   │   │   │   └───────────── Feature B (feature flag)
        │   │   │   └───────────────── Feature A (feature flag)
        │   │   └───────────────────── Hotfix (from main)
        │   └───────────────────────── Release (from main)
        └───────────────────────────── Release (from main)
```

## Branch Types

### `main` (Trunk)
- **Purpose**: Production-ready code
- **Status**: Always deployable
- **Protection**: Requires CI/CD passes and code review
- **Commits**: Direct commits or PRs from feature branches

### Feature Branches (Optional)
- **Pattern**: `feature/<description>` or `feat/<description>`
- **Lifetime**: 1-3 days maximum
- **Usage**: For larger changes that benefit from isolation
- **Merge**: Merge to `main` with feature flag enabled/disabled

### Hotfix Branches
- **Pattern**: `hotfix/<description>`
- **Source**: Create from `main`
- **Purpose**: Critical production fixes
- **Merge**: Merge directly to `main` and tag immediately

## Feature Flag Strategy

### Flag Lifecycle

```
1. Add flag with default: false
2. Deploy with flag hidden
3. Enable flag for testing
4. Enable flag for all users
5. Remove flag after verification
```

### Flag Implementation

```typescript
// config/features.ts
export interface FeatureFlags {
  newDashboard: boolean;
  darkMode: boolean;
  betaApi: boolean;
}

export const featureFlags: FeatureFlags = {
  newDashboard: process.env.FEATURE_NEW_DASHBOARD === 'true' || false,
  darkMode: process.env.FEATURE_DARK_MODE === 'true' || false,
  betaApi: process.env.FEATURE_BETA_API === 'true' || false,
};

// Usage in code
if (featureFlags.newDashboard) {
  renderNewDashboard();
} else {
  renderLegacyDashboard();
}
```

### Flag Types

| Type | Purpose | Duration |
|------|---------|----------|
| **Release Flags** | Hide incomplete features until release | Days/weeks |
| **Canary Flags** | Roll out to subset of users | Weeks |
| **Experiment Flags** | A/B testing and experiments | Days/weeks |
| **Kill Switches** | Emergency feature disabling | Anytime |

## Development Workflow

### Small Changes (Direct to Main)

```bash
# 1. Pull latest main
git checkout main
git pull origin main

# 2. Make changes and commit
git commit -m "fix: correct typo in documentation"

# 3. Push directly to main
git push origin main
```

### Large Features (Feature Branch)

```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/payment-integration

# 2. Work on feature with feature flag
git commit -m "feat: add payment API client"
git commit -m "feat: add feature flag for payments"
git commit -m "feat: integrate payment API behind flag"

# 3. Push and create PR
git push origin feature/payment-integration
# Open PR for review

# 4. Merge to main
git checkout main
git pull origin main
git merge feature/payment-integration
git push origin main

# 5. Enable feature flag in production
# Update environment variables or database flags
```

### Hotfix Workflow

```bash
# 1. Create hotfix from main
git checkout main
git pull origin main
git checkout -b hotfix/security-patch

# 2. Fix the issue
git commit -m "fix: security vulnerability in authentication"

# 3. Merge to main immediately
git checkout main
git pull origin main
git merge hotfix/security-patch
git push origin main

# 4. Create release tag
git tag -a v1.2.1 -m "Version 1.2.1 - Security Patch"
git push origin v1.2.1
```

## CI/CD Integration

### Main Branch Pipeline

```yaml
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test
      - run: npm run lint
      
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./deploy.sh production
```

### Feature Flag Testing

```yaml
jobs:
  test-with-features:
    strategy:
      matrix:
        feature_flags: ['FEATURE_FLAG=0', 'FEATURE_FLAG=1']
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test
        env:
          FEATURE_FLAG: ${{ matrix.feature_flags }}
```

## Code Review Requirements

### Pull Requests to Main

- **Mandatory**: At least one approval from a team member
- **Tests**: All tests must pass (100% coverage required for new code)
- **Linting**: No linting errors
- **Feature Flags**: All new features must include feature flags
- **Documentation**: Updated for any public API changes

### Commit Message Requirements

Use conventional commits format:

```
<type>(<scope>): <description>

[optional body]

[optional footer with BREAKING CHANGE]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

## Rollback Strategy

### Feature Flag Rollback

```bash
# Disable problematic feature
export FEATURE_NEW_DASHBOARD=false

# Or update feature flags in configuration
# Restart services
```

### Code Rollback

```bash
# Find problematic commit
git log --oneline

# Revert specific commit
git revert <commit-hash>

# Push to main
git push origin main
```

## Monitoring and Analytics

### Feature Flag Metrics

- Enablement rate for each feature
- Performance impact of flagged features
- User feedback on new features
- Error rates with features enabled

### Kill Switches

All production services must have a kill switch for:
- New feature flags
- New API endpoints
- Database migrations
- External service integrations

## Advantages of This Strategy

| Benefit | Description |
|---------|-------------|
| **Fast Feedback** | Changes reach production quickly |
| **Small Changes** | Easier to debug and test |
| **No Merge Hell** | Minimal conflicts with short-lived branches |
| **Continuous Deployment** | Every commit to main is a release candidate |
| **Safe Rollbacks** | Feature flags enable instant rollback |
| **Team Autonomy** | Developers work independently on main |

## When to Use Alternative Strategies

| Scenario | Recommended Strategy |
|----------|---------------------|
| Large team with complex releases | Git Flow |
| Monthly release cadence | Git Flow |
| Scheduled releases | Release Branching |
| Multi-version support | Git Flow |

## Related Documentation

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [RELEASING.md](../RELEASING.md) - Release process
- [conventional-commits.md](./conventional-commits.md) - Commit message format
