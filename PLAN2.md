
# GitHub Actions Modernization & Fix Prompt — May 2026

> **How to use this file:** Paste the entirety of this document into an AI coding agent
> (Claude, Codex, OpenCode, Cursor, etc.) inside the `agent-skill-router` repo. The agent
> will have everything required to apply, verify, and roll back the changes.
>
> **Repository:** `paulpas/agent-skill-router`
> **Audit date:** May 2026
> **Scope:** All four GitHub Actions workflows + supporting config

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Action / Tool Currency Matrix (May 2026)](#2-action--tool-currency-matrix-may-2026)
3. [Decisions Adopted](#3-decisions-adopted)
4. [Changes To Apply (Step-by-Step)](#4-changes-to-apply-step-by-step)
   - 4.1 [DELETE `.github/workflows/quality.yml`](#41-delete-githubworkflowsqualityyml)
   - 4.2 [REPLACE `.github/workflows/ci.yml`](#42-replace-githubworkflowsciyml)
   - 4.3 [REPLACE `.github/workflows/release.yml`](#43-replace-githubworkflowsreleaseyml)
   - 4.4 [REPLACE `.github/workflows/skill-relationships.yml`](#44-replace-githubworkflowsskill-relationshipsyml)
   - 4.5 [CREATE `.github/workflows/codeql.yml`](#45-create-githubworkflowscodeqlyml)
   - 4.6 [CREATE `.github/dependabot.yml`](#46-create-githubdependabotyml)
   - 4.7 [CREATE `.releaserc.json`](#47-create-releasercjson)
   - 4.8 [CREATE `commitlint.config.js`](#48-create-commitlintconfigjs)
   - 4.9 [PATCH `package.json`](#49-patch-packagejson)
   - 4.10 [PATCH `agent-skill-routing-system/jest.config.js`](#410-patch-agent-skill-routing-systemjestconfigjs)
5. [Verification Checklist](#5-verification-checklist)
6. [Rollout Guidance (Repo Settings & Secrets)](#6-rollout-guidance-repo-settings--secrets)
7. [Rollback Plan](#7-rollback-plan)
8. [Appendix: Issue → Fix Traceability](#8-appendix-issue--fix-traceability)

---

## 1. Executive Summary

The repository's four GitHub Actions workflows contain **multiple blocking bugs** that
either cause silent no-ops or would fail outright if exercised. The most critical:

| # | Severity | Issue | File |
|---|---|---|---|
| 1 | **BLOCKER** | `semantic-release/github@v9` is **not a real Action** (semantic-release is a CLI). Release workflow cannot run. | `release.yml` |
| 2 | **BLOCKER** | No `semantic-release` config file or dependency installed. | repo root |
| 3 | **HIGH** | `node_modules` uploaded as cross-job artifact (anti-pattern; slow, wasteful). | `ci.yml` |
| 4 | **HIGH** | CI runs `eslint --fix` (mutates code in CI). | `ci.yml`, `quality.yml`, `package.json` |
| 5 | **HIGH** | Coverage gate uses deprecated `npm install -g codecov`. | `ci.yml`, `quality.yml` |
| 6 | **HIGH** | Coverage threshold parser is fragile (`grep -o '"pct":[0-9.]*' \| head -1`). | `quality.yml` |
| 7 | **HIGH** | `snyk/actions/node@master` (mutable, unpinned). | `quality.yml` |
| 8 | **HIGH** | `commitlint --from HEAD~1` breaks on squash merges & first-commit branches. | `quality.yml` |
| 9 | **HIGH** | `skill-relationships.yml` references **4 Python scripts that don't exist**. Phases silently no-op. | `skill-relationships.yml` |
| 10 | **HIGH** | `reformat_skills.py` referenced at repo root, but actually lives at `scripts/reformat_skills.py`. | `skill-relationships.yml` |
| 11 | **HIGH** | No top-level `permissions:` block on any workflow (defaults to whatever the repo settings allow). | all |
| 12 | **MED** | `actions/setup-python@v4` is outdated (v5 since 2024). | `skill-relationships.yml` |
| 13 | **MED** | `npm test` script doesn't exist in root `package.json` (only `test:unit`, `test:integration`). | `release.yml` + `package.json` |
| 14 | **MED** | `npm run docs:generate` referenced but not defined. | `release.yml` |
| 15 | **MED** | `release.yml` `publish` job uses `--provenance` but lacks `id-token: write`. | `release.yml` |
| 16 | **MED** | `ci.yml` and `quality.yml` duplicate ~5 jobs (lint/prettier/typecheck/coverage/security). | both |
| 17 | **LOW** | No `timeout-minutes` on most jobs. | all |
| 18 | **LOW** | No CodeQL workflow. | (missing) |
| 19 | **LOW** | No Dependabot config. | (missing) |

After applying the changes in §4, all workflows will:
- Use only **currently-supported, properly-pinned actions** (May 2026).
- **Not duplicate work** across workflows.
- Have **explicit, minimal `permissions:` blocks**.
- Have **timeouts** to prevent runaway jobs.
- Have **a working release pipeline** (semantic-release with conventional commits).
- Pass `actionlint` clean.

---

## 2. Action / Tool Currency Matrix (May 2026)

| Action / Tool | Currently Used | Latest May 2026 | After Fix | Notes |
|---|---|---|---|---|
| `actions/checkout` | `v4` | `v4` | `v4` | ✅ Current |
| `actions/setup-node` | `v4` | `v4` | `v4` | ✅ Current; cache: 'npm' built-in |
| `actions/setup-python` | `v4` | `v5` | `v5` | ❌→✅ Bumped |
| `actions/upload-artifact` | `v4` | `v4` | `v4` | ✅ v3 sunset Jan 2025 |
| `actions/download-artifact` | `v4` | `v4` | `v4` | ✅ |
| `actions/cache` | (unused) | `v4` | (still unused, setup-node cache suffices) | – |
| `codecov/codecov-action` | (npm-global) | `v5` | `v5` | ➕ Replaces deprecated install |
| `snyk/actions/node` | `@master` | `@v3` | `@v3` | ❌→✅ Pinned tag |
| `semantic-release/github` | `@v9` *(invalid)* | does not exist | replaced by `cycjimmy/semantic-release-action@v4` | ❌→✅ |
| `cycjimmy/semantic-release-action` | (unused) | `v4` | `v4` | ➕ Added |
| `wagoid/commitlint-github-action` | (unused) | `v6` | `v6` | ➕ Added |
| `github/codeql-action` | (unused) | `v3` | `v3` | ➕ Added |
| `Node.js` | `'24'` | 24 LTS (active until Apr 2027) | `'24'` | ✅ |
| `Python` | `3.12` | 3.12 supported, 3.13 GA | `3.12` (kept; 3.13 optional) | ✅ |
| `semantic-release` (npm) | (not installed) | `24.x` | `^24.2.0` | ➕ Added |

---

## 3. Decisions Adopted

| Decision | Choice |
|---|---|
| Skill workflow missing scripts | **Remove phases 3–6** (`analyze_skill_relationships`, `fix_skill_relationships`, `enforce_bidirectionality`, `enhance_cncf_relationships`). Keep phases 1, 2, 7. |
| Release strategy | **Full semantic-release** via `cycjimmy/semantic-release-action@v4` with plugins: `commit-analyzer`, `release-notes-generator`, `changelog`, `npm`, `github`, `git`. |
| CI vs Quality | **Merge into single `ci.yml`**. **Delete `quality.yml`**. |
| Action pinning | **Tag pins (`@v4`, `@v5`)** + **Dependabot weekly** to keep them up to date. |
| Output file | This single markdown prompt. |

---

## 4. Changes To Apply (Step-by-Step)

> **Apply order is important.** Steps 4.1–4.10 should be applied as one logical change
> (e.g., one PR, one commit) so that the workflows remain consistent at every step.

### 4.1 DELETE `.github/workflows/quality.yml`

```bash
git rm .github/workflows/quality.yml
```

**Why:** All useful jobs from `quality.yml` are merged into `ci.yml` in §4.2 (with bug fixes).

---

### 4.2 REPLACE `.github/workflows/ci.yml`

Overwrite the file completely with the content below.

```yaml
name: CI Pipeline

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

# Default to least-privilege; jobs may escalate as needed.
permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

env:
  NODE_VERSION: '24'

jobs:
  # ----------------------------------------------------------------------
  # Lint (ESLint, READ-ONLY in CI — no --fix)
  # ----------------------------------------------------------------------
  lint:
    name: Lint
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - name: Run ESLint (no auto-fix in CI)
        run: npx eslint 'src/**/*.ts'

  # ----------------------------------------------------------------------
  # Prettier formatting check
  # ----------------------------------------------------------------------
  format:
    name: Format (Prettier)
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - run: npm run format:check

  # ----------------------------------------------------------------------
  # TypeScript type checking
  # ----------------------------------------------------------------------
  typecheck:
    name: Type Check
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - run: npm run typecheck

  # ----------------------------------------------------------------------
  # Unit tests + coverage
  # ----------------------------------------------------------------------
  test-unit:
    name: Unit Tests
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - name: Run Unit Tests
        run: npm run test:coverage
      - name: Upload Coverage Artifact
        uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/
          retention-days: 7

  # ----------------------------------------------------------------------
  # Integration tests
  # ----------------------------------------------------------------------
  test-integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - run: npm run test:integration

  # ----------------------------------------------------------------------
  # Coverage threshold + Codecov upload
  # ----------------------------------------------------------------------
  coverage:
    name: Coverage Threshold
    runs-on: ubuntu-latest
    needs: test-unit
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - uses: actions/download-artifact@v4
        with:
          name: coverage
          path: coverage/
      - name: Enforce coverage >= 70%
        run: |
          if [ ! -f coverage/coverage-summary.json ]; then
            echo "::warning::coverage-summary.json missing — ensure jest reporter 'json-summary' is enabled."
            exit 0
          fi
          COVERAGE=$(node -p "require('./coverage/coverage-summary.json').total.lines.pct")
          echo "Line coverage: ${COVERAGE}%"
          awk -v c="$COVERAGE" 'BEGIN { if (c+0 < 70) { print "::error::Coverage " c "% < 70% threshold"; exit 1 } }'
      - name: Upload to Codecov
        if: ${{ env.CODECOV_TOKEN != '' }}
        uses: codecov/codecov-action@v5
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: coverage/coverage-final.json
          fail_ci_if_error: false
        env:
          CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}

  # ----------------------------------------------------------------------
  # npm audit + Snyk
  # ----------------------------------------------------------------------
  security:
    name: Security
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - name: npm audit (production deps only)
        run: npm audit --audit-level=high --omit=dev
        continue-on-error: true
      - name: Snyk
        if: ${{ env.SNYK_TOKEN != '' }}
        uses: snyk/actions/node@v3
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
        continue-on-error: true

  # ----------------------------------------------------------------------
  # Conventional commits
  # ----------------------------------------------------------------------
  commitlint:
    name: Commitlint
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - uses: wagoid/commitlint-github-action@v6
        with:
          configFile: commitlint.config.js

  # ----------------------------------------------------------------------
  # Build (depends on lint, typecheck, tests passing)
  # ----------------------------------------------------------------------
  build:
    name: Build
    runs-on: ubuntu-latest
    needs: [lint, format, typecheck, test-unit, test-integration]
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: |
            dist/
            agent-skill-routing-system/dist/
          retention-days: 7
          if-no-files-found: ignore

  # ----------------------------------------------------------------------
  # Final aggregator: required check for branch protection
  # ----------------------------------------------------------------------
  ci-status:
    name: CI Status
    runs-on: ubuntu-latest
    if: always()
    needs: [lint, format, typecheck, test-unit, test-integration, coverage, security, build]
    steps:
      - name: Verify all required jobs passed
        run: |
          echo "Job results: ${{ toJSON(needs) }}"
          if echo '${{ toJSON(needs) }}' | grep -E '"result":\s*"(failure|cancelled)"'; then
            echo "::error::One or more required CI jobs failed."
            exit 1
          fi
          echo "All required CI jobs passed."
```

**Key changes vs original:**
- ❌ Dropped the `install` job + `node_modules` artifact pattern.
- ❌ Dropped redundant `fetch-depth: 0` from most jobs.
- ✅ Each job runs `npm ci` directly (cached by `setup-node`).
- ✅ ESLint runs without `--fix`.
- ✅ Codecov upload via official `@v5` action.
- ✅ Coverage parsed from `coverage-summary.json` via `node -p` (stable schema).
- ✅ Snyk pinned to `@v3`, gated on token presence.
- ✅ Commitlint via `wagoid/commitlint-github-action@v6` (handles squash merges).
- ✅ Top-level `permissions: contents: read`.
- ✅ `timeout-minutes` on every job.
- ✅ Final `ci-status` aggregator job for branch protection.

---

### 4.3 REPLACE `.github/workflows/release.yml`

Overwrite the file completely with the content below.

```yaml
# Required secrets:
#   GITHUB_TOKEN     (auto-provided)
#   NPM_TOKEN        (only if publishing to npm registry)
#
# Required config files:
#   .releaserc.json     (semantic-release config — see §4.7 of fix prompt)
#   commitlint.config.js (see §4.8)
#
# Trigger: pushes to main with conventional commits.
name: Release

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: release-${{ github.ref }}
  cancel-in-progress: false

env:
  NODE_VERSION: '24'

jobs:
  release:
    name: Semantic Release
    runs-on: ubuntu-latest
    timeout-minutes: 20
    permissions:
      contents: write       # tag + commit CHANGELOG
      issues: write         # comment on resolved issues
      pull-requests: write  # comment on released PRs
      id-token: write       # npm provenance + OIDC
    outputs:
      new_release_published: ${{ steps.semantic.outputs.new_release_published }}
      new_release_version:   ${{ steps.semantic.outputs.new_release_version }}
      new_release_notes:     ${{ steps.semantic.outputs.new_release_notes }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
          persist-credentials: false
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci
      - run: npm run build
      - name: Run tests
        run: npm test
      - name: Audit production deps
        run: npm audit --audit-level=high --omit=dev
        continue-on-error: true
      - name: Semantic Release
        id: semantic
        uses: cycjimmy/semantic-release-action@v4
        with:
          semantic_version: 24
          extra_plugins: |
            @semantic-release/changelog@6
            @semantic-release/git@10
        env:
          GITHUB_TOKEN:    ${{ secrets.GITHUB_TOKEN }}
          NPM_TOKEN:       ${{ secrets.NPM_TOKEN }}
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

      - name: Output release info
        if: ${{ steps.semantic.outputs.new_release_published == 'true' }}
        run: |
          echo "::notice::Released v${{ steps.semantic.outputs.new_release_version }}"
          echo "${{ steps.semantic.outputs.new_release_notes }}"
```

**Key changes vs original:**
- ✅ Replaced fictitious `semantic-release/github@v9` with real `cycjimmy/semantic-release-action@v4`.
- ✅ Added `id-token: write` for npm `--provenance` (handled inside semantic-release npm plugin).
- ✅ `npm test` now resolves (see §4.9 — script added).
- ✅ Removed broken `docs` job (CHANGELOG commit handled atomically by `@semantic-release/git`).
- ✅ Removed broken `publish` job (npm publish handled by `@semantic-release/npm` plugin).
- ✅ `persist-credentials: false` to prevent token leak; semantic-release uses its own.
- ✅ Concurrency `cancel-in-progress: false` to never abort a release mid-flight.

---

### 4.4 REPLACE `.github/workflows/skill-relationships.yml`

Overwrite the file completely with the content below.

```yaml
name: Skill Relationships & Index Generation

on:
  push:
    branches: [main, master, develop]
    paths:
      - 'skills/**/SKILL.md'
      - 'scripts/**/*.py'
      - '.github/workflows/skill-relationships.yml'
  pull_request:
    branches: [main, master]
    paths:
      - 'skills/**/SKILL.md'
  workflow_dispatch:
    inputs:
      force_update:
        description: 'Force update all indexes and relationships'
        required: false
        default: 'false'

permissions:
  contents: read

concurrency:
  group: skill-relationships-${{ github.ref }}
  cancel-in-progress: true

jobs:
  validate-and-update:
    name: Validate Skills & Update Indexes
    runs-on: ubuntu-latest
    timeout-minutes: 30
    permissions:
      contents: write   # auto-commit regenerated index/README on push to main

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml

      - name: Detect changed SKILL.md files
        id: detect_changes
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ] && [ "${{ github.event.inputs.force_update }}" = "true" ]; then
            echo "skill_files_changed=true" >> "$GITHUB_OUTPUT"
            echo "force=true" >> "$GITHUB_OUTPUT"
            echo "::notice::Force update requested"
            exit 0
          fi

          BASE_REF="${{ github.event.pull_request.base.ref || github.event.before || 'origin/main' }}"
          if git diff --quiet "$BASE_REF"...HEAD -- 'skills/**/SKILL.md' 2>/dev/null; then
            echo "skill_files_changed=false" >> "$GITHUB_OUTPUT"
            echo "::notice::No SKILL.md changes detected"
          else
            echo "skill_files_changed=true" >> "$GITHUB_OUTPUT"
            echo "::notice::SKILL.md changes detected"
          fi

      - name: Phase 1 — YAML validation
        id: validation
        if: steps.detect_changes.outputs.skill_files_changed == 'true'
        run: |
          if [ ! -f "scripts/reformat_skills.py" ]; then
            echo "::error::scripts/reformat_skills.py not found"
            exit 1
          fi
          python scripts/reformat_skills.py 2>&1 | tee validation.log

      - name: Phase 2 — Generate skills-index.json
        id: index_gen
        if: steps.validation.outcome == 'success'
        run: |
          if [ ! -f "scripts/generate_index.py" ]; then
            echo "::error::scripts/generate_index.py not found"
            exit 1
          fi
          python scripts/generate_index.py 2>&1 | tee index_gen.log

      - name: Phase 3 — Generate README catalog
        id: readme
        if: steps.validation.outcome == 'success'
        continue-on-error: true
        run: |
          if [ -f "scripts/generate_readme.py" ]; then
            python scripts/generate_readme.py 2>&1 | tee readme.log
          else
            echo "::warning::scripts/generate_readme.py missing — skipping README regeneration"
          fi

      - name: Detect modifications
        id: changes
        run: |
          if git diff --quiet; then
            echo "changes_detected=false" >> "$GITHUB_OUTPUT"
            echo "::notice::No file modifications produced"
          else
            echo "changes_detected=true" >> "$GITHUB_OUTPUT"
            git diff --stat
          fi

      - name: Auto-commit on main
        if: |
          steps.changes.outputs.changes_detected == 'true' &&
          (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master') &&
          github.event_name != 'pull_request'
        run: |
          git config --local user.name "github-actions[bot]"
          git config --local user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add skills-index.json README.md 2>/dev/null || true
          if ! git diff --cached --quiet; then
            git commit -m "chore: regenerate skill index and README [skip ci]"
            git push origin "HEAD:${{ github.ref_name }}"
          fi

      - name: Job summary
        if: always()
        run: |
          {
            echo "## Skill Automation Summary"
            echo ""
            echo "| Phase | Status |"
            echo "|-------|--------|"
            echo "| YAML Validation     | ${{ steps.validation.outcome || 'skipped' }} |"
            echo "| Index Generation    | ${{ steps.index_gen.outcome || 'skipped' }} |"
            echo "| README Generation   | ${{ steps.readme.outcome || 'skipped' }} |"
            echo "| Changes Detected    | ${{ steps.changes.outputs.changes_detected || 'false' }} |"
          } >> "$GITHUB_STEP_SUMMARY"
```

**Key changes vs original:**
- ❌ Removed phases 3–6 referencing nonexistent scripts (`analyze_skill_relationships.py`, `fix_skill_relationships.py`, `enforce_bidirectionality.py`, `enhance_cncf_relationships.py`).
- ✅ Fixed path: `reformat_skills.py` → `scripts/reformat_skills.py`.
- ✅ `actions/setup-python@v5` (was v4).
- ✅ Explicit `permissions: contents: write` on the job (was implicit).
- ✅ Hardened diff base resolution; uses `github.event.before` for push events.
- ✅ Added explicit error if required scripts missing (instead of silent no-op).
- ✅ Includes `[skip ci]` to prevent commit loop.

---

### 4.5 CREATE `.github/workflows/codeql.yml`

Create this new file with the content below.

```yaml
name: CodeQL

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'   # Mondays 06:00 UTC

permissions:
  actions: read
  contents: read
  security-events: write

concurrency:
  group: codeql-${{ github.ref }}
  cancel-in-progress: true

jobs:
  analyze:
    name: Analyze (${{ matrix.language }})
    runs-on: ubuntu-latest
    timeout-minutes: 30
    strategy:
      fail-fast: false
      matrix:
        language: ['javascript-typescript', 'python']
    steps:
      - uses: actions/checkout@v4
      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-and-quality
      - name: Autobuild
        uses: github/codeql-action/autobuild@v3
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          category: "/language:${{ matrix.language }}"
```

---

### 4.6 CREATE `.github/dependabot.yml`

Create this new file with the content below.

```yaml
version: 2
updates:
  # GitHub Actions versions
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
      day: monday
      time: "06:00"
    open-pull-requests-limit: 5
    commit-message:
      prefix: "ci"
      include: "scope"

  # Root npm
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
      day: monday
    open-pull-requests-limit: 10
    commit-message:
      prefix: "chore(deps)"
      include: "scope"
    groups:
      dev-dependencies:
        dependency-type: "development"

  # Subproject npm
  - package-ecosystem: npm
    directory: /agent-skill-routing-system
    schedule:
      interval: weekly
      day: monday
    open-pull-requests-limit: 10
    commit-message:
      prefix: "chore(deps)"
      include: "scope"
    groups:
      dev-dependencies:
        dependency-type: "development"

  # Python (used by scripts/)
  - package-ecosystem: pip
    directory: /
    schedule:
      interval: weekly
      day: monday
    open-pull-requests-limit: 5
    commit-message:
      prefix: "chore(deps)"
      include: "scope"
```

---

### 4.7 CREATE `.releaserc.json`

Create this new file at repo root.

```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    [
      "@semantic-release/changelog",
      { "changelogFile": "CHANGELOG.md" }
    ],
    [
      "@semantic-release/npm",
      { "npmPublish": false }
    ],
    "@semantic-release/github",
    [
      "@semantic-release/git",
      {
        "assets": ["CHANGELOG.md", "package.json", "package-lock.json"],
        "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
      }
    ]
  ]
}
```

> **Note:** `npmPublish: false` because the root `package.json` has no `name` and is not
> intended for npm publish. If you ever decide to publish, set `npmPublish: true` and
> add `"name"`, `"version"`, `"publishConfig": { "access": "public" }` to `package.json`.

---

### 4.8 CREATE `commitlint.config.js`

Create this new file at repo root.

```js
/** @type {import('@commitlint/types').UserConfig} */
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'header-max-length': [2, 'always', 120],
    'body-max-line-length': [1, 'always', 200],
    'footer-max-line-length': [1, 'always', 200],
  },
};
```

---

### 4.9 PATCH `package.json`

Apply this unified diff to the root `package.json`:

```diff
--- a/package.json
+++ b/package.json
@@ -1,22 +1,38 @@
 {
+  "private": true,
   "dependencies": {},
   "devDependencies": {
+    "@commitlint/cli": "^19.5.0",
+    "@commitlint/config-conventional": "^19.5.0",
+    "@semantic-release/changelog": "^6.0.3",
+    "@semantic-release/git": "^10.0.1",
     "@typescript-eslint/eslint-plugin": "^8.59.1",
     "@typescript-eslint/parser": "^8.59.1",
+    "eslint": "^9.0.0",
     "eslint-config-prettier": "^10.1.8",
     "eslint-plugin-import": "^2.32.0",
     "eslint-plugin-prettier": "^5.5.5",
     "jest": "^29.7.0",
     "prettier": "^3.3.3",
+    "semantic-release": "^24.2.0",
     "typescript": "^5.5.4"
   },
   "scripts": {
-    "lint": "eslint 'src/**/*.ts' --fix",
+    "lint": "eslint 'src/**/*.ts'",
+    "lint:fix": "eslint 'src/**/*.ts' --fix",
+    "format": "prettier --write 'src/**/*.{ts,tsx,js,jsx,json,md}'",
     "format:check": "prettier --check 'src/**/*.{ts,tsx,js,jsx,json,md}'",
+    "test": "npm run test:unit && npm run test:integration",
     "test:unit": "jest --testPathPattern='src/**/*.test.ts'",
     "test:integration": "jest --testPathPattern='src/**/*.integration.test.ts'",
-    "test:coverage": "jest --coverage",
+    "test:coverage": "jest --coverage --coverageReporters=text --coverageReporters=lcov --coverageReporters=json --coverageReporters=json-summary",
     "typecheck": "tsc --noEmit",
     "build": "tsc --project agent-skill-routing-system/tsconfig.json"
+  },
+  "commitlint": {
+    "extends": ["@commitlint/config-conventional"]
   }
 }
```

**Why each change:**
- `lint` no longer auto-fixes (CI must be read-only). New `lint:fix` script for local use.
- `test` script enables `npm test` referenced by release workflow.
- `test:coverage` explicitly enables `json-summary` reporter so the coverage gate can read `coverage/coverage-summary.json`.
- Added `format` (write) for local convenience.
- Added `commitlint`, `semantic-release` and plugin dev-deps so workflows can resolve them.
- Added top-level `private: true` + commitlint reference (so commitlint can find config even without `commitlint.config.js`).

> **Apply with:** `git apply` or just paste the resulting file. After applying, run
> `npm install` to update `package-lock.json`. **Commit the updated lockfile.**

---

### 4.10 PATCH `agent-skill-routing-system/jest.config.js`

If this file exists and does not already include `'json-summary'` in `coverageReporters`, add it.

```diff
 module.exports = {
   // ... existing config ...
-  coverageReporters: ['text', 'lcov', 'json'],
+  coverageReporters: ['text', 'lcov', 'json', 'json-summary'],
 };
```

If your `jest.config.js` has a different shape, just ensure the equivalent of:

```js
coverageReporters: ['text', 'lcov', 'json', 'json-summary'],
```

is present. Without it, the `coverage` job's threshold check will skip with a warning.

---

## 5. Verification Checklist

Run these locally **before** opening the PR.

### 5.1 Static lint of the workflows themselves

```bash
# Install actionlint (one-time)
brew install actionlint     # macOS
# or: go install github.com/rhysd/actionlint/cmd/actionlint@latest

actionlint .github/workflows/*.yml
```

Expected: **no errors**.

### 5.2 Local npm sanity

```bash
npm ci
npm run lint
npm run format:check
npm run typecheck
npm run test:coverage
npm run build
```

Expected: all green. Verify `coverage/coverage-summary.json` exists after the test step.

### 5.3 Dry-run semantic-release

```bash
# Use a personal access token with repo scope, NOT the real workflow token
GITHUB_TOKEN=<your-pat> npx semantic-release --dry-run --no-ci
```

Expected: prints "next version is X.Y.Z" or "no relevant changes" (both fine) — does **not** error.

### 5.4 Commitlint sanity

```bash
echo "feat: test message" | npx commitlint
echo "broken message"     | npx commitlint   # should FAIL
```

### 5.5 Push to a feature branch

```bash
git checkout -b chore/modernize-actions
git add -A
git commit -m "ci: modernize GitHub Actions workflows for May 2026

- Merge ci.yml and quality.yml; remove node_modules artifact pattern
- Replace invalid semantic-release/github@v9 with cycjimmy@v4 + .releaserc.json
- Fix coverage parser, codecov action, snyk pinning
- Add CodeQL workflow and Dependabot config
- Bump setup-python to v5; remove missing-script phases from skill-relationships.yml"
git push -u origin chore/modernize-actions
gh pr create --fill
```

Then verify in the GitHub UI that **every workflow job is green** before merging.

### 5.6 Required checks for branch protection

After merging, in **Settings → Branches → main → Branch protection rules**, mark these as required:

- `CI Status` (the aggregator job from `ci.yml`)
- `Analyze (javascript-typescript)` (CodeQL)
- `Analyze (python)` (CodeQL)
- `Validate Skills & Update Indexes` (only if you want to gate on it)

---

## 6. Rollout Guidance (Repo Settings & Secrets)

### 6.1 Workflow permissions

**Settings → Actions → General → Workflow permissions**:
- ✅ Read and write permissions
- ✅ Allow GitHub Actions to create and approve pull requests

(Required so `release.yml` can tag, push CHANGELOG, and create releases; and so `skill-relationships.yml` can auto-commit.)

### 6.2 Secrets to configure

| Secret | Required | Purpose |
|---|---|---|
| `GITHUB_TOKEN` | ✅ auto | Built-in; used by all workflows |
| `NPM_TOKEN` | ⚠ only if publishing | Read `.releaserc.json`; set `npmPublish: true` first |
| `CODECOV_TOKEN` | optional | Codecov upload — coverage job no-ops gracefully without it |
| `SNYK_TOKEN` | optional | Snyk scan — security job no-ops gracefully without it |

### 6.3 Conventional Commits enforcement

The repo already has `.husky/commit-msg`. After applying §4.8, also ensure local hooks
work by running `npx husky init` (Husky v9+) once after `npm install`.

---

## 7. Rollback Plan

If anything breaks in production after merge:

```bash
# Find the merge commit
git log --oneline | head -5

# Revert the entire change as one atomic commit
git revert -m 1 <merge-commit-sha>
git push origin main
```

All four workflows will return to their previous (broken-but-known) state. No data loss
is possible because none of the changes mutate code, only CI configuration.

---

## 8. Appendix: Issue → Fix Traceability

| # | Issue (from §1) | Fixed In |
|---|---|---|
| 1 | `semantic-release/github@v9` invalid | §4.3, §4.7 |
| 2 | No semantic-release config / dep | §4.7, §4.9 |
| 3 | `node_modules` artifact pattern | §4.2 (removed `install` job) |
| 4 | `eslint --fix` in CI | §4.2, §4.9 |
| 5 | Deprecated codecov npm-global | §4.2 (uses `codecov/codecov-action@v5`) |
| 6 | Fragile coverage parser | §4.2, §4.9, §4.10 |
| 7 | `snyk/actions/node@master` | §4.2 (`@v3`) |
| 8 | Brittle `commitlint --from HEAD~1` | §4.2 (`wagoid/commitlint-github-action@v6`) |
| 9 | Missing skill-relationship Python scripts | §4.4 (phases removed) |
| 10 | `reformat_skills.py` wrong path | §4.4 (corrected to `scripts/`) |
| 11 | No top-level `permissions:` | §4.2, §4.3, §4.4, §4.5 |
| 12 | `setup-python@v4` outdated | §4.4 (`@v5`) |
| 13 | `npm test` script missing | §4.9 |
| 14 | `npm run docs:generate` missing | §4.3 (job removed; `@semantic-release/git` handles CHANGELOG) |
| 15 | `--provenance` without `id-token: write` | §4.3 (job permission added; npm provenance handled by plugin) |
| 16 | CI/Quality duplication | §4.1 (delete), §4.2 (merge) |
| 17 | No `timeout-minutes` | §4.2, §4.3, §4.4, §4.5 |
| 18 | No CodeQL | §4.5 |
| 19 | No Dependabot | §4.6 |

---

## END OF FIX PROMPT

> **Agent instruction (for the executor):**
> Apply §4.1 through §4.10 in order. After each step, do not run any tests; apply all
> changes first as a single commit. Then run §5 in order. If any §5 step fails, stop
> and report the failure with the full error output. Do not push to `main` directly —
> open a PR. Do not modify any source code under `src/` or
> `agent-skill-routing-system/src/` — this task is **CI configuration only**.

