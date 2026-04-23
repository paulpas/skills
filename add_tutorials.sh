#!/usr/bin/env bash

# Script to add Tutorial sections to all CNCF skills that don't have one
# This will be run by the coder agent to batch process all skills

WORK_DIR="/home/paulpas/git/skills"
SKILL_DIRS=$(find "$WORK_DIR" -maxdepth 1 -type d -name "cncf-*" | sort)

echo "Found $(echo "$SKILL_DIRS" | wc -l) CNCF skill directories"

# Track statistics
total=0
has_tutorial=0
needs_tutorial=0
processed=0

for skill_dir in $SKILL_DIRS; do
    skill_name=$(basename "$skill_dir")
    skill_file="$skill_dir/SKILL.md"
    
    if [[ ! -f "$skill_file" ]]; then
        echo "WARNING: No SKILL.md in $skill_dir, skipping"
        continue
    fi
    
    ((total++))
    
    # Check if tutorial section exists
    if grep -q "^## Tutorial" "$skill_file"; then
        ((has_tutorial++))
        echo "✓ $skill_name - already has Tutorial"
        continue
    fi
    
    ((needs_tutorial++))
    echo " needs Tutorial ($needs_tutorial/$total)"
done

echo ""
echo "Summary:"
echo "  Total skills: $total"
echo "  Already have Tutorial: $has_tutorial"
echo "  Need Tutorial: $needs_tutorial"
