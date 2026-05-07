#!/usr/bin/env python3
"""
reformat_skills.py - Validates and normalizes YAML frontmatter across all skills.

This script ensures consistency across all skills in the agent-skill-router repository.
It validates YAML syntax, normalizes formatting, and reports errors.

Usage:
    python3 scripts/reformat_skills.py [--directory /path/to/skills]

Environment Variables:
    SKILLS_DIRECTORY: Path to skills directory (default: /home/paulpas/git/agent-skill-router/skills)

Dependencies:
    - pyyaml (pip install pyyaml)
"""

import argparse
import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any


class Colors:
    """Terminal color codes."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


class SkillFormatter:
    """Validates and normalizes skill YAML frontmatter."""

    # Required frontmatter fields
    REQUIRED_FIELDS = ["name", "description", "metadata"]

    # Required metadata fields
    REQUIRED_METADATA_FIELDS = [
        "version",
        "domain",
        "triggers",
        "role",
        "scope",
        "output-format",
    ]

    # Optional metadata fields with defaults
    OPTIONAL_METADATA = {
        "related-skills": "",
        "author": "",
        "source": "",
    }

    # Domain-specific defaults
    DOMAIN_DEFAULTS = {
        "agent": {
            "role": "orchestration",
            "scope": "orchestration",
            "output-format": "analysis",
        },
        "cncf": {
            "role": "reference",
            "scope": "infrastructure",
            "output-format": "manifests",
        },
        "coding": {
            "role": "implementation",
            "scope": "implementation",
            "output-format": "code",
        },
        "programming": {
            "role": "reference",
            "scope": "implementation",
            "output-format": "code",
        },
        "trading": {
            "role": "implementation",
            "scope": "implementation",
            "output-format": "code",
        },
    }

    def __init__(self, skills_dir: str = None):
        if skills_dir is None:
            skills_dir = os.environ.get(
                "SKILLS_DIRECTORY", "/home/paulpas/git/agent-skill-router/skills"
            )
        self.skills_dir = Path(skills_dir)
        self.results: List[Dict[str, Any]] = []

    def parse_yaml_frontmatter(self, content: str) -> Tuple[Optional[Dict], str]:
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
        except yaml.YAMLError as e:
            return None, content

    def normalize_triggers(self, triggers: Any) -> str:
        """Normalize triggers to a comma-separated string."""
        if isinstance(triggers, str):
            # Already a string, ensure proper formatting
            trigger_list = [t.strip() for t in triggers.split(",") if t.strip()]
            return ", ".join(trigger_list)
        elif isinstance(triggers, list):
            # Convert list to comma-separated string
            return ", ".join(str(t).strip() for t in triggers if t)
        else:
            return ""

    def normalize_metadata(self, metadata: Dict, domain: str) -> Dict:
        """Normalize metadata with defaults."""
        normalized = {}

        # Required fields
        for field in self.REQUIRED_METADATA_FIELDS:
            if field in metadata:
                normalized[field] = metadata[field]
            elif (
                domain in self.DOMAIN_DEFAULTS and field in self.DOMAIN_DEFAULTS[domain]
            ):
                normalized[field] = self.DOMAIN_DEFAULTS[domain][field]
            else:
                normalized[field] = ""

        # Optional fields
        for field, default in self.OPTIONAL_METADATA.items():
            normalized[field] = metadata.get(field, default)

        # Ensure triggers is a string
        if "triggers" in normalized and not isinstance(normalized["triggers"], str):
            normalized["triggers"] = self.normalize_triggers(normalized["triggers"])

        return normalized

    def normalize_frontmatter(self, frontmatter: Dict) -> Dict:
        """Normalize the entire frontmatter."""
        normalized = {}

        # Required top-level fields
        for field in self.REQUIRED_FIELDS:
            if field in frontmatter:
                normalized[field] = frontmatter[field]

        # Normalize metadata
        if "metadata" in frontmatter and isinstance(frontmatter["metadata"], dict):
            domain = frontmatter["metadata"].get("domain", "coding")
            normalized["metadata"] = self.normalize_metadata(
                frontmatter["metadata"], domain
            )

        # Add optional fields
        if "license" in frontmatter:
            normalized["license"] = frontmatter["license"]
        if "compatibility" in frontmatter:
            normalized["compatibility"] = frontmatter["compatibility"]

        return normalized

    def format_yaml(self, data: Dict, indent: int = 0) -> str:
        """Format YAML with consistent indentation."""
        spaces = "  " * indent
        result = []

        for key, value in data.items():
            if isinstance(value, dict):
                result.append(f"{spaces}{key}:")
                result.append(self.format_yaml(value, indent + 1))
            elif isinstance(value, list):
                if len(value) == 0:
                    result.append(f"{spaces}{key}: []")
                else:
                    result.append(f"{spaces}{key}:")
                    for item in value:
                        if isinstance(item, dict):
                            # Multi-line dict format
                            result.append(f"{spaces}  - |")
                            for k, v in item.items():
                                result.append(f"{spaces}    {k}: {v}")
                        else:
                            result.append(f"{spaces}  - {item}")
            elif isinstance(value, str):
                # Escape special characters if needed
                if "\n" in value or ":" in value or "'" in value or '"' in value:
                    # Use block scalar for multi-line strings
                    result.append(f"{spaces}{key}: |")
                    for line in value.split("\n"):
                        result.append(f"{spaces}  {line}")
                else:
                    # Escape single quotes in strings
                    escaped = value.replace("'", "\\'")
                    result.append(f"{spaces}{key}: '{escaped}'")
            else:
                result.append(f"{spaces}{key}: {value}")

        return "\n".join(result)

    def validate_skill(self, file_path: Path) -> Dict[str, Any]:
        """Validate a single skill file."""
        result = {
            "path": str(file_path),
            "valid": True,
            "errors": [],
            "warnings": [],
            "normalized": False,
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

        yaml_frontmatter, body = self.parse_yaml_frontmatter(content)

        if yaml_frontmatter is None:
            result["valid"] = False
            result["errors"].append("Invalid YAML syntax in frontmatter")
            return result

        # Check required fields
        for field in self.REQUIRED_FIELDS:
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
                for field in self.REQUIRED_METADATA_FIELDS:
                    if field not in metadata:
                        result["warnings"].append(
                            f"Missing optional metadata field: {field}"
                        )

        # Check triggers count
        if (
            "metadata" in yaml_frontmatter
            and "triggers" in yaml_frontmatter["metadata"]
        ):
            triggers = yaml_frontmatter["metadata"]["triggers"]
            trigger_list = []
            if isinstance(triggers, str):
                trigger_list = [t.strip() for t in triggers.split(",") if t.strip()]
            elif isinstance(triggers, list):
                trigger_list = [str(t).strip() for t in triggers if t]

            if len(trigger_list) < 3:
                result["warnings"].append(
                    f"Only {len(trigger_list)} triggers (recommended: 3-8)"
                )

        # Check file size
        if len(content) < 3000:
            result["warnings"].append(
                f"File size ({len(content)} bytes) is under 3000 bytes"
            )

        # Check for sentinel string
        if "Implementing this specific pattern or feature" in content:
            result["valid"] = False
            result["errors"].append(
                "Contains sentinel string 'Implementing this specific pattern or feature'"
            )

        return result

    def normalize_file(self, file_path: Path) -> bool:
        """Normalize a skill file's YAML frontmatter."""
        try:
            content = file_path.read_text(encoding="utf-8")

            # Parse existing frontmatter
            yaml_frontmatter, body = self.parse_yaml_frontmatter(content)

            if yaml_frontmatter is None:
                return False

            # Normalize frontmatter
            normalized_frontmatter = self.normalize_frontmatter(yaml_frontmatter)

            # Format YAML
            yaml_string = self.format_yaml(normalized_frontmatter)

            # Reconstruct file with normalized frontmatter
            new_content = f"---\n{yaml_string}\n---\n{body}"

            # Write back
            file_path.write_text(new_content, encoding="utf-8")

            return True
        except Exception as e:
            print(f"{Colors.RED}Error normalizing {file_path}: {e}{Colors.RESET}")
            return False

    def process_all_skills(self) -> List[Dict[str, Any]]:
        """Process all skill files in the directory."""
        if not self.skills_dir.exists():
            print(
                f"{Colors.RED}Error: Skills directory not found: {self.skills_dir}{Colors.RESET}"
            )
            return []

        # Find all SKILL.md files
        skill_files = list(self.skills_dir.glob("**/SKILL.md"))

        print(
            f"{Colors.CYAN}Found {len(skill_files)} skill files to process{Colors.RESET}"
        )

        results = []
        for skill_file in skill_files:
            result = self.validate_skill(skill_file)
            results.append(result)

            if result["valid"]:
                print(
                    f"{Colors.GREEN}✓ {skill_file.relative_to(self.skills_dir)}{Colors.RESET}"
                )
            else:
                print(
                    f"{Colors.RED}✗ {skill_file.relative_to(self.skills_dir)}{Colors.RESET}"
                )
                for error in result["errors"]:
                    print(f"  {Colors.RED}- {error}{Colors.RESET}")
                for warning in result["warnings"]:
                    print(f"  {Colors.YELLOW}- {warning}{Colors.RESET}")

        return results

    def print_summary(self, results: List[Dict[str, Any]]) -> int:
        """Print validation summary and return exit code."""
        total = len(results)
        valid_count = sum(1 for r in results if r["valid"])
        invalid_count = total - valid_count
        skills_with_errors = [r for r in results if not r["valid"]]
        skills_with_warnings = [r for r in results if r["warnings"]]

        print()
        print("=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Total skills: {total}")
        print(f"Valid skills: {valid_count}")
        print(f"Skills with errors: {invalid_count}")
        print(f"Skills with warnings: {len(skills_with_warnings)}")
        print()

        if skills_with_errors:
            print("-" * 70)
            print(f"{Colors.RED}SKILLS WITH ERRORS{Colors.RESET}")
            print("-" * 70)
            for result in skills_with_errors:
                print(f"\n{Colors.RED}{result['path']}{Colors.RESET}")
                for error in result["errors"]:
                    print(f"  {Colors.RED}- {error}{Colors.RESET}")

        if skills_with_warnings:
            print()
            print("-" * 70)
            print(f"{Colors.YELLOW}SKILLS WITH WARNINGS{Colors.RESET}")
            print("-" * 70)
            for result in skills_with_warnings:
                print(f"\n{Colors.YELLOW}{result['path']}{Colors.RESET}")
                for warning in result["warnings"]:
                    print(f"  {Colors.YELLOW}- {warning}{Colors.RESET}")

        print()
        if invalid_count == 0:
            print(f"{Colors.GREEN}✓ VALIDATION PASSED{Colors.RESET}")
        else:
            print(
                f"{Colors.RED}✗ VALIDATION FAILED: {invalid_count} skills have errors{Colors.RESET}"
            )

        return 1 if invalid_count > 0 else 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate and normalize skill YAML frontmatter"
    )
    parser.add_argument(
        "--directory",
        type=str,
        help="Path to skills directory",
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Normalize YAML frontmatter (experimental)",
    )

    args = parser.parse_args()

    # Initialize formatter
    formatter = SkillFormatter(args.directory)

    # Process all skills
    results = formatter.process_all_skills()

    # Print summary
    exit_code = formatter.print_summary(results)

    # Normalize if requested
    if args.normalize:
        print()
        print(f"{Colors.CYAN}Normalizing YAML frontmatter...{Colors.RESET}")
        for result in results:
            if result["valid"]:
                file_path = Path(result["path"])
                if formatter.normalize_file(file_path):
                    print(f"{Colors.GREEN}✓ Normalized: {result['path']}{Colors.RESET}")
                else:
                    print(
                        f"{Colors.RED}✗ Failed to normalize: {result['path']}{Colors.RESET}"
                    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
