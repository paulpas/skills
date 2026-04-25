#!/usr/bin/env python3
"""Remove numbered prefixes from skill names and update metadata."""

import re
import yaml
from pathlib import Path

SKILLS_ROOT = Path("/home/paulpas/git/agent-skill-router/skills")
DOMAINS = ["agent", "cncf", "coding", "programming", "trading"]

# Map old names to new names for updating related-skills
old_to_new_map = {}

# Pattern to match numbered prefix
# Matches: 00-, 007-, 1-, 123-, etc. or 00_, 007_, etc.
prefix_pattern = re.compile(r"^(\d+)[_-](.+)$")

print("🔍 Phase 1: Building name mapping...")

for domain_dir in SKILLS_ROOT.iterdir():
    if not domain_dir.is_dir() or domain_dir.name not in DOMAINS:
        continue

    domain = domain_dir.name

    for skill_dir in domain_dir.iterdir():
        if not skill_dir.is_dir():
            continue

        skill_name = skill_dir.name
        match = prefix_pattern.match(skill_name)

        if match:
            prefix, clean_name = match.groups()
            old_to_new_map[skill_name] = clean_name
            print(f"  {domain}/{skill_name} → {domain}/{clean_name}")

print(f"✅ Found {len(old_to_new_map)} skills to rename")

print("\n🔄 Phase 2: Renaming directories...")

renamed_count = 0
for domain_dir in SKILLS_ROOT.iterdir():
    if not domain_dir.is_dir() or domain_dir.name not in DOMAINS:
        continue

    domain = domain_dir.name

    for skill_dir in sorted(domain_dir.iterdir()):
        if not skill_dir.is_dir():
            continue

        skill_name = skill_dir.name
        match = prefix_pattern.match(skill_name)

        if match:
            prefix, clean_name = match.groups()
            new_path = skill_dir.parent / clean_name

            try:
                # Rename directory
                skill_dir.rename(new_path)
                renamed_count += 1
                print(f"  ✅ {domain}/{skill_name} → {domain}/{clean_name}")
            except Exception as e:
                print(f"  ❌ Error renaming {skill_name}: {e}")

print(f"✅ Renamed {renamed_count} directories")

print("\n🔄 Phase 3: Updating SKILL.md files...")

updated_count = 0
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

        try:
            with open(skill_md, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract frontmatter
            if not content.startswith("---"):
                continue

            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            yaml_str = parts[1]
            md_content = parts[2]

            # Parse YAML
            try:
                metadata = yaml.safe_load(yaml_str)
            except yaml.YAMLError:
                continue

            changed = False

            # Update name field if it has numbered prefix
            if "name" in metadata:
                old_name = metadata["name"]
                match = prefix_pattern.match(old_name)
                if match:
                    prefix, clean_name = match.groups()
                    metadata["name"] = clean_name
                    changed = True
                    print(f"  ✅ {skill_dir.name}/SKILL.md: updated name field")

            # Update related-skills to reference cleaned names
            if "metadata" in metadata and "related-skills" in metadata["metadata"]:
                related = metadata["metadata"]["related-skills"]
                if related:  # Check if not None
                    updated_related = []

                    for rel in related.split(","):
                        rel = rel.strip()
                        if not rel:
                            continue

                        # Check if it's a domain:skillname reference
                        if ":" in rel:
                            domain_part, skill_part = rel.split(":", 1)
                            # Clean the skill part if it has numbered prefix
                            match = prefix_pattern.match(skill_part)
                            if match:
                                prefix, clean = match.groups()
                                rel = f"{domain_part}:{clean}"
                                changed = True
                        else:
                            # Check if it's in our mapping
                            if rel in old_to_new_map:
                                rel = old_to_new_map[rel]
                                changed = True

                        updated_related.append(rel)

                    if changed:
                        metadata["metadata"]["related-skills"] = ", ".join(
                            updated_related
                        )

            # Write back if changed
            if changed:
                yaml_updated = yaml.dump(
                    metadata, default_flow_style=False, allow_unicode=True
                )
                new_content = f"---\n{yaml_updated}---\n{md_content}"

                with open(skill_md, "w", encoding="utf-8") as f:
                    f.write(new_content)

                updated_count += 1

        except Exception as e:
            print(f"  ❌ Error updating {skill_dir.name}: {str(e)}")

print(f"✅ Updated {updated_count} SKILL.md files")
print("✅ Phase 3 complete")
