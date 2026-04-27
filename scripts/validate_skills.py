#!/usr/bin/env python3
"""
Validate YAML frontmatter in all SKILL.md files.
Checks for required fields and proper formatting.
"""

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime


def parse_yaml_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from Markdown content."""
    if not content.startswith("---"):
        return None, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content

    try:
        yaml_frontmatter = yaml.safe_load(parts[1])
        body = parts[2]
        return yaml_frontmatter, body
    except yaml.YAMLError:
        return None, content


def validate_skill(file_path: Path) -> dict:
    """Validate a single skill file."""
    result = {
        "path": str(file_path),
        "valid": True,
        "errors": [],
        "warnings": [],
        "updated": False,
    }

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        result["valid"] = False
        result["errors"].append(f"Failed to read file: {e}")
        return result

    if not content.startswith("---"):
        result["valid"] = False
        result["errors"].append("Missing YAML frontmatter delimiter (---)")
        return result

    yaml_frontmatter, body = parse_yaml_frontmatter(content)

    if yaml_frontmatter is None:
        result["valid"] = False
        result["errors"].append("Invalid YAML syntax in frontmatter")
        return result

    # Check required fields
    required_fields = ["name", "description", "metadata"]
    for field in required_fields:
        if field not in yaml_frontmatter:
            result["valid"] = False
            result["errors"].append(f"Missing required field: {field}")

    # Validate metadata
    if "metadata" in yaml_frontmatter:
        metadata = yaml_frontmatter["metadata"]
        if not isinstance(metadata, dict):
            result["valid"] = False
            result["errors"].append("metadata must be a dictionary")
        else:
            required_meta_fields = [
                "version",
                "domain",
                "triggers",
                "role",
                "scope",
                "output-format",
            ]
            for field in required_meta_fields:
                if field not in metadata:
                    result["warnings"].append(
                        f"Missing optional metadata field: {field}"
                    )

    # Check triggers
    if "metadata" in yaml_frontmatter and "triggers" in yaml_frontmatter["metadata"]:
        triggers = yaml_frontmatter["metadata"]["triggers"]
        if isinstance(triggers, str):
            trigger_list = [t.strip() for t in triggers.split(",")]
            if len(trigger_list) < 3:
                result["warnings"].append(
                    f"Only {len(trigger_list)} triggers (recommended: 5-8)"
                )
            elif len(trigger_list) > 8:
                result["warnings"].append(
                    f"{len(trigger_list)} triggers (recommended: 5-8)"
                )

    # Check content structure
    required_sections = ["When to Use", "Core Workflow"]
    for section in required_sections:
        if f"## {section}" not in body and f"## {section}" not in body:
            result["warnings"].append(f"Missing section: {section}")

    # Check file size
    if len(content) < 3000:
        result["warnings"].append(
            f"File size ({len(content)} bytes) is under 3000 bytes (may be a stub)"
        )

    return result


def main():
    """Main validation function."""
    print("=" * 70)
    print("SKILL VALIDATION REPORT")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    skills_dir = Path("/home/paulpas/git/agent-skill-router/skills")

    if not skills_dir.exists():
        print(f"Error: Skills directory not found: {skills_dir}")
        sys.exit(1)

    # Find all SKILL.md files
    skill_files = list(skills_dir.glob("**/SKILL.md"))

    print(f"Found {len(skill_files)} skill files to validate")
    print()

    # Validate each skill
    results = []
    for skill_file in skill_files:
        result = validate_skill(skill_file)
        results.append(result)

    # Summary statistics
    total = len(results)
    valid_count = sum(1 for r in results if r["valid"] and len(r["errors"]) == 0)
    invalid_count = total - valid_count

    skills_with_errors = [r for r in results if not r["valid"] or len(r["errors"]) > 0]
    skills_with_warnings = [r for r in results if r["warnings"]]

    print("-" * 70)
    print("SUMMARY")
    print("-" * 70)
    print(f"Total skills validated: {total}")
    print(f"Valid skills: {valid_count}")
    print(f"Skills with errors: {invalid_count}")
    print(f"Skills with warnings: {len(skills_with_warnings)}")
    print()

    # Errors
    if skills_with_errors:
        print("-" * 70)
        print("SKILLS WITH ERRORS")
        print("-" * 70)
        for result in skills_with_errors:
            print(f"\n❌ {result['path']}")
            for error in result["errors"]:
                print(f"  - {error}")
        print()

    # Warnings
    if skills_with_warnings:
        print("-" * 70)
        print("SKILLS WITH WARNINGS")
        print("-" * 70)
        for result in skills_with_warnings:
            print(f"\n⚠️  {result['path']}")
            for warning in result["warnings"]:
                print(f"  - {warning}")
        print()

    # Final status
    print("-" * 70)
    if invalid_count == 0:
        print("✅ VALIDATION PASSED: All skills are valid")
    else:
        print(f"❌ VALIDATION FAILED: {invalid_count} skills have errors")
    print("=" * 70)

    # Exit code
    sys.exit(1 if invalid_count > 0 else 0)


if __name__ == "__main__":
    main()
