#!/usr/bin/env bash
# Installs git hooks for the agent-skill-router repository.
# Usage: bash scripts/install_hooks.sh

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOK_SOURCE="$REPO_ROOT/scripts/git-hooks/pre-commit"

echo "Installing git hooks for agent-skill-router..."

if [ ! -f "$HOOK_SOURCE" ]; then
    echo "❌ Hook source not found: $HOOK_SOURCE" >&2
    exit 1
fi

# Backup existing hook if present
if [ -f "$HOOKS_DIR/pre-commit" ]; then
    backup="$HOOKS_DIR/pre-commit.bak.$(date +%s)"
    echo "⚠️  Existing pre-commit hook backed up to: $backup"
    cp "$HOOKS_DIR/pre-commit" "$backup"
fi

cp "$HOOK_SOURCE" "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/pre-commit"
chmod +x "$REPO_ROOT/scripts/validate_skill.sh"

echo ""
echo "✅ Installed: .git/hooks/pre-commit"
echo ""
echo "The hook will:"
echo "  • Run on every git commit"
echo "  • Validate all staged SKILL.md files against stub detection rules"
echo "  • Block commits containing stubs automatically"
echo ""
echo "To run with LLM quality check:  ./scripts/validate_skill.sh --llm skills/coding/my-skill/SKILL.md"
echo "To bypass (emergency only):     SKIP_SKILL_VALIDATE=1 git commit ..."
echo "To uninstall:                   rm .git/hooks/pre-commit"
