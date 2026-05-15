#!/usr/bin/env python3
"""
Domain discovery module for agent-skill-router.

Replaces hardcoded domain lists across scripts with dynamic filesystem discovery.

Usage:
    from domain_discovery import get_domain_list, get_domain_defaults

    # Get all domains discovered from skills directory
    domains = get_domain_list()
    
    # Get defaults for a specific domain
    defaults = get_domain_defaults('coding')
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Default skills directory (respects SKILLS_DIRECTORY env var)
DEFAULT_SKILLS_DIR = "skills"

# Default domain metadata (used when domain not in domains.json)
DEFAULT_DOMAIN_CONFIG = {
    "agent": {
        "role": "orchestration",
        "scope": "orchestration",
        "content_types": ["guidance", "examples", "do-dont"],
        "description": "Agent orchestration and choreography skills",
    },
    "cncf": {
        "role": "reference",
        "scope": "infrastructure",
        "content_types": ["guidance", "examples", "do-dont", "config"],
        "description": "Cloud Native Computing Foundation skills",
    },
    "coding": {
        "role": "implementation",
        "scope": "implementation",
        "content_types": ["code", "guidance", "do-dont", "examples"],
        "description": "Software coding and implementation skills",
    },
    "programming": {
        "role": "reference",
        "scope": "implementation",
        "content_types": ["code", "guidance", "examples", "diagrams"],
        "description": "Programming concepts and algorithms",
    },
    "trading": {
        "role": "implementation",
        "scope": "implementation",
        "content_types": ["code", "guidance", "config", "do-dont"],
        "description": "Algorithmic trading skills",
    },
}


def get_skills_directory() -> Path:
    """Get the skills directory path.
    
    Returns:
        Path to skills directory
    """
    env_path = os.environ.get("SKILLS_DIRECTORY")
    if env_path:
        return Path(env_path)
    return Path(DEFAULT_SKILLS_DIR)


def _load_config() -> Dict:
    """Load domains.json config if it exists."""
    possible_paths = [
        Path("agent-skill-routing-system/config/domains.json"),
        Path("config/domains.json"),
    ]
    for config_path in possible_paths:
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
    return {}


def get_domain_list(skills_dir: str = DEFAULT_SKILLS_DIR) -> List[str]:
    """Discover domains by scanning the skills directory for subdirectories.
    
    This replaces the hardcoded DOMAINS list found in many scripts.
    
    Args:
        skills_dir: Path to the skills directory (default: "skills")
    
    Returns:
        Sorted list of domain directory names
        
    Example:
        >>> domains = get_domain_list()
        >>> assert isinstance(domains, list)
        >>> assert all(isinstance(d, str) for d in domains)
    """
    skills_path = Path(skills_dir)
    if not skills_path.exists():
        return []
    
    try:
        entries = os.listdir(skills_path)
        domains = sorted([
            entry for entry in entries
            if os.path.isdir(skills_path / entry)
            and not entry.startswith(".")
            and entry not in ("__pycache__", ".git")
        ])
        return domains
    except OSError:
        return []


def get_domain_defaults(domain: str, skills_dir: str = DEFAULT_SKILLS_DIR) -> Dict[str, str]:
    """Get default metadata values for a domain.
    
    Checks domains.json config first, then falls back to built-in defaults.
    Unlike the old get_domain_defaults(), this does NOT raise ValueError for unknown domains.
    
    Args:
        domain: Domain name (e.g., 'coding', 'writing', 'devops')
        skills_dir: Path to the skills directory (for discovery)
    
    Returns:
        Dictionary with default role, scope, content_types, and description.
        Always returns a valid dict — never raises.
    
    Example:
        >>> defaults = get_domain_defaults('coding')
        >>> assert 'role' in defaults
        >>> assert defaults['role'] == 'implementation'
        
        # Unknown domains get sensible defaults
        >>> defaults = get_domain_defaults('unknown-domain')
        >>> assert defaults['role'] == 'reference'
    """
    config = _load_config()
    
    config_domains = config.get("domains", {})
    if domain in config_domains:
        cfg = config_domains[domain]
        return {
            "role": cfg.get("role", "reference"),
            "scope": cfg.get("scope", "implementation"),
            "content_types": cfg.get("content_types", ["code", "guidance"]),
            "description": cfg.get("description", f"Skills in the {domain} domain"),
        }
    
    if domain in DEFAULT_DOMAIN_CONFIG:
        cfg = DEFAULT_DOMAIN_CONFIG[domain]
        return {
            "role": cfg["role"],
            "scope": cfg["scope"],
            "content_types": cfg["content_types"],
            "description": cfg["description"],
        }
    
    return {
        "role": "reference",
        "scope": "implementation",
        "content_types": ["code", "guidance"],
        "description": f"Skills in the {domain} domain",
    }


def get_content_types_for_domain(domain: str, skills_dir: str = DEFAULT_SKILLS_DIR) -> List[str]:
    """Get the content-types for a domain.
    
    Args:
        domain: Domain name
        skills_dir: Path to the skills directory
    
    Returns:
        List of content type strings
    """
    return get_domain_defaults(domain, skills_dir)["content_types"]


def is_valid_domain(domain: str, skills_dir: str = DEFAULT_SKILLS_DIR) -> bool:
    """Check if a domain exists as a directory in the skills folder.
    
    Args:
        domain: Domain name to check
        skills_dir: Path to the skills directory
    
    Returns:
        True if domain directory exists, False otherwise
    """
    skills_path = Path(skills_dir)
    return (skills_path / domain).is_dir()


if __name__ == "__main__":
    import json
    
    print("=" * 50)
    print("Domain Discovery")
    print("=" * 50)
    
    skills_dir = str(get_skills_directory())
    domains = get_domain_list(skills_dir)
    
    print(f"Skills directory: {skills_dir}")
    print(f"Discovered domains: {domains}")
    print()
    
    for domain in domains:
        defaults = get_domain_defaults(domain, skills_dir)
        print(f"  {domain}:")
        print(f"    role: {defaults['role']}")
        print(f"    scope: {defaults['scope']}")
        print(f"    content_types: {defaults['content_types']}")
        print(f"    description: {defaults['description']}")
