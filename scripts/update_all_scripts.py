#!/usr/bin/env python3
"""
Update all Python automation scripts for hierarchical directory structure.
"""

import re
from pathlib import Path

scripts_dir = Path("/home/paulpas/git/agent-skill-router/scripts")
updated_count = 0

# List of scripts to check and update
scripts_to_check = [
    "enhance_triggers.py",
    "connect_trading_skills.py",
]

DOMAINS = ["agent", "cncf", "coding", "programming", "trading"]

for script_name in scripts_to_check:
    script_path = scripts_dir / script_name
    if not script_path.exists():
        print(f"⚠️  {script_name} not found, skipping")
        continue

    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Check if already updated (has DOMAINS list)
    if 'DOMAINS = ["agent", "cncf", "coding", "programming", "trading"]' in content:
        print(f"✅ {script_name} - already uses domain structure")
        continue

    # Pattern 1: Find skill_dirs = [d for d in SKILLS_ROOT.iterdir()...]
    if (
        "skill_dirs = sorted([d for d in SKILLS_ROOT.iterdir() if d.is_dir()])"
        in content
    ):
        content = content.replace(
            "skill_dirs = sorted([d for d in SKILLS_ROOT.iterdir() if d.is_dir()])",
            """DOMAINS = ["agent", "cncf", "coding", "programming", "trading"]
    skill_dirs = []
    for domain in DOMAINS:
        domain_path = SKILLS_ROOT / domain
        if domain_path.exists():
            skill_dirs.extend(sorted([d for d in domain_path.iterdir() if d.is_dir()]))
    skill_dirs = sorted(skill_dirs)""",
        )

    # Pattern 2: Find skill_dirs = [d for d in skills_root.iterdir()...]
    if (
        "skill_dirs = sorted([d for d in skills_root.iterdir() if d.is_dir()])"
        in content
    ):
        content = content.replace(
            "skill_dirs = sorted([d for d in skills_root.iterdir() if d.is_dir()])",
            """DOMAINS = ["agent", "cncf", "coding", "programming", "trading"]
    skill_dirs = []
    for domain in DOMAINS:
        domain_path = skills_root / domain
        if domain_path.exists():
            skill_dirs.extend(sorted([d for d in domain_path.iterdir() if d.is_dir()]))
    skill_dirs = sorted(skill_dirs)""",
        )

    # Pattern 3: Find glob patterns
    content = re.sub(r'glob\(["\']skills/\*-\*["\']', 'glob("skills/*/*")', content)

    if content != original:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Updated {script_name}")
        updated_count += 1
    else:
        print(f"ℹ️  {script_name} - no changes needed (manual review recommended)")

print(f"\n✅ Updated {updated_count} scripts")
