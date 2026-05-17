#!/usr/bin/env bash
# =============================================================================
# fix-coding-ds-skills.sh — Fix placeholder code in data science skills
# =============================================================================
#
# Runs skill-fixer.sh against all coding/ds-* SKILL.md files with a
# domain-specific prompt optimized for data science code examples.
#
# USAGE:
#   ./scripts/fix-coding-ds-skills.sh [OPTIONS]
#
# OPTIONS (passed through to skill-fixer.sh):
#   --dry-run        Show what would be done without modifying files
#   --max-retries N  Maximum retry attempts per file (default: 2)
#   --validate-only  Only check for issues, do not fix
#
# EXAMPLES:
#   ./scripts/fix-coding-ds-skills.sh                    # Fix all ds-* skills
#   ./scripts/fix-coding-ds-skills.sh --dry-run          # Preview fixes
#   ./scripts/fix-coding-ds-skills.sh --max-retries 3    # More retry attempts
#
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "============================================"
echo "  Data Science Skill Fixer"
echo "============================================"
echo ""
echo "Target: skills/coding/ds-*/SKILL.md"
echo "Domain: Data Science (pandas, numpy, scikit-learn, etc.)"
echo ""

exec bash "$SCRIPT_DIR/skill-fixer.sh" \
    "skills/coding/ds-*/SKILL.md" \
    "$@"
