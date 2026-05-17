#!/usr/bin/env bash
# =============================================================================
# fix-agent-skills.sh — Fix generic boilerplate in agent skills
# =============================================================================
#
# Runs skill-fixer.sh against all agent/* SKILL.md files with a
# domain-specific prompt optimized for removing generic orchestration
# boilerplate and replacing it with domain-specific examples.
#
# USAGE:
#   ./scripts/fix-agent-skills.sh [OPTIONS]
#
# OPTIONS (passed through to skill-fixer.sh):
#   --dry-run        Show what would be done without modifying files
#   --max-retries N  Maximum retry attempts per file (default: 2)
#   --validate-only  Only check for issues, do not fix
#
# EXAMPLES:
#   ./scripts/fix-agent-skills.sh                    # Fix all agent skills
#   ./scripts/fix-agent-skills.sh --dry-run          # Preview fixes
#   ./scripts/fix-agent-skills.sh --max-retries 3    # More retry attempts
#
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "============================================"
echo "  Agent Skill Fixer"
echo "============================================"
echo ""
echo "Target: skills/agent/*/SKILL.md"
echo "Goal: Remove generic select_skill/execute_with_fallback boilerplate"
echo "      and replace with domain-specific examples"
echo ""

exec bash "$SCRIPT_DIR/skill-fixer.sh" \
    "skills/agent/*/SKILL.md" \
    "$@"
