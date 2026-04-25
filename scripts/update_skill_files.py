#!/usr/bin/env python3
"""
Update SKILL.md files:
1. Change 'name' field from 'domain-skillname' to just 'skillname'
2. Update 'related-skills' to remove domain prefixes, use domain:skillname for cross-domain
"""

import os
import re
import yaml
from pathlib import Path

SKILLS_ROOT = Path("/home/paulpas/git/agent-skill-router/skills")
DOMAINS = ["agent", "cncf", "coding", "programming", "trading"]


def get_domain_for_skill(skill_path):
    """Determine domain from directory structure."""
    parts = skill_path.relative_to(SKILLS_ROOT).parts
    return parts[0] if len(parts) > 0 else None


def extract_frontmatter(content):
    """Extract YAML frontmatter from SKILL.md."""
    if not content.startswith("---"):
        return None, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content

    return parts[1], parts[2]


def update_skill_file(skill_md_path, domain):
    """Update a single SKILL.md file."""
    try:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            content = f.read()

        yaml_str, md_content = extract_frontmatter(content)
        if yaml_str is None:
            return False, "No frontmatter"

        try:
            metadata = yaml.safe_load(yaml_str)
        except yaml.YAMLError as e:
            return False, f"YAML error"

        if metadata is None:
            metadata = {}

        # Extract skill name from current name field
        old_name = metadata.get("name", "")

        # Remove domain prefix if present
        if old_name and "-" in old_name:
            parts = old_name.split("-", 1)
            skill_name = parts[1]
        else:
            skill_name = old_name

        metadata["name"] = skill_name

        # Update metadata sub-section if it exists
        if "metadata" not in metadata:
            metadata["metadata"] = {}

        # Update related-skills
        related = metadata["metadata"].get("related-skills", "")
        if related:
            updated_related = []
            for rel_skill in related.split(","):
                rel_skill = rel_skill.strip()
                if not rel_skill:
                    continue

                # Check if it's a domain-prefixed skill
                if "-" in rel_skill:
                    parts = rel_skill.split("-", 1)
                    rel_domain = parts[0]
                    rel_name = parts[1]

                    if rel_domain in DOMAINS:
                        if rel_domain == domain:
                            # Same domain: just use skill name
                            updated_related.append(rel_name)
                        else:
                            # Different domain: use domain:skillname notation
                            updated_related.append(f"{rel_domain}:{rel_name}")
                    else:
                        # Not a known domain prefix, keep as-is
                        updated_related.append(rel_skill)
                else:
                    # No domain prefix: assume same domain if no colon
                    updated_related.append(rel_skill)

            if updated_related:
                metadata["metadata"]["related-skills"] = ", ".join(updated_related)

        # Reconstruct file with proper YAML formatting
        # Use safe_dump to ensure proper YAML output
        yaml_output = yaml.dump(
            metadata, default_flow_style=False, allow_unicode=True, sort_keys=False
        )
        new_content = f"---\n{yaml_output}---\n{md_content}"

        with open(skill_md_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return True, "Updated"
    except Exception as e:
        return False, str(e)


print("🔄 Updating all SKILL.md files...")
updated = 0
failed = 0
failed_skills = []

for domain_dir in SKILLS_ROOT.iterdir():
    if not domain_dir.is_dir() or domain_dir.name not in DOMAINS:
        continue

    domain = domain_dir.name

    for skill_dir in domain_dir.iterdir():
        if not skill_dir.is_dir():
            continue

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        success, msg = update_skill_file(skill_md, domain)
        if success:
            updated += 1
        else:
            failed += 1
            failed_skills.append((skill_dir.name, msg))

print(f"\n✅ Updated {updated} SKILL.md files ({failed} failed)")
if failed_skills:
    print("\nFailed skills (first 10):")
    for skill, msg in failed_skills[:10]:
        print(f"  - {skill}: {msg}")

exit(0 if failed == 0 else 1)
