---
name: github-actions-status
description: "View and monitor GitHub Actions workflow runs, statuses, and logs using the
  gh CLI. Lists workflows, inspects run details, follows logs, checks commit statuses,
  and triggers new runs."
license: MIT
compatibility: opencode
metadata:
  version: 1.0.0
  domain: agent
  role: information
  scope: implementation
  output-format: markdown
  triggers: github actions, ci/cd, workflow, gh run, gh workflow, pipeline, build status,
    ci status, action status, check runs
  author: https://github.com/paulpas
  source: local
  related-skills:
---

# GitHub Actions Status

View, monitor, and manage GitHub Actions workflows and their run statuses using the `gh` CLI.

## When to Use This Skill

- Checking the status of CI/CD pipeline runs
- Debugging failed workflow runs by viewing logs
- Monitoring a run until completion
- Listing all workflows and their recent activity
- Triggering a workflow run manually
- Checking commit-level check run statuses via the API

## Prerequisites

- **`gh` CLI must be installed and authenticated** with a GitHub account that has access to the target repository.
- Verify authentication: run `gh auth status` — if not logged in, run `gh auth login`.
- The `--repo <owner>/<repo>` flag is used on all commands to target a specific repository.

## Core Workflow

### Step 1: Identify the Repository

Determine the target repository in `owner/repo` format. If working in a local git repo, you can extract it with:

```bash
git remote get-url origin | sed -E 's|.*:(.+)/(.+)\.git|\1/\2|'
```

### Step 2: List All Workflows

See every workflow file and its last run status:

```bash
gh workflow list --repo <owner>/<repo>
```

This shows each workflow name, ID, state (active/disabled), and the time of its last run.

### Step 3: List Recent Workflow Runs

View the most recent runs across all workflows:

```bash
gh run list --repo <owner>/<repo> --limit 20
```

Use `--status` to filter by state (`pending`, `in_progress`, `completed`, `cancelled`, `failed`, `skipped`, `success`, `neutral`, `timed_out`, `action_required`):

```bash
gh run list --repo <owner>/<repo> --status failed --limit 10
gh run list --repo <owner>/<repo> --status in_progress --limit 10
```

### Step 4: Inspect a Specific Run

View detailed information about a single run:

```bash
gh run view <run-id> --repo <owner>/<repo>
```

This shows the workflow name, status, conclusion, duration, trigger, branch, commit message, and a summary of each job.

### Step 5: View Run Logs

For debugging a failed run, fetch the full logs:

```bash
gh run view <run-id> --repo <owner>/<repo> --log --job <job-id>
```

If no `--job` is specified, all job logs are shown. To list jobs within a run:

```bash
gh run view <run-id> --repo <owner>/<repo> --jobs
```

### Step 6: Monitor a Run in Real-Time

Watch a run's progress until it completes (useful for long-running pipelines):

```bash
gh run watch <run-id> --repo <owner>/<repo>
```

This polls the run status and prints updates. It exits with a non-zero code if the run fails.

### Step 7: Check Commit-Level Check Runs

Query check runs for a specific commit via the GitHub API:

```bash
gh api repos/<owner>/<repo>/commits/<sha>/check-runs
```

This returns check suites and individual check runs, including their conclusions and detailed output.

### Step 8: Trigger a Workflow Run

Manually trigger a workflow:

```bash
gh workflow run <workflow-name> --repo <owner>/<repo> --ref <branch-or-tag>
```

The `--ref` flag specifies which branch/tag to run against (defaults to the default branch).

## Reference

### All Commands

