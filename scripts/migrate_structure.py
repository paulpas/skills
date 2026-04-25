#!/usr/bin/env python3
"""
Restructure skills from flat (cncf-kubernetes) to hierarchical (cncf/kubernetes).
"""

import os
import re
import shutil
from pathlib import Path

SKILLS_ROOT = Path("/home/paulpas/git/agent-skill-router/skills")
DOMAINS = ["agent", "cncf", "coding", "programming", "trading"]

# Map old names to new names
migrations = []

print("🔍 Scanning for skills to migrate...")
old_dirs = [d for d in SKILLS_ROOT.iterdir() if d.is_dir() and "-" in d.name]

migrated = 0
skipped = 0
errors = 0

for old_dir in sorted(old_dirs):
    old_name = old_dir.name

    # Skip domain directories themselves (already created)
    if old_name in DOMAINS:
        continue

    # Parse domain-skillname from directory name
    parts = old_name.split("-", 1)  # Split on first hyphen only
    if len(parts) != 2:
        print(f"⚠️  Skipping {old_name}: cannot parse domain-skill")
        skipped += 1
        continue

    domain, skill_name = parts

    # Validate domain
    if domain not in DOMAINS:
        print(f"⚠️  Skipping {old_name}: unknown domain '{domain}'")
        skipped += 1
        continue

    # Target directory
    target_dir = SKILLS_ROOT / domain / skill_name
    target_skill_md = target_dir / "SKILL.md"

    # Move directory
    if target_dir.exists():
        print(f"⚠️  Skipping {old_name}: target {domain}/{skill_name} already exists")
        skipped += 1
        continue

    try:
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_dir), str(target_dir))
        migrated += 1
        if migrated % 100 == 0:
            print(f"  ... migrated {migrated} skills so far")
    except Exception as e:
        print(f"❌ Error migrating {old_name}: {e}")
        errors += 1

print(f"\n✅ Migration complete:")
print(f"  - Migrated: {migrated} skills")
print(f"  - Skipped: {skipped} skills")
print(f"  - Errors: {errors} skills")

exit(0 if errors == 0 else 1)
