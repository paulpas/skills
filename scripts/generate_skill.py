#!/usr/bin/env python3
"""
Skill Generation Script for agent-skill-router

Parses user task description to extract domain and topic, then generates
a complete SKILL.md file based on SKILL_FORMAT_SPEC.md with all required
frontmatter fields and content sections.

Usage:
    python3 scripts/generate_skill.py --domain coding --topic my-skill
    python3 scripts/generate_skill.py --task "Create a code review skill"
    python3 scripts/generate_skill.py --domain trading --topic risk-stop-loss --contribute

Environment Variables:
    AUTO_SKILL_MODEL: LLM model for generation (default: gpt-4o-mini)
    AUTO_SKILL_TIMEOUT: Request timeout in seconds (default: 60)
    AUTO_SKILL_MAX_RETRIES: Maximum retries on failure (default: 3)
    AUTO_SKILL_CACHE_DIR: Local cache directory (default: .skill-cache/)
    AUTO_SKILL_CONTRIBUTE: Whether to commit to git (default: false)
    OPENAI_API_KEY: API key for OpenAI (required for LLM generation)

Dependencies:
    - openai (pip install openai)
    - pyyaml (pip install pyyaml)
    - python-dotenv (pip install python-dotenv)
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# Environment variable defaults
DEFAULT_MODEL = os.environ.get("AUTO_SKILL_MODEL", "gpt-4o-mini")
DEFAULT_TIMEOUT = int(os.environ.get("AUTO_SKILL_TIMEOUT", "60"))
DEFAULT_MAX_RETRIES = int(os.environ.get("AUTO_SKILL_MAX_RETRIES", "3"))
DEFAULT_CACHE_DIR = os.environ.get("AUTO_SKILL_CACHE_DIR", ".skill-cache/")
DEFAULT_CONTRIBUTE = os.environ.get("AUTO_SKILL_CONTRIBUTE", "false").lower() == "true"

try:
    import openai
except ImportError:
    print("❌ openai package not installed. Install with: pip install openai")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("❌ PyYAML not installed. Install with: pip install pyyaml")
    sys.exit(1)


class Colors:
    """Terminal color codes."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


class SkillGenerator:
    """Generates SKILL.md files based on user task descriptions."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        cache_dir: str = DEFAULT_CACHE_DIR,
        contribute: bool = DEFAULT_CONTRIBUTE,
    ):
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.cache_dir = Path(cache_dir)
        self.contribute = contribute

        # Initialize OpenAI client
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print(
                f"{Colors.YELLOW}⚠ OPENAI_API_KEY not set. LLM generation will fail.{Colors.RESET}"
            )
            print(
                f"{Colors.YELLOW}⚠ Set it with: export OPENAI_API_KEY=your-key{Colors.RESET}"
            )

        self.client = openai.OpenAI(
            api_key=api_key,
            timeout=timeout,
        )

        # Cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def parse_task_to_domain_topic(self, task: str) -> Tuple[str, str]:
        """Extract domain and topic from task description using LLM."""
        prompt = f"""Extract the domain and topic from this task description.

Task: "{task}"

Return a JSON object with:
- domain: one of (agent, cncf, coding, programming, trading)
- topic: kebab-case topic name (e.g., "code-review", "risk-stop-loss")

Examples:
- Task: "Create a code review skill" → {{"domain": "coding", "topic": "code-review"}}
- Task: "Build a stop loss mechanism" → {{"domain": "trading", "topic": "risk-stop-loss"}}
- Task: "Create a Kubernetes deployment skill" → {{"domain": "cncf", "topic": "kubernetes"}}