| Action | Command |
|--------|---------|
| List workflows | `gh workflow list --repo <owner>/<repo>` |
| List workflow runs | `gh run list --repo <owner>/<repo> [--limit N] [--status <state>]` |
| View run details | `gh run view <run-id> --repo <owner>/<repo>` |
| List jobs in a run | `gh run view <run-id> --repo <owner>/<repo> --jobs` |
| View run logs | `gh run view <run-id> --repo <owner>/<repo> --log [--job <job-id>]` |
| Watch a run | `gh run watch <run-id> --repo <owner>/<repo>` |
| Trigger workflow | `gh workflow run <name> --repo <owner>/<repo> [--ref <ref>]` |
| Commit check runs | `gh api repos/<owner>/<repo>/commits/<sha>/check-runs` |

### Useful Flags

| Flag | Description |
|------|-------------|
| `--limit N` | Number of runs to return (default varies, max typically 100) |
| `--status STATE` | Filter runs by status (see Step 3 for valid states) |
| `--json FIELDS` | Output selected fields as JSON for programmatic use |
| `--log` | Download and display full run logs |
| `--job JOB` | Filter logs to a specific job ID |
| `--ref REF` | Branch, tag, or commit SHA to trigger on |

### JSON Output for Programmatic Use

For scripts or structured parsing, use `--json` to select specific fields:

```bash
gh run list --repo <owner>/<repo> --limit 5 --json id,workflowName,status,conclusion,createdAt,durationMs,headBranch,headCommit
```

## Examples

### List recent runs for paulpas/agent-skill-router

```bash
gh run list --repo paulpas/agent-skill-router --limit 10
```

### View details of a specific run

```bash
gh run view 1234567890 --repo paulpas/agent-skill-router
```

### Watch a run until completion

```bash
gh run watch 1234567890 --repo paulpas/agent-skill-router
```

### List all workflows and their last run status

```bash
gh workflow list --repo paulpas/agent-skill-router
```

### Filter to only failed runs

```bash
gh run list --repo paulpas/agent-skill-router --status failed --limit 20
```

### View logs for a specific job in a run

```bash
gh run view 1234567890 --repo paulpas/agent-skill-router --log --job 9876543210
```

### Trigger a workflow on a specific branch

```bash
gh workflow run "CI" --repo paulpas/agent-skill-router --ref feature/my-branch
```

### Check commit-level check runs

```bash
gh api repos/paulpas/agent-skill-router/commits/abc1234/check-runs
```

### Get structured JSON of recent runs

```bash
gh run list --repo paulpas/agent-skill-router --limit 5 --json id,workflowName,status,conclusion,createdAt,durationMs,headBranch
```

## Output Format

Present GitHub Actions status results in the following structured format:

### Run Summary Table

| Run ID | Workflow | Status | Branch | Duration | Started |
|--------|----------|--------|--------|----------|---------|
| `12345` | CI | ✅ passed | main | `2m 34s` | 2 hours ago |
| `12344` | CI | ❌ failed | feature/x | `45s` | 3 hours ago |

### Status Indicators

- `✅ passed` — Run completed successfully
- `❌ failed` — Run completed with errors
- `🔄 in_progress` — Run currently executing
- `⏳ pending` — Run queued, not yet started
- `⛔ cancelled` — Run was manually cancelled
- `⚠️ timed_out` — Run exceeded the allowed duration
- `🔶 action_required` — Run requires manual intervention
- `⏭️ skipped` — Run was skipped by conditions
- `🟡 neutral` — Run concluded with neutral status

### Per-Run Detail Format

For each failed or in-progress run, include:

1. **Run header** — workflow name, run ID, status badge, duration
2. **Trigger info** — how the run was triggered (push, PR, manual, etc.)
3. **Branch & commit** — source branch and commit SHA/message
4. **Jobs breakdown** — list each job with its status
5. **Failure reason** — if failed, include the error from the job logs
6. **Duration** — total run time and per-job breakdown

### Failure Reason Extraction

When a run has failed, extract the root cause from logs:

```bash
gh run view <run-id> --repo <owner>/<repo> --log --job <failed-job-id> 2>&1 | grep -iE 'error|fail|exception|failed' | tail -5
```

Present the most relevant error lines (up to 5) as the failure reason.
