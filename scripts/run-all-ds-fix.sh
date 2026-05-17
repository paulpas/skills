#!/usr/bin/env bash
# Run all ds-* skills through the fixer
set -euo pipefail
cd /home/paulpas/git/agent-skill-router
exec bash scripts/fix-coding-ds-skills.sh --max-retries 2 >> logs/skill-fixer-20260516.log 2>&1