Respond with ONLY the JSON object, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a skill categorization expert.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("domain", "coding"), result.get("topic", "new-skill")
        except Exception as e:
            print(f"{Colors.RED}❌ LLM parsing failed: {e}{Colors.RESET}")
            # Fallback: use first word as domain, extract topic from task
            domain = "coding"
            topic = re.sub(r"[^a-z0-9-]", "-", task.lower().strip()[:50])
            topic = re.sub(r"-+", "-", topic).strip("-")
            print(
                f"{Colors.YELLOW}⚠ Using fallback: domain={domain}, topic={topic}{Colors.RESET}"
            )
            return domain, topic

    def generate_skill_content(
        self,
        domain: str,
        topic: str,
        description: str,
        role: Optional[str] = None,
        output_format: Optional[str] = None,
    ) -> str:
        """Generate complete SKILL.md content using LLM."""

        if role is None:
            role = self._get_default_role(domain)
        if output_format is None:
            output_format = self._get_default_output_format(domain)

        # Build the generation prompt
        generation_prompt = f"""You are creating a SKILL.md file for the agent-skill-router repository.

DOMAIN: {domain}
TOPIC: {topic}
DESCRIPTION: {description}
ROLE: {role}
OUTPUT FORMAT: {output_format}

Create a complete, high-quality SKILL.md file following SKILL_FORMAT_SPEC.md requirements:

**YAML Frontmatter Requirements:**
- name: {topic} (must match topic directory name exactly)
- description: Single line, 1-2 sentences. Active verb. Domain-specific terms.
- license: MIT
- compatibility: opencode
- metadata.version: "1.0.0"
- metadata.domain: {domain}
- metadata.role: {role}
- metadata.scope: {self._get_default_scope(domain)}
- metadata.output-format: {output_format}
- metadata.triggers: 5-8 comma-separated keywords (technical + conversational)
- metadata.related-skills: comma-separated related skill names (optional)

**Content Section Requirements:**
1. H1 Title: Human-readable name (not kebab-case)
2. Role/purpose paragraph: 1-3 sentences from model's perspective
3. ## TL;DR Checklist: 3-5 actionable items
4. ## TL;DR for Code Generation: 3-7 specific constraints (REQUIRED for role=implementation)
5. ## When to Use: Bulleted list of concrete situations
6. ## When NOT to Use: Anti-patterns and exclusions (for complex skills)
7. ## Core Workflow: Numbered steps with checkpoints
8. ## Implementation Patterns: Typed Python code with BAD/GOOD examples
9. ## Constraints: MUST DO / MUST NOT DO sections
10. ## Output Template: What the model produces (for review/analysis roles)
11. ## Related Skills: Table if metadata.related-skills exists

**Domain-Specific Requirements:**
{self._get_domain_requirements(domain)}

**Quality Gate Requirements:**
- File size: ≥3000 bytes
- At least 2 code blocks for implementation skills
- No sentinel string "Implementing this specific pattern or feature"
- 3-8 triggers in metadata
- All required sections present
- Real code examples, not placeholders
- Domain-specific constraints in MUST DO/MUST NOT DO

**Important:**
- Use typed Python signatures with docstrings for all functions
- Include BAD vs GOOD code examples
- Add concrete, actionable constraints
- Use domain-specific language and terminology
- Make the skill actionable and specific

Generate the complete SKILL.md file content. Start with --- for YAML frontmatter."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating high-quality AI skill definitions.",
                    },
                    {"role": "user", "content": generation_prompt},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"{Colors.RED}❌ LLM generation failed: {e}{Colors.RESET}")
            return None

    def _get_default_role(self, domain: str) -> str:
        """Get default role for a domain."""
        defaults = {
            "agent": "orchestration",
            "cncf": "reference",
            "coding": "implementation",
            "programming": "reference",
            "trading": "implementation",
        }
        return defaults.get(domain, "implementation")

    def _get_default_scope(self, domain: str) -> str:
        """Get default scope for a domain."""
        defaults = {
            "agent": "orchestration",
            "cncf": "infrastructure",
            "coding": "implementation",
            "programming": "implementation",
            "trading": "implementation",
        }
        return defaults.get(domain, "implementation")

    def _get_default_output_format(self, domain: str) -> str:
        """Get default output format for a domain."""
        defaults = {
            "agent": "analysis",
            "cncf": "manifests",
            "coding": "code",
            "programming": "code",
            "trading": "code",
        }
        return defaults.get(domain, "code")

    def _get_domain_requirements(self, domain: str) -> str:
        """Get domain-specific requirements."""
        requirements = {
            "agent": "- Include ASCII flow diagram for orchestration logic\n- Reference code-philosophy (5 Laws of Elegant Defense)\n- Fallback/error routing for every branching point",
            "cncf": "- Complete working YAML manifest example\n- Architecture diagram or table\n- Common Pitfalls section",
            "coding": "- At least one BAD vs GOOD code example pair\n- MUST DO/MUST NOT DO constraints\n- Reference to standard (OWASP, SOLID, etc.)",
            "trading": "- Python functions with typed signatures and docstrings\n- Risk constraints section\n- File path conventions (risk_engine/, data_pipeline/, execution/, tests/)",
            "programming": "- Implementation in specific language\n- Complexity table\n- Algorithm steps",
        }
        return requirements.get(domain, "")

    def validate_skill_content(self, content: str) -> Tuple[bool, List[str]]:
        """Validate generated skill content against quality gates."""
        errors = []
        warnings = []

        # Check sentinel string
        if "Implementing this specific pattern or feature" in content:
            errors.append(
                "Contains sentinel string 'Implementing this specific pattern or feature'"
            )

        # Check file size
        if len(content) < 3000:
            errors.append(
                f"File size ({len(content)} bytes) is under 3000 bytes minimum"
            )

        # Check YAML frontmatter
        if not content.startswith("---"):
            errors.append("Missing YAML frontmatter delimiter (---)")

        # Check for code blocks in implementation skills
        if role_match := re.search(r"role:\s*(\w+)", content):
            role = role_match.group(1)
            if role == "implementation":
                code_blocks = len(re.findall(r"```", content))
                if code_blocks < 4:  # At least 2 complete code blocks
                    errors.append(
                        f"Implementation skill has fewer than 2 code blocks (found {code_blocks // 2})"
                    )

        # Check triggers in frontmatter
        if triggers_match := re.search(r"triggers:\s*(.+?)(?=\n|$)", content):
            triggers_str = triggers_match.group(1)
            # Count comma-separated items (rough estimate)
            trigger_count = len(
                [t.strip() for t in triggers_str.split(",") if t.strip()]
            )
            if trigger_count < 3:
                warnings.append(f"Only {trigger_count} triggers (recommended: 3-8)")
            elif trigger_count > 8:
                warnings.append(f"{trigger_count} triggers (recommended: 3-8)")

        # Check required sections
        required_sections = ["## When to Use", "## Core Workflow"]
        for section in required_sections:
            if section not in content:
                warnings.append(f"Missing section: {section}")

        return len(errors) == 0, errors + warnings

    def extract_yaml_and_body(self, content: str) -> Tuple[Optional[dict], str]:
        """Extract YAML frontmatter and body from markdown content."""
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

    def save_skill_file(
        self,
        domain: str,
        topic: str,
        content: str,
    ) -> Path:
        """Save skill file to appropriate location."""
        if self.contribute:
            # Save to skills directory
            base_dir = Path("/home/paulpas/git/agent-skill-router")
            skill_dir = base_dir / "skills" / domain / topic
        else:
            # Save to cache directory
            skill_dir = self.cache_dir / domain / topic

        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"

        # Write the skill file
        skill_file.write_text(content, encoding="utf-8")

        return skill_file

    def run_reformat_script(self, skill_file: Path) -> bool:
        """Run reformat_skills.py to normalize YAML."""
        if not self.contribute:
            return True  # Skip if not contributing

        script_path = Path(
            "/home/paulpas/git/agent-skill-router/scripts/reformat_skills.py"
        )
        if not script_path.exists():
            print(
                f"{Colors.YELLOW}⚠ reformat_skills.py not found at {script_path}{Colors.RESET}"
            )
            return False

        try:
            result = os.system(f"python3 {script_path}")
            if result == 0:
                print(
                    f"{Colors.GREEN}✅ reformat_skills.py completed successfully{Colors.RESET}"
                )
                return True
            else:
                print(
                    f"{Colors.RED}❌ reformat_skills.py failed with exit code {result}{Colors.RESET}"
                )
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to run reformat_skills.py: {e}{Colors.RESET}")
            return False

    def run_enhance_triggers_script(self, skill_file: Path) -> bool:
        """Run enhance_triggers.py to improve triggers."""
        if not self.contribute:
            return True  # Skip if not contributing

        script_path = Path(
            "/home/paulpas/git/agent-skill-router/scripts/enhance_triggers.py"
        )
        if not script_path.exists():
            print(
                f"{Colors.YELLOW}⚠ enhance_triggers.py not found at {script_path}{Colors.RESET}"
            )
            return False

        try:
            result = os.system(f"python3 {script_path}")
            if result == 0:
                print(
                    f"{Colors.GREEN}✅ enhance_triggers.py completed successfully{Colors.RESET}"
                )
                return True
            else:
                print(
                    f"{Colors.RED}❌ enhance_triggers.py failed with exit code {result}{Colors.RESET}"
                )
                return False
        except Exception as e:
            print(
                f"{Colors.RED}❌ Failed to run enhance_triggers.py: {e}{Colors.RESET}"
            )
            return False

    def run_generate_index_script(self, skill_file: Path) -> bool:
        """Run generate_index.py to update skills-index.json."""
        if not self.contribute:
            return True  # Skip if not contributing

        script_path = Path(
            "/home/paulpas/git/agent-skill-router/scripts/generate_index.py"
        )
        if not script_path.exists():
            print(
                f"{Colors.YELLOW}⚠ generate_index.py not found at {script_path}{Colors.RESET}"
            )
            return False

        try:
            result = os.system(f"python3 {script_path}")
            if result == 0:
                print(
                    f"{Colors.GREEN}✅ generate_index.py completed successfully{Colors.RESET}"
                )
                return True
            else:
                print(
                    f"{Colors.RED}❌ generate_index.py failed with exit code {result}{Colors.RESET}"
                )
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to run generate_index.py: {e}{Colors.RESET}")
            return False

    def run_validation_script(self, skill_file: Path) -> bool:
        """Run validate_skill.sh for quality checks."""
        script_path = Path(
            "/home/paulpas/git/agent-skill-router/scripts/validate_skill.sh"
        )
        if not script_path.exists():
            print(
                f"{Colors.YELLOW}⚠ validate_skill.sh not found at {script_path}{Colors.RESET}"
            )
            return False

        try:
            result = os.system(f"bash {script_path} {skill_file}")
            if result == 0:
                print(f"{Colors.GREEN}✅ validate_skill.sh passed{Colors.RESET}")
                return True
            else:
                print(
                    f"{Colors.RED}❌ validate_skill.sh failed with exit code {result}{Colors.RESET}"
                )
                return False
        except Exception as e:
            print(f"{Colors.RED}❌ Failed to run validate_skill.sh: {e}{Colors.RESET}")
            return False

    def generate(
        self,
        task: Optional[str] = None,
        domain: Optional[str] = None,
        topic: Optional[str] = None,
        description: Optional[str] = None,
        dry_run: bool = False,
    ) -> Optional[dict]:
        """Generate a skill file and return metadata."""
        print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}Skill Generation{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")

        # Parse task to extract domain and topic if not provided
        if task and not (domain and topic):
            print(f"\n{Colors.CYAN}Parsing task description...{Colors.RESET}")
            domain, topic = self.parse_task_to_domain_topic(task)
            print(
                f"{Colors.GREEN}✓ Extracted: domain={domain}, topic={topic}{Colors.RESET}"
            )

        # Validate domain
        valid_domains = ["agent", "cncf", "coding", "programming", "trading"]
        if domain not in valid_domains:
            print(f"{Colors.RED}❌ Invalid domain: {domain}{Colors.RESET}")
            print(
                f"{Colors.YELLOW}Valid domains: {', '.join(valid_domains)}{Colors.RESET}"
            )
            return None

        # Generate skill content
        print(f"\n{Colors.CYAN}Generating skill content...{Colors.RESET}")
        skill_description = (
            description or f"Creates a skill for {topic} in the {domain} domain."
        )

        for attempt in range(self.max_retries):
            content = self.generate_skill_content(domain, topic, skill_description)

            if content:
                break

            if attempt < self.max_retries - 1:
                print(
                    f"{Colors.YELLOW}⚠ Retry {attempt + 1}/{self.max_retries}...{Colors.RESET}"
                )
                time.sleep(1)
            else:
                print(
                    f"{Colors.RED}❌ Failed after {self.max_retries} attempts{Colors.RESET}"
                )
                return None

        # Validate content
        print(f"\n{Colors.CYAN}Validating skill content...{Colors.RESET}")
        is_valid, issues = self.validate_skill_content(content)

        if not is_valid:
            print(f"{Colors.RED}❌ Quality gate failed:{Colors.RESET}")
            for issue in issues:
                print(f"  {Colors.YELLOW}- {issue}{Colors.RESET}")
            return None

        # Show warnings
        if issues:
            print(f"{Colors.GREEN}✓ Quality gate passed with warnings:{Colors.RESET}")
            for issue in issues:
                print(f"  {Colors.YELLOW}- {issue}{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}✓ Quality gate passed{Colors.RESET}")

        # Dry run mode
        if dry_run:
            print(f"\n{Colors.CYAN}{'=' * 60}{Colors.RESET}")
            print(f"{Colors.BOLD}DRY RUN - No files will be saved{Colors.RESET}")
            print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")
            print(f"\n{Colors.CYAN}Generated SKILL.md content:{Colors.RESET}\n")
            print(content)
            print(
                f"\n{Colors.GREEN}✓ Dry run complete - content validated successfully{Colors.RESET}"
            )
            return {
                "domain": domain,
                "topic": topic,
                "skill_file": None,
                "content": content,
                "size": len(content),
            }

        # Save skill file
        print(f"\n{Colors.CYAN}Saving skill file...{Colors.RESET}")
        skill_file = self.save_skill_file(domain, topic, content)
        print(f"{Colors.GREEN}✓ Saved to: {skill_file}{Colors.RESET}")
        print(f"  Size: {len(content)} bytes")

        # Run automation scripts
        if self.contribute:
            print(f"\n{Colors.CYAN}Running automation scripts...{Colors.RESET}")

            # Reformat
            if not self.run_reformat_script(skill_file):
                print(f"{Colors.YELLOW}⚠ Continuing without reformat...{Colors.RESET}")

            # Enhance triggers
            if not self.run_enhance_triggers_script(skill_file):
                print(
                    f"{Colors.YELLOW}⚠ Continuing without trigger enhancement...{Colors.RESET}"
                )

            # Generate index
            if not self.run_generate_index_script(skill_file):
                print(
                    f"{Colors.YELLOW}⚠ Continuing without index generation...{Colors.RESET}"
                )

        # Run validation script
        if self.contribute:
            print(f"\n{Colors.CYAN}Running validation script...{Colors.RESET}")
            if not self.run_validation_script(skill_file):
                print(
                    f"{Colors.YELLOW}⚠ Validation failed - skill may have issues{Colors.RESET}"
                )
            else:
                print(f"{Colors.GREEN}✓ Skill validated successfully{Colors.RESET}")

        # Summary
        print(f"\n{Colors.CYAN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}Generation Complete{Colors.RESET}")
        print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")
        print(f"\n{Colors.GREEN}✓ Skill generated successfully{Colors.RESET}")
        print(f"  Domain: {domain}")
        print(f"  Topic: {topic}")
        print(f"  File: {skill_file}")
        print(f"  Size: {len(content)} bytes")
        print(f"  Contribute: {self.contribute}")

        return {
            "domain": domain,
            "topic": topic,
            "skill_file": str(skill_file),
            "content": content,
            "size": len(content),
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate SKILL.md files for agent-skill-router"
    )
    parser.add_argument(
        "--task",
        type=str,
        help="Task description to parse for domain and topic",
    )
    parser.add_argument(
        "--domain",
        type=str,
        choices=["agent", "cncf", "coding", "programming", "trading"],
        help="Skill domain",
    )
    parser.add_argument(
        "--topic",
        type=str,
        help="Skill topic (kebab-case)",
    )
    parser.add_argument(
        "--description",
        type=str,
        help="Skill description (overrides auto-generated)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate skill content without saving",
    )
    parser.add_argument(
        "--contribute",
        action="store_true",
        default=DEFAULT_CONTRIBUTE,
        help="Save to skills directory and run automation scripts",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_MODEL,
        help=f"LLM model for generation (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help=f"Maximum retries on failure (default: {DEFAULT_MAX_RETRIES})",
    )
    parser.add_argument(
        "--cache-dir",
        type=str,
        default=DEFAULT_CACHE_DIR,
        help=f"Cache directory (default: {DEFAULT_CACHE_DIR})",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.task and not (args.domain and args.topic):
        parser.error("Either --task or both --domain and --topic must be provided")

    # Create generator
    generator = SkillGenerator(
        model=args.model,
        timeout=args.timeout,
        max_retries=args.max_retries,
        cache_dir=args.cache_dir,
        contribute=args.contribute,
    )

    # Generate skill
    result = generator.generate(
        task=args.task,
        domain=args.domain,
        topic=args.topic,
        description=args.description,
        dry_run=args.dry_run,
    )

    # Exit code
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
