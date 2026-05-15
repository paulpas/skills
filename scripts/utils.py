#!/usr/bin/env python3
"""
Shared utilities for agent-skill-router scripts.

This module consolidates common functionality extracted from multiple scripts
in the scripts/ directory. It provides:

- YAML Frontmatter Parsing
- Colored Terminal Output
- Domain Configuration
- Path Utilities
- YAML Formatting
- Trigger Utilities
- File Writing
- Custom Error Handling

All functions follow the 5 Laws of Elegant Defense:
1. Early Exit - Guard clauses handle edge cases at top
2. Parse Don't Validate - Data parsed at boundaries, trusted internally
3. Atomic Predictability - Pure functions where possible
4. Fail Fast - Invalid states halt with descriptive errors
5. Intentional Naming - Code reads like English
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from domain_discovery import get_domain_list, get_domain_defaults as _get_dd_defaults

try:
    import yaml
except ImportError:
    print(
        "❌ PyYAML not installed. Install with: pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(1)


# =============================================================================
# 1. COLORS CLASS
# =============================================================================


class Colors:
    """Terminal color codes for colored output.

    Usage:
        print(f"{Colors.GREEN}Success{Colors.RESET}")
        print(f"{Colors.RED}Error{Colors.RESET}")

    Attributes:
        RED: Red color code
        GREEN: Green color code
        YELLOW: Yellow color code
        BLUE: Blue color code
        CYAN: Cyan color code
        RESET: Reset color code
        BOLD: Bold text code
    """

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


# =============================================================================
# 2. DOMAIN CONFIGURATION
# =============================================================================

# Dynamically discovered from skills/ directory — no hardcoded list
# DOMAINS is now a function for lazy evaluation
def get_domains(skills_dir: Optional[str] = None) -> List[str]:
    """Get the list of domains by scanning the skills directory.
    
    Replaces the old hardcoded DOMAINS list.
    
    Args:
        skills_dir: Optional path to skills directory (uses env var or default)
    
    Returns:
        Sorted list of domain directory names
    """
    return get_domain_list(skills_dir or str(get_skills_directory()))


# Keep DOMAIN_DEFAULTS for backward compatibility with existing code
# that imports it directly. New code should use domain_discovery.get_domain_defaults().
DOMAIN_DEFAULTS: Dict[str, Dict[str, str]] = {
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


def get_domain_defaults(domain: str) -> Dict[str, str]:
    """Get default metadata values for a domain.
    
    Now accepts any domain name — returns sensible defaults for unknown domains.
    For known domains, returns values from domain_discovery module.
    
    Args:
        domain: Domain name (e.g., 'agent', 'coding', 'writing')
    
    Returns:
        Dictionary with default role, scope, and output-format.
        Never raises — always returns a valid dict.
    
    Examples:
        >>> defaults = get_domain_defaults('coding')
        >>> defaults['role']
        'implementation'
        >>> defaults = get_domain_defaults('unknown-domain')
        >>> defaults['role']
        'reference'
    """
    # Use domain_discovery for defaults
    dd = _get_dd_defaults(domain)
    return {
        "role": dd["role"],
        "scope": dd["scope"],
        "output-format": dd["role"] if dd["role"] in ("implementation", "orchestration") else "code",
    }


# =============================================================================
# 3. PATH UTILITIES
# =============================================================================


def get_skills_directory() -> Path:
    """Get the skills directory path.

    Checks environment variable first, then defaults to standard location.

    Returns:
        Path to skills directory

    Examples:
        >>> skills_dir = get_skills_directory()
        >>> skills_dir.name
        'skills'
    """
    # Parse at boundary - get env var, default if not set
    env_path = os.environ.get("SKILLS_DIRECTORY")
    if env_path:
        return Path(env_path)

    # Fail fast with default if env var not set
    return Path("skills")


def get_skill_path(domain: str, name: str) -> Path:
    """Get the path to a skill's SKILL.md file.

    Args:
        domain: Domain name (e.g., 'coding')
        name: Skill name (e.g., 'code-review')

    Returns:
        Full path to SKILL.md file

    Raises:
        ValueError: If domain is not recognized

    Examples:
        >>> path = get_skill_path('coding', 'code-review')
        >>> path.name
        'SKILL.md'
    """
    # Accept any directory name — domains are dynamically discovered
    skills_dir = get_skills_directory()
    domain_path = skills_dir / domain
    if not domain_path.is_dir():
        raise ValueError(f"Domain directory does not exist: {domain}")

    return skills_dir / domain / name / "SKILL.md"


# =============================================================================
# 4. YAML FRONTMATTER PARSING
# =============================================================================


def parse_yaml_frontmatter(content: str) -> Tuple[Optional[Dict], str, bool]:
    """Extract YAML frontmatter and body from Markdown content.

    Follows the standard Markdown frontmatter format:
    ---
    yaml_content
    ---
    markdown_body

    Args:
        content: Full Markdown content with potential frontmatter

    Returns:
        Tuple of (yaml_frontmatter_dict or None, markdown_body, error)

    Note:
        This function parses data at the boundary and returns trusted types.
        Once parsed, the data is considered valid and trusted internally.
        The third return value indicates if parsing failed.

    Examples:
        >>> content = "---\\nname: test\\n---\\n# Body"
        >>> yaml_data, body, error = parse_yaml_frontmatter(content)
        >>> yaml_data['name']
        'test'
        >>> body
        '# Body'
        >>> error
        False

        >>> content = "# No frontmatter"
        >>> yaml_data, body, error = parse_yaml_frontmatter(content)
        >>> yaml_data is None
        True
        >>> error
        False

        >>> content = "---\\ninvalid: yaml: content:\\n---\\nbody"
        >>> yaml_data, body, error = parse_yaml_frontmatter(content)
        >>> yaml_data is None
        True
        >>> error
        True
    """
    # Early Exit - Handle edge cases at top
    if not content or not isinstance(content, str):
        return None, "", False

    if not content.startswith("---"):
        return None, content, False

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content, False

    try:
        yaml_frontmatter = yaml.safe_load(parts[1])
        body = parts[2]
        return yaml_frontmatter, body, False
    except yaml.YAMLError as e:
        print(
            f"⚠️  YAML parse error in frontmatter: {e}",
            file=sys.stderr,
        )
        return None, "", True


# =============================================================================
# 5. TRIGGER UTILITIES
# =============================================================================


def normalize_triggers(triggers: Any) -> List[str]:
    """Normalize triggers to a list of strings.

    Handles multiple input formats:
    - String: comma-separated values
    - List: converts to list
    - None or other: returns empty list

    Args:
        triggers: Raw triggers in various formats

    Returns:
        List of normalized trigger strings ( stripped, non-empty)

    Examples:
        >>> normalize_triggers("stop loss, trailing stop, ATR")
        ['stop loss', 'trailing stop', 'ATR']

        >>> normalize_triggers(["one", " two ", ""])
        ['one', 'two']

        >>> normalize_triggers(None)
        []
    """
    # Parse at boundary - handle different input formats
    if isinstance(triggers, str):
        # Split by comma and strip whitespace
        return [t.strip() for t in triggers.split(",") if t.strip()]

    if isinstance(triggers, list):
        # Convert list items to strings and filter empty
        return [str(t).strip() for t in triggers if t]

    # Invalid type - fail fast with empty list
    return []


# =============================================================================
# 6. YAML FORMATTING
# =============================================================================


def format_yaml(data: Dict, indent: int = 0) -> str:
    """Format a dictionary as YAML with consistent indentation.

    Args:
        data: Dictionary to format
        indent: Initial indentation level (default: 0)

    Returns:
        Formatted YAML string

    Examples:
        >>> result = format_yaml({'name': 'test', 'count': 5})
        >>> 'name: test' in result
        True
    """
    spaces = "  " * indent
    result: List[str] = []

    for key, value in data.items():
        if isinstance(value, dict):
            result.append(f"{spaces}{key}:")
            result.append(format_yaml(value, indent + 1))
        elif isinstance(value, list):
            if len(value) == 0:
                result.append(f"{spaces}{key}: []")
            else:
                result.append(f"{spaces}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        result.append(f"{spaces}  - |")
                        for k, v in item.items():
                            result.append(f"{spaces}    {k}: {v}")
                    else:
                        # Type guard for list items
                        if not isinstance(item, (str, int, float, bool, type(None))):
                            item = str(item)
                        result.append(f"{spaces}  - {item}")
        elif isinstance(value, str):
            if "\n" in value or ":" in value or "'" in value or '"' in value:
                result.append(f"{spaces}{key}: |")
                for line in value.split("\n"):
                    result.append(f"{spaces}  {line}")
            else:
                escaped = value.replace("'", "\\'")
                result.append(f"{spaces}{key}: '{escaped}'")
        else:
            result.append(f"{spaces}{key}: {value}")

    return "\n".join(result)


# =============================================================================
# 7. FILE WRITING
# =============================================================================


def write_skill_file(path: Path, frontmatter: Dict, body: str) -> None:
    """Write a skill file with YAML frontmatter and markdown body.

    Args:
        path: Path to SKILL.md file
        frontmatter: Dictionary containing frontmatter data
        body: Markdown content after frontmatter

    Raises:
        IOError: If file cannot be written

    Examples:
        >>> from pathlib import Path
        >>> import tempfile
        >>> with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        ...     path = Path(f.name)
        >>> write_skill_file(path, {'name': 'test'}, '# Body')
        >>> content = path.read_text()
        >>> 'name: test' in content
        True
    """
    # Parse the frontmatter into YAML
    yaml_string = format_yaml(frontmatter)

    # Reconstruct file with normalized frontmatter
    new_content = f"---\n{yaml_string}\n---\n{body}"

    # Write back
    path.write_text(new_content, encoding="utf-8")


# =============================================================================
# 8. ERROR HANDLING
# =============================================================================


class InvalidSkillError(ValueError):
    """Raised when a skill file is invalid or malformed."""

    pass


class YAMLParseError(ValueError):
    """Raised when YAML parsing fails."""

    pass


class ValidationError(ValueError):
    """Raised when skill validation fails."""

    pass


def format_error(script: str, domain: str, skill: str, message: str) -> str:
    """Format an error message with context.

    Args:
        script: Name of the script where error occurred
        domain: Skill domain (e.g., 'coding')
        skill: Skill name
        message: Error description

    Returns:
        Formatted error message string

    Examples:
        >>> format_error('reformat.py', 'coding', 'code-review', 'Missing name')
        '[reformat.py] coding/code-review: Missing name'
    """
    # Fail Fast - Don't try to recover, just format clearly
    return f"[{script}] {domain}/{skill}: {message}"


# =============================================================================
# 9. HELPER FUNCTIONS
# =============================================================================


def truncate_at_word_boundary(text: str, max_length: int = 60) -> str:
    """Truncate text at word boundary with ellipsis if needed.

    Args:
        text: Text to truncate
        max_length: Maximum length (default: 60)

    Returns:
        Truncated text with ellipsis if needed

    Examples:
        >>> truncate_at_word_boundary("this is a long text", 10)
        'this is a...'
    """
    if len(text) <= max_length:
        return text

    truncated = text[:max_length]
    last_space = truncated.rfind(" ")

    if last_space > 0:
        return text[:last_space] + "..."
    else:
        return text[: max_length - 3] + "..."


def extract_h1_title(content: str) -> Optional[str]:
    """Extract H1 title from markdown content.

    Args:
        content: Markdown content

    Returns:
        H1 title text or None if not found

    Examples:
        >>> extract_h1_title("# My Title\\n\\nBody")
        'My Title'
        >>> extract_h1_title("## Subtitle")
        None
    """
    for line in content.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return None
