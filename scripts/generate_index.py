#!/usr/bin/env python3
"""
Generate skills-index.json from SKILL.md files in the skills directory.
This script extracts metadata from skill frontmatter and builds an index
for the skill-router to use for auto-loading and task routing.

Version: 1.1.0
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

try:
    import yaml
except ImportError:
    print("❌ PyYAML not installed. Install with: pip install pyyaml")
    sys.exit(1)

# Add current directory to path for utils module
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)
from utils import (
    Colors,
    get_domain_defaults,
    get_skills_directory,
    format_error,
    parse_yaml_frontmatter,
    normalize_triggers,
)
from domain_discovery import get_domain_list


def extract_triggers(metadata: dict) -> list:
    """Extract triggers from metadata using normalize_triggers utility."""
    return normalize_triggers(metadata.get("metadata", {}).get("triggers"))


def extract_related_skills(metadata: dict) -> list:
    """Extract related skills from metadata."""
    related_str = metadata.get("metadata", {}).get("related-skills", "")
    if not related_str:
        return []

    skills = [s.strip() for s in related_str.split(",")]
    return [s for s in skills if s]


def scan_skills_directory(skills_root: Path) -> tuple[list, dict]:
    """Scan skills directory and extract metadata from all SKILL.md files."""
    skills = []
    stats = {
        "total": 0,
        "domains": {},
        "roles": {},
        "domains_with_count": {},
        "errors": [],
        "warnings": [],
    }

    for domain_dir in sorted(skills_root.iterdir()):
        if not domain_dir.is_dir():
            continue

        domain_name = domain_dir.name
        stats["domains"][domain_name] = 0

        for skill_dir in sorted(domain_dir.iterdir()):
            if not skill_dir.is_dir():
                continue

            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                stats["errors"].append(f"No SKILL.md in {skill_dir}")
                continue

            stats["total"] += 1
            stats["domains"][domain_name] += 1

            try:
                content = skill_md.read_text(encoding="utf-8")
                # Parse YAML frontmatter - utils returns (dict, str, error) tuple
                metadata_dict, body, error = parse_yaml_frontmatter(content)

                if error:
                    stats["warnings"].append(f"YAML parse error in {skill_dir}")
                    continue

                if metadata_dict is None:
                    stats["warnings"].append(f"No frontmatter in {skill_dir}")
                    continue

                # Extract domain from directory (remove prefix like "cncf-" from skill name)
                skill_name = metadata_dict.get("name", skill_dir.name)

                # Get metadata section
                meta = metadata_dict.get("metadata", {})
                triggers = extract_triggers(metadata_dict)
                related = extract_related_skills(metadata_dict)

                skill_entry = {
                    "name": skill_name,
                    "domain": domain_name,
                    "description": metadata_dict.get("description", ""),
                    "role": meta.get("role", "implementation"),
                    "scope": meta.get("scope", "implementation"),
                    "outputFormat": meta.get("output-format", "code"),
                    "triggers": triggers,
                    "relatedSkills": related,
                    "version": meta.get("version", "1.0.0"),
                    "source": str(skill_md.relative_to(skills_root.parent)),
                }

                skills.append(skill_entry)

                # Update role stats
                role = skill_entry["role"]
                stats["roles"][role] = stats["roles"].get(role, 0) + 1

                # Track domains with counts
                stats["domains_with_count"][domain_name] = stats["domains"][domain_name]

            except Exception as e:
                error_msg = format_error(
                    "generate_index.py", domain_name, skill_dir.name, f"Error: {e}"
                )
                stats["errors"].append(error_msg)

    return skills, stats


def generate_index(skills: list, stats: dict) -> dict:
    """Generate the complete index structure."""
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "totalSkills": len(skills),
        "domains": stats["domains_with_count"],
        "roles": stats["roles"],
        "skills": skills,
        "indexVersion": "1.0.0",
    }


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    skills_root = repo_root / "skills"
    output_file = repo_root / "skills-index.json"

    print("🔍 Scanning skills directory...")
    print(f"   Root: {skills_root}")

    if not skills_root.exists():
        print(f"❌ Skills directory not found: {skills_root}")
        sys.exit(1)

    skills, stats = scan_skills_directory(skills_root)

    print(f"\n📊 Index Statistics:")
    print(f"   Total skills: {stats['total']}")
    print(f"   Domains: {list(stats['domains'].keys())}")
    print(f"   Roles: {list(stats['roles'].keys())}")

    if stats["warnings"]:
        print(f"\n⚠️  Warnings ({len(stats['warnings'])}):")
        for w in stats["warnings"][:5]:
            print(f"   - {w}")
        if len(stats["warnings"]) > 5:
            print(f"   ... and {len(stats['warnings']) - 5} more")

    if stats["errors"]:
        print(f"\n❌ Errors ({len(stats['errors'])}):")
        for e in stats["errors"][:5]:
            print(f"   - {e}")
        if len(stats["errors"]) > 5:
            print(f"   ... and {len(stats['errors']) - 5} more")

    print(f"\n📝 Generating index...")
    index = generate_index(skills, stats)

    # Sort skills alphabetically by name
    index["skills"].sort(key=lambda s: s["name"])

    # Write output
    output_file.write_text(
        json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\n✅ Output written to:")
    print(f"   {output_file}")
    print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")

    # Show sample
    print(f"\n📄 Sample entry:")
    if skills:
        sample = skills[0]
        print(f"   {sample['name']} ({sample['domain']})")
        print(f"   Description: {sample['description'][:80]}...")
        print(f"   Triggers: {', '.join(sample['triggers'][:3])}...")

    return 0


if __name__ == "__main__":
    sys.exit(main())
