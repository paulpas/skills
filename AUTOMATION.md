# Skill Relationship Automation

This document explains the automated systems that recalculate and maintain skill relationships in the agent-skill-router repository.

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Pre-Commit Hook](#pre-commit-hook)
- [GitHub Actions Workflow](#github-actions-workflow)
- [Local Testing](#local-testing)
- [Troubleshooting](#troubleshooting)
- [Skill Router Integration](#skill-router-integration)

---

## Overview

The agent-skill-router uses three complementary automation systems to keep skill relationships, indexes, and documentation synchronized:

1. **Pre-Commit Hook** — Local validation before commits (prevents broken data)
2. **GitHub Actions Workflow** — Remote validation and auto-commits (ensures consistency)
3. **Skill Router Runtime** — Dynamic skill discovery at runtime (enables live updates)

Together, these systems ensure that:
- ✅ Every new skill is validated for YAML correctness
- ✅ Skill relationships are automatically recalculated
- ✅ Bidirectional relationships are enforced
- ✅ Index files are always in sync with skill data
- ✅ README catalog is automatically updated
- ✅ Changes are committed back to the repository

---

## How It Works

### The Complete Flow

```
Developer adds a new SKILL.md
            ↓
Git staging area detects change
            ↓
Pre-commit hook triggers automatically
            ↓
1. YAML validation runs
2. Relationship analysis runs
3. Bidirectionality check runs
4. Index regeneration
5. README update
6. Updated files auto-staged
            ↓
Developer commits (hook files included)
            ↓
Push to GitHub
            ↓
GitHub Actions workflow triggers
            ↓
7. Remote validation (same checks)
8. Additional enhancements run
9. Auto-commit results back to branch
            ↓
PR/merge proceeds with all metadata in sync
```

### What Each System Does

| System | When | What | Result |
|--------|------|------|--------|
| **Pre-Commit Hook** | Locally, before commit | Validate & regenerate indexes | Prevents commits with broken skills |
| **GitHub Actions** | On push/PR, on GitHub | Redundant validation + auto-commit | Ensures all PRs have fresh indexes |
| **Skill Router** | At runtime, on demand | Reloads skills from disk | Enables live discovery without restart |

---

## Pre-Commit Hook

### Location

```
.git/hooks/pre-commit
```

### What It Does

The pre-commit hook automatically runs when you execute `git commit`. It:

1. **Detects changes** — Identifies if any `skills/*/SKILL.md` files are staged
2. **Skips if no changes** — If no skill files changed, exits immediately
3. **Validates YAML** — Runs `reformat_skills.py` to check syntax
4. **Generates indexes** — Runs `generate_index.py` to create `skills-index.json`
5. **Analyzes relationships** — Runs relationship analysis scripts
6. **Fixes relationships** — Auto-corrects missing reciprocal relationships
7. **Enforces bidirectionality** — Ensures A→B implies B→A
8. **Enhances CNCF** — Domain-specific relationship improvements
9. **Generates documentation** — Updates README.md with latest catalog
10. **Stages updates** — Automatically adds generated files to commit
11. **Allows commit** — Proceeds if all validation passed

### The Hook is Executable

The hook is automatically made executable when you clone the repository:

```bash
ls -la .git/hooks/pre-commit
# -rwxrwxr-x 1 paulpas paulpas 5258 Apr 24 17:41 .git/hooks/pre-commit
```

If it's not executable, make it so:

```bash
chmod +x .git/hooks/pre-commit
```

### What Happens When You Commit

**Scenario: Adding a new skill**

```bash
# Create a new skill
mkdir -p skills/my-new-skill/
cat > skills/my-new-skill/SKILL.md << 'EOF'
---
name: my-new-skill
description: Does something awesome
metadata:
  version: "1.0.0"
  domain: coding
  triggers: awesome, new feature
  role: implementation
  scope: implementation
  output-format: code
---
# My New Skill
...
EOF

# Stage the new skill
git add skills/my-new-skill/SKILL.md

# Commit — this triggers the pre-commit hook
git commit -m "feat: add my-new-skill"
```

**What the hook does:**

```
ℹ️  Detected changes to SKILL.md files:
  - skills/my-new-skill/SKILL.md

ℹ️  === Phase 1: Validation ===
ℹ️  Running: YAML validation (reformat_skills.py)
✅ YAML validation completed

ℹ️  === Phase 2: Index Generation ===
ℹ️  Running: Index generation (generate_index.py)
✅ Index generation completed

ℹ️  === Phase 3: Relationship Analysis ===
ℹ️  Running: Relationship analysis
✅ Relationship analysis completed

[... phases 4-6 ...]

ℹ️  === Phase 7: Staging Updates ===
✅ Staged: skills-index.json
✅ Staged: README.md
✅ Staged: SKILL_RELATIONSHIPS_ANALYSIS.md
✅ Staged 3 updated file(s)

✅ Pre-commit hook completed successfully!
ℹ️  Run 'git diff --cached' to review staged changes
```

Your commit now includes the original skill + the updated index files.

### Skipping the Hook (NOT Recommended)

If you need to skip the hook for a specific commit:

```bash
# Skip with --no-verify flag
git commit --no-verify -m "your message"

# Or set environment variable
SKIP_SKILL_HOOK=1 git commit -m "your message"
```

**⚠️ WARNING:** Skipping the hook is **not recommended** because:
- Index files become out of sync
- Broken YAML won't be caught until CI
- Relationship gaps won't be fixed
- The PR will fail validation on GitHub

**When might you skip:**
- You're committing a work-in-progress (WIP) that you'll fix before pushing
- You want to commit without triggering scripts (rare edge case)
- You're debugging a hook issue

Even then, always run the scripts locally before pushing:

```bash
# If you skipped the hook, run scripts manually before pushing
python3 reformat_skills.py
python3 generate_index.py
python3 agent-skill-routing-system/scripts/analyze_skill_relationships.py
python3 agent-skill-routing-system/scripts/fix_skill_relationships.py
python3 agent-skill-routing-system/scripts/enforce_bidirectionality.py
python3 agent-skill-routing-system/scripts/enhance_cncf_relationships.py
python3 scripts/generate_readme.py

git add skills-index.json README.md SKILL_RELATIONSHIPS_ANALYSIS.md TRIGGER_ENHANCEMENTS.md
git commit --amend -m "add missing automation updates"
```

### Understanding Hook Output

The hook outputs color-coded messages:

| Icon | Color | Meaning | Action |
|------|-------|---------|--------|
| ℹ️ | Blue | Information | FYI, no action needed |
| ✅ | Green | Success | Step completed successfully |
| ⚠️ | Yellow | Warning | Non-critical issue, but worth noting |
| ❌ | Red | Error | Critical failure, commit rejected |

**Example output breakdown:**

```
ℹ️  === Phase 1: Validation ===          # Blue = informational
ℹ️  Running: YAML validation...          # Shows what's running
✅ YAML validation completed             # Green = success

ℹ️  === Phase 2: Index Generation ===
ℹ️  Running: Index generation...
✅ Index generation completed

[... if a step fails ...]
❌ YAML validation failed                # Red = error, prevents commit
Please fix SKILL.md syntax.
exit 1                                   # Commit rejected
```

---

## GitHub Actions Workflow

### Location

```
.github/workflows/skill-relationships.yml
```

### Triggers

The workflow runs automatically on:

- **Push to main/master** — When code is pushed to production branches
- **Pull request** — When a PR is opened against main/master
- **SKILL.md changes** — Only if `skills/**/SKILL.md` files are modified
- **Workflow dispatch** — Manual trigger via GitHub Actions UI

### What It Does

The GitHub Actions workflow:

1. **Checks out code** — Clones the repository at current commit
2. **Sets up Python** — Configures Python 3.12 environment
3. **Installs dependencies** — Installs pyyaml
4. **Detects changes** — Identifies modified SKILL.md files
5. **Runs all validation scripts** in sequence:
   - YAML validation
   - Index generation
   - Relationship analysis
   - Fix relationships
   - Enforce bidirectionality
   - Enhance CNCF relationships
   - Generate README
6. **Stages updates** — Adds generated files to git
7. **Auto-commits results** — Creates commit with updates
8. **Reports summary** — Posts results to PR/workflow summary

### GitHub Actions UI

You can view the workflow status:

1. Go to: **Actions** tab in GitHub
2. Find: **"Skill Relationships & Index Generation"** workflow
3. Click the latest run to see:
   - ✅ Each phase and its status
   - 📊 Relationship updates summary
   - 📝 Files modified
   - 💬 Commit message

### Auto-Commit Behavior

The workflow automatically commits results **only on main/master branches**:

```yaml
if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'
```

This means:
- ✅ **main/master**: Updates committed automatically
- ⚠️ **Pull requests**: Updates shown in workflow, not auto-committed
- ✅ **After PR merge**: Next push triggers auto-commit

### Force Update

To force re-run the workflow on all skills:

1. Go to: **Actions** → **"Skill Relationships & Index Generation"**
2. Click: **"Run workflow"** button
3. Select: **"Force update all indexes"** = `true`
4. Click: **"Run workflow"**

This regenerates all indexes even if no SKILL.md files changed.

### Concurrent Runs

The workflow uses `concurrency` to prevent multiple simultaneous runs:

```yaml
concurrency:
  group: skill-relationships-${{ github.ref }}
  cancel-in-progress: true
```

This means:
- If you push multiple commits quickly, only the latest run executes
- Earlier runs are automatically cancelled
- Prevents git conflicts from simultaneous updates

---

## Local Testing

### Test 1: Validate Your Hook Installation

Check that the pre-commit hook exists and is executable:

```bash
ls -la .git/hooks/pre-commit

# Expected output:
# -rwxrwxr-x 1 paulpas paulpas 5258 Apr 24 17:41 .git/hooks/pre-commit
```

If not executable:

```bash
chmod +x .git/hooks/pre-commit
```

### Test 2: Create a Test Skill

Create a new test skill to verify the automation:

```bash
mkdir -p skills/test-automation-skill/

cat > skills/test-automation-skill/SKILL.md << 'EOF'
---
name: test-automation-skill
description: Test skill for automation verification
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  role: implementation
  scope: implementation
  output-format: code
  triggers: automation testing, test skill, verify automation
  related-skills: coding-code-review
---

# Test Automation Skill

This skill is for testing the automation system.

## When to Use

- Testing the pre-commit hook
- Verifying skill relationship automation
- Validating index generation

## When NOT to Use

- In production environments
- For real development workflows

## Core Content

The automation system should:
1. Detect this skill's creation
2. Validate its YAML
3. Add it to skills-index.json
4. Create reciprocal relationship with coding-code-review
5. Update README.md

EOF
```

### Test 3: Stage and Commit

```bash
# Stage the test skill
git add skills/test-automation-skill/SKILL.md

# Try to commit — watch the hook output
git commit -m "test: add test automation skill

This tests the pre-commit hook and automation system."
```

**Expected output:** Should see all 7 phases running, files staged, success message.

### Test 4: Verify Generated Files

```bash
# Check if index was updated
git status

# You should see:
# modified:   README.md
# modified:   SKILL_RELATIONSHIPS_ANALYSIS.md
# modified:   skills-index.json
# modified:   TRIGGER_ENHANCEMENTS.md

# View the changes
git diff --cached README.md | head -50

# View skill in index
python3 -c "import json; idx = json.load(open('skills-index.json')); print([s for s in idx if s['name'] == 'test-automation-skill'])"
```

### Test 5: Check Reciprocal Relationship

```bash
# Our test skill listed coding-code-review as a related skill
# coding-code-review should have been updated to list our test skill

python3 << 'EOF'
import os, yaml

# Check our test skill
with open('skills/test-automation-skill/SKILL.md') as f:
    content = f.read()
    # Find metadata.related-skills
    if 'related-skills:' in content:
        print("✅ Test skill has related-skills defined")

# Check coding-code-review for reciprocal relationship
try:
    with open('skills/coding-code-review/SKILL.md') as f:
        content = f.read()
        if 'test-automation-skill' in content:
            print("✅ coding-code-review lists test-automation-skill")
        else:
            print("⚠️  coding-code-review doesn't list test-automation-skill (yet)")
except FileNotFoundError:
    print("ℹ️  coding-code-review skill not found")
EOF
```

### Test 6: Clean Up Test Skill

```bash
# Remove the test skill
rm -rf skills/test-automation-skill/

# Commit the removal
git add -A
git commit -m "test: remove test automation skill"

# The hook will run again and clean up the index
```

---

## Troubleshooting

### Problem: Hook Not Running

**Symptom:** You commit a SKILL.md file but the hook doesn't run.

**Solutions:**

1. **Check hook is executable:**
   ```bash
   ls -la .git/hooks/pre-commit
   # Should show -rwxrwxr-x (executable)
   ```

2. **Check git recognizes hooks:**
   ```bash
   git config core.hooksPath
   # Should return: .git/hooks (or similar)
   ```

3. **Verify you're in git repo:**
   ```bash
   git rev-parse --git-dir
   # Should return: .git
   ```

4. **Check hook permissions:**
   ```bash
   chmod +x .git/hooks/pre-commit
   git status
   ```

### Problem: Hook Fails with YAML Error

**Symptom:** Hook rejects commit with "YAML validation failed"

**Solution:** Fix your SKILL.md file:

```bash
# The error message will point to the problem
# Common issues:
# - Missing quotes around colons in values: "name: with: colons"
# - Wrong indentation: mix of tabs and spaces
# - Unclosed strings or blocks

# Use a YAML validator:
python3 -c "import yaml; yaml.safe_load(open('skills/your-skill/SKILL.md'))"

# Fix the YAML, then try again
git add skills/your-skill/SKILL.md
git commit -m "fix: correct SKILL.md YAML syntax"
```

### Problem: Hook Fails on Python Script

**Symptom:** Hook fails on a specific script (e.g., `fix_skill_relationships.py`)

**Solutions:**

1. **Run the script directly to see the error:**
   ```bash
   python3 agent-skill-routing-system/scripts/fix_skill_relationships.py
   # Will show detailed error message
   ```

2. **Check Python dependencies:**
   ```bash
   pip install pyyaml
   ```

3. **Check script exists:**
   ```bash
   ls -la agent-skill-routing-system/scripts/fix_skill_relationships.py
   ```

4. **Run hook with debugging:**
   ```bash
   # Add debug output to see which step fails
   bash -x .git/hooks/pre-commit
   ```

### Problem: Index Not Updated

**Symptom:** You add a skill but `skills-index.json` doesn't update.

**Solution:**

1. **Run index generation manually:**
   ```bash
   python3 generate_index.py
   git diff skills-index.json
   ```

2. **Check index file is staged:**
   ```bash
   git status
   # skills-index.json should be in "Changes to be committed"
   ```

3. **If not staged, add it manually:**
   ```bash
   git add skills-index.json
   git commit --amend --no-edit
   ```

### Problem: GitHub Actions Fails

**Symptom:** PR shows ❌ for "Skill Relationships & Index Generation"

**Solutions:**

1. **Check workflow logs:**
   - Go to: **Actions** tab
   - Click the failing workflow run
   - Click the failing job to see detailed logs

2. **Common causes:**
   - Python dependency missing: Check `pip install pyyaml`
   - YAML syntax error: Same as pre-commit hook
   - Script error: Check that all scripts exist

3. **Re-run workflow:**
   - Click **"Re-run jobs"** in GitHub Actions UI
   - Or push an empty commit: `git commit --allow-empty -m "ci: retrigger workflow"`

### Problem: Merge Conflicts in Generated Files

**Symptom:** Pull request has merge conflicts in `skills-index.json` or `README.md`

**Solution:**

Don't manually resolve conflicts in generated files. Instead:

```bash
# On your branch, regenerate the files
python3 reformat_skills.py
python3 generate_index.py
python3 agent-skill-routing-system/scripts/analyze_skill_relationships.py
python3 agent-skill-routing-system/scripts/fix_skill_relationships.py
python3 agent-skill-routing-system/scripts/enforce_bidirectionality.py
python3 agent-skill-routing-system/scripts/enhance_cncf_relationships.py
python3 scripts/generate_readme.py

# Stage the regenerated files
git add skills-index.json README.md SKILL_RELATIONSHIPS_ANALYSIS.md TRIGGER_ENHANCEMENTS.md

# Commit
git commit -m "chore: regenerate skill indexes to resolve conflicts"

# Push
git push
```

The regenerated files will be correct and conflicts resolved.

### Problem: Performance (Hook Takes Too Long)

**Symptom:** Committing takes 30+ seconds because of hook.

**Optimization:**

1. **Skip non-critical scripts:**
   Edit `.git/hooks/pre-commit` and comment out non-critical phases:
   ```bash
   # Optional: Skip CNCF enhancements if not using CNCF skills
   # if [ -f "$SCRIPTS_DIR/enhance_cncf_relationships.py" ]; then
   #   ...
   # fi
   ```

2. **Use `--no-verify` for quick commits:**
   ```bash
   git commit --no-verify -m "work in progress"
   git commit -m "final commit" # Will run hook for final version
   ```

3. **Cache Python:**
   ```bash
   python3 -B -m compileall scripts/
   ```

---

## Skill Router Integration

The skill-router (running at `localhost:3000`) automatically discovers new skills through the generated `skills-index.json`.

### How Skill Router Works with Automation

1. **Automation generates** `skills-index.json`
2. **Skill Router reads** the index file
3. **Routes requests** based on `triggers` and `tags`
4. **Enables auto-loading** when keywords match conversation

### Reloading Skills at Runtime

When you add a new skill, the skill-router can pick it up without restarting:

#### Option 1: HTTP Reload (Immediate)

```bash
# Force the skill-router to reload skills from disk
curl -X POST http://localhost:3000/reload

# Response:
# {"status": "reloaded", "skillsLoaded": 239, "timestamp": "2026-04-24T..."}
```

#### Option 2: Automatic Reload (Scheduled)

The skill-router checks for updates every `SKILL_SYNC_INTERVAL` seconds (default: 3600 = 1 hour):

```bash
# Check current sync interval
curl http://localhost:3000/stats | jq '.syncInterval'

# To change interval, restart with environment variable:
# SKILL_SYNC_INTERVAL=300 docker start skill-router  # 5 minutes
```

#### Option 3: Watch Mode (Development)

For active development, set a short sync interval:

```bash
# Reload every 10 seconds
docker run -e SKILL_SYNC_INTERVAL=10 skill-router:latest
```

### Checking Skill Router Status

```bash
# Health check
curl http://localhost:3000/health
# {"status": "healthy", "version": "1.0.0"}

# See loaded skills count
curl http://localhost:3000/stats | jq '.skills'
# {"totalSkills": 239, ...}

# List all skills
curl http://localhost:3000/skills | jq 'length'
# 239

# Get specific skill
curl http://localhost:3000/skill/coding-code-review
# Returns full SKILL.md content
```

### Docker Integration

If running skill-router in Docker:

```bash
# View logs
docker logs skill-router -f --tail 50

# Restart after pushing new skills
docker restart skill-router

# Or use the /reload endpoint (preferred, no downtime)
curl -X POST http://localhost:3000/reload
```

---

## Summary

The three-layer automation system works together:

| Layer | When | What | Result |
|-------|------|------|--------|
| **Pre-commit Hook** | Before each commit | Validates, generates, stages | Prevents broken commits |
| **GitHub Actions** | On push to GitHub | Re-validates, auto-commits | Ensures consistency |
| **Skill Router** | At runtime | Reloads skill index | Enables live discovery |

**Best practices:**

✅ **Always let the pre-commit hook run** — It prevents problems early
✅ **Check hook output before committing** — It tells you what changed
✅ **Review staged files before committing** — `git diff --cached` to verify
✅ **Let GitHub Actions run** — It provides redundant validation
✅ **Use `/reload` endpoint** — For immediate skill-router updates

This ensures skills are always valid, relationships are always synchronized, and your skill catalog is always consistent.
