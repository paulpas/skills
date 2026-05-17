#!/usr/bin/env python3
"""
fix_skill_quality.py - Audit and fix quality issues across all SKILL.md files.

Fixes:
  1. Add missing `content-types` frontmatter (domain defaults)
  2. Add missing `maturity: stable` and `completeness: 95` frontmatter
  3. Add missing `Constraints` section (domain-specific)
  4. For trading skills: add When to Use, Core Workflow, Constraints
  5. For cncf skills: add When to Use, Core Workflow where missing

Uses PyYAML for safe frontmatter parsing and rewriting.

Usage:
  python3 scripts/fix_skill_quality.py [--dry-run] [--skills-dir SKILLS_DIR]
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

# ─── Domain Defaults ────────────────────────────────────────────────────────────

DOMAIN_CONTENT_TYPES: dict[str, list[str]] = {
    "agent": ["guidance", "examples", "do-dont"],
    "cncf": ["guidance", "examples", "do-dont", "config"],
    "coding": ["code", "guidance", "do-dont", "examples"],
    "trading": ["code", "guidance", "config", "do-dont"],
    "programming": ["code", "guidance", "examples", "diagrams"],
    "writing": ["guidance", "examples", "do-dont"],
}

DOMAIN_CONSTRAINTS: dict[str, dict[str, list[str]]] = {
    "agent": {
        "must_do": [
            "Ensure each agent handles a single responsibility",
            "Include explicit fallback/error routing for every branching point",
            "Reference code-philosophy (5 Laws of Elegant Defense)",
        ],
        "must_not_do": [
            "Use fixed thresholds without adaptive tuning",
            "Ignore low-confidence fallback scenarios",
            "Skip execution history tracking",
        ],
    },
    "cncf": {
        "must_do": [
            "Include at least one complete working YAML manifest example",
            "Note when content is auto-generated vs. manually verified",
            "Reference relevant CNCF project documentation",
        ],
        "must_not_do": [
            "Deploy manifests without testing in a staging environment first",
            "Use deprecated API versions (e.g., apps/v1beta1)",
            "Omit resource limits and requests in Kubernetes manifests",
        ],
    },
    "coding": {
        "must_do": [
            "Include at least one BAD/GOOD code example pair",
            "Reference a relevant standard (OWASP, SOLID, DRY, KISS, etc.)",
            "Use type hints on all function signatures",
        ],
        "must_not_do": [
            "Use magic numbers or hardcoded configuration values",
            "Bypass error handling for assumed-valid inputs",
            "Write functions longer than 50 lines without decomposition",
        ],
    },
    "trading": {
        "must_do": [
            "Use Python with typed signatures and docstrings",
            "Implement emergency stops as an independent layer",
            "Follow APEX platform file path conventions (risk_engine/, data_pipeline/, execution/)",
        ],
        "must_not_do": [
            "Disable or bypass emergency stops under any circumstance",
            "Place stops at round numbers (attracts stop hunting)",
            "Use the same risk parameters across all market regimes without adjustment",
        ],
    },
    "programming": {
        "must_do": [
            "Include time and space complexity analysis for all algorithms",
            "Show at least one working example with input/output",
            "Include diagrams for non-trivial algorithm flows",
        ],
        "must_not_do": [
            "Present an algorithm without its complexity bounds",
            "Use recursive solutions without discussing tail-call or memoization alternatives",
            "Omit edge case handling in examples",
        ],
    },
    "writing": {
        "must_do": [
            "Include before/after text comparisons showing improvements",
            "Provide specific style rules with reasoning for each",
            "Maintain consistent tone guidelines throughout",
        ],
        "must_not_do": [
            "Use passive voice where active voice is clearer",
            "Write sentences longer than 30 words without breaking them up",
            "Use jargon without defining it for the target audience",
        ],
    },
}

# Markdown sections to insert for cncf skills
CNCF_WHEN_TO_USE = """---

## When to Use

Use this skill when:

- **Integrating a CNCF project into Kubernetes infrastructure** — You need to configure, deploy, or troubleshoot a cloud-native tool within a cluster
- **Designing cloud-native architecture** — You are selecting and integrating CNCF tools to solve specific infrastructure challenges
- **Resolving operational issues** — A CNCF component is misbehaving, underperforming, or needs configuration changes
"""

CNCF_CORE_WORKFLOW = """---

## Core Workflow

1. **Assess Requirements** — Understand the use case, scale, integration needs, and existing infrastructure. **Checkpoint:** Document requirements, constraints, and success criteria.

2. **Design Architecture** — Plan component interactions, data flow, and deployment strategy using cloud-native best practices. **Checkpoint:** Verify the architecture addresses all requirements and follows CNCF conventions.

3. **Implement & Configure** — Create manifests, configurations, and deployment scripts. Include resource limits, health checks, and observability hooks. **Checkpoint:** Validate all YAML against schema and test in a staging environment.

4. **Deploy & Monitor** — Apply manifests to the cluster, verify component health, and confirm observability is working. **Checkpoint:** Confirm all pods/services are running, probes passing, and metrics/alerts configured.
"""

# Generic sections for trading skills
TRADING_WHEN_TO_USE = """---

## When to Use

Use this skill when:

- **Implementing position risk controls** — You need to add stop losses, position sizing, or drawdown limits to a trading algorithm
- **Designing or reviewing trading system components** — You are building or auditing order execution, market data processing, or exchange connectivity
- **Building market analysis or signal generation logic** — You need to create indicators, signals, or prediction models for trading decisions
"""

TRADING_CORE_WORKFLOW = """---

## Core Workflow

1. **Analyze Requirements** — Understand the trading scenario, market conditions, data sources, and risk constraints. **Checkpoint:** Clearly document inputs, outputs, edge cases, and failure modes.

2. **Design Implementation** — Choose appropriate algorithms, data structures, and risk constraints following APEX platform conventions. **Checkpoint:** Verify the design includes proper error handling and risk enforcement at every step.

3. **Implement & Test** — Write Python code with typed signatures, docstrings, and comprehensive tests including edge cases. **Checkpoint:** All risk constraints are enforced, tested, and documented. Emergency layers are independent.

4. **Validate & Review** — Run all tests, verify risk controls under simulated conditions, and review against best practices. **Checkpoint:** All edge cases handled, emergency stops functional, and code follows APEX platform patterns.
"""

# Generic sections for programming skills
PROGRAMMING_WHEN_TO_USE = """---

## When to Use

Use this skill when:

- **Implementing or analyzing algorithms** — You need to understand, implement, or optimize algorithms for a specific problem domain
- **Comparing algorithmic approaches** — You are evaluating different algorithms for correctness, performance, or trade-offs
- **Studying computational patterns** — You need reference implementations and complexity analysis for standard algorithmic patterns
"""

PROGRAMMING_CORE_WORKFLOW = """---

## Core Workflow

1. **Understand the Problem** — Identify inputs, outputs, constraints, and edge cases. **Checkpoint:** Clearly define the problem statement and expected behavior.

2. **Select Algorithm** — Choose the most appropriate algorithm based on constraints (time/space complexity, data size, ordering requirements). **Checkpoint:** Justify the algorithm choice with complexity analysis.

3. **Implement & Test** — Write clean, readable code with type hints, docstrings, and edge case handling. **Checkpoint:** Verify correctness with multiple test cases including edge cases.

4. **Analyze & Optimize** — Review time/space complexity, identify optimization opportunities, and validate against benchmarks. **Checkpoint:** Confirm complexity bounds match analysis and all test cases pass.
"""

# ─── Data Classes ────────────────────────────────────────────────────────────────


@dataclass
class SkillFixReport:
    filepath: str
    domain: str
    added_content_types: bool = False
    added_maturity: bool = False
    added_constraints: bool = False
    added_when_to_use: bool = False
    added_core_workflow: bool = False
    changes_summary: list[str] = field(default_factory=list)

    def summary(self) -> str:
        parts = [os.path.relpath(self.filepath)]
        if self.changes_summary:
            parts.append(" + ".join(self.changes_summary))
        return " | ".join(parts)


# ─── Helpers ─────────────────────────────────────────────────────────────────────


def extract_domain(filepath: str) -> Optional[str]:
    """Extract domain from path like skills/<domain>/<topic>/SKILL.md"""
    parts = Path(filepath).parts
    for i, p in enumerate(parts):
        if p in DOMAIN_CONTENT_TYPES:
            return p
    return None


def parse_frontmatter(content: str):
    """
    Parse frontmatter from SKILL.md content.
    Returns (frontmatter_dict, rest_of_content, raw_fm_text).
    Returns (None, content, "") if no frontmatter found.
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None, content, ""

    fm_text = match.group(1)
    rest = content[match.end():]

    try:
        fm = yaml.safe_load(fm_text)
        if fm is None:
            fm = {}
    except yaml.YAMLError:
        # If YAML parsing fails, try to extract at least the basics
        fm = {}

    return fm, rest, fm_text


def format_frontmatter(fm: dict) -> str:
    """
    Format frontmatter dict back to YAML.
    Uses yaml.dump but with tuned settings to keep it clean.
    """
    # Sort keys for consistency
    sorted_fm = dict(sorted(fm.items()))
    return yaml.dump(sorted_fm, default_flow_style=False, allow_unicode=True, width=120)


def insert_frontmatter_field(fm: dict, key: str, value) -> dict:
    """Add a field to frontmatter dict."""
    fm[key] = value
    return fm


def has_section(rest: str, section_name: str) -> bool:
    """Check if a markdown section exists in content."""
    return bool(re.search(rf"^##\s+{re.escape(section_name)}\s*$", rest, re.MULTILINE))


def insert_sections_after_title(content: str, sections: str) -> str:
    """
    Insert markdown sections at the end of the file content.

    The template strings start with \n---\n\n## so they're self-contained blocks.
    Appending at the end ensures correct ordering when multiple sections are added
    in sequence (first call = first section in file).
    """
    # Ensure there's a trailing newline before appending
    if content and not content.endswith('\n'):
        content += '\n'
    return content + sections


# ─── Fix Functions ──────────────────────────────────────────────────────────────


def fix_content_types(fm: dict, domain: str) -> tuple[dict, bool]:
    """Add content-types to frontmatter if missing."""
    if domain not in DOMAIN_CONTENT_TYPES:
        return fm, False

    if "content-types" in fm:
        return fm, False

    types = DOMAIN_CONTENT_TYPES[domain]
    fm = insert_frontmatter_field(fm, "content-types", types)
    return fm, True


def fix_maturity(fm: dict) -> tuple[dict, bool]:
    """Add maturity and completeness to frontmatter if missing."""
    changed = False
    if "maturity" not in fm:
        fm = insert_frontmatter_field(fm, "maturity", "stable")
        changed = True
    if "completeness" not in fm:
        fm = insert_frontmatter_field(fm, "completeness", 95)
        changed = True
    return fm, changed


def build_constraints_md(domain: str) -> str:
    """Build Constraints section markdown from domain defaults."""
    constraints = DOMAIN_CONSTRAINTS.get(domain, {
        "must_do": ["Follow domain best practices"],
        "must_not_do": ["Do not bypass safety controls"],
    })

    md = "\n" + "---\n\n"
    md += "## Constraints\n\n"
    md += "### MUST DO\n"
    for c in constraints["must_do"]:
        md += f"- {c}\n"
    md += "\n### MUST NOT DO\n"
    for c in constraints["must_not_do"]:
        md += f"- {c}\n"
    return md


def add_constraints_section(content: str, domain: str) -> tuple[str, bool]:
    """Add a Constraints section if missing."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return content, False
    rest = content[match.end():]

    if has_section(rest, "Constraints"):
        return content, False

    md = build_constraints_md(domain)
    return insert_sections_after_title(content, md), True


def fix_all_skills(skills_dir: str, dry_run: bool = False) -> tuple[list[SkillFixReport], int]:
    """
    Scan all SKILL.md files and fix missing fields/sections.
    Returns (reports, modified_count).
    """
    reports: list[SkillFixReport] = []
    modified_count = 0

    for root, dirs, files in os.walk(skills_dir):
        if "SKILL.md" not in files:
            continue

        filepath = os.path.join(root, "SKILL.md")
        domain = extract_domain(filepath)

        if domain is None:
            # Skip domains we don't know about (go, linux, etc.)
            # They already have all fields
            continue

        with open(filepath, "r") as f:
            original_content = f.read()

        content = original_content
        fm, rest, raw_fm = parse_frontmatter(content)
        if fm is None:
            fm = {}

        report = SkillFixReport(filepath=filepath, domain=domain)

        # Step 1: Add content-types if missing
        if domain in DOMAIN_CONTENT_TYPES:
            fm, changed = fix_content_types(fm, domain)
            if changed:
                report.added_content_types = True
                report.changes_summary.append("Added content-types")

        # Step 2: Add maturity + completeness if missing
        fm, changed = fix_maturity(fm)
        if changed:
            report.added_maturity = True
            report.changes_summary.append("Added maturity+completeness")

        # Step 3: Rewrite frontmatter if we added/changed anything
        new_fm_changed = report.added_content_types or report.added_maturity
        if new_fm_changed:
            new_fm_text = format_frontmatter(fm)
            # Replace frontmatter block in content
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if match:
                content = content[:match.start()] + "---\n" + new_fm_text + "---\n" + content[match.end():]

        # Step 4: Domain-specific content fixes
        if domain == "trading":
            # Trading: add When to Use, Core Workflow, Constraints
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if match:
                rest = content[match.end():]

            # Add When to Use if missing
            if not has_section(rest, "When to Use"):
                content = insert_sections_after_title(content, TRADING_WHEN_TO_USE)
                report.added_when_to_use = True
                report.changes_summary.append("Added When to Use")
                # Refresh rest for next check
                match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
                if match:
                    rest = content[match.end():]

            # Add Core Workflow if missing
            if not has_section(rest, "Core Workflow"):
                content = insert_sections_after_title(content, TRADING_CORE_WORKFLOW)
                report.added_core_workflow = True
                report.changes_summary.append("Added Core Workflow")
                match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
                if match:
                    rest = content[match.end():]

            # Add Constraints if missing
            if not has_section(rest, "Constraints"):
                md = build_constraints_md(domain)
                content = insert_sections_after_title(content, md)
                report.added_constraints = True
                report.changes_summary.append("Added Constraints")

        elif domain == "cncf":
            # CNCF: add When to Use + Core Workflow if missing, plus Constraints
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if match:
                rest = content[match.end():]

            if not has_section(rest, "When to Use"):
                content = insert_sections_after_title(content, CNCF_WHEN_TO_USE)
                report.added_when_to_use = True
                report.changes_summary.append("Added When to Use")
                match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
                if match:
                    rest = content[match.end():]

            if not has_section(rest, "Core Workflow"):
                content = insert_sections_after_title(content, CNCF_CORE_WORKFLOW)
                report.added_core_workflow = True
                report.changes_summary.append("Added Core Workflow")
                match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
                if match:
                    rest = content[match.end():]

            if not has_section(rest, "Constraints"):
                md = build_constraints_md(domain)
                content = insert_sections_after_title(content, md)
                report.added_constraints = True
                report.changes_summary.append("Added Constraints")

        elif domain == "coding":
            # Coding: add Constraints if missing
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if match:
                rest = content[match.end():]
            else:
                rest = ""

            if not has_section(rest, "Constraints"):
                md = build_constraints_md(domain)
                content = insert_sections_after_title(content, md)
                report.added_constraints = True
                report.changes_summary.append("Added Constraints")

        elif domain == "agent":
            # Agent: add Constraints if missing (they already have When to Use + Core Workflow)
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if match:
                rest = content[match.end():]
            else:
                rest = ""

            if not has_section(rest, "Constraints"):
                md = build_constraints_md(domain)
                content = insert_sections_after_title(content, md)
                report.added_constraints = True
                report.changes_summary.append("Added Constraints")

        elif domain == "programming":
            # Programming: add When to Use, Core Workflow, Constraints
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if match:
                rest = content[match.end():]
            else:
                rest = ""

            if not has_section(rest, "When to Use"):
                content = insert_sections_after_title(content, PROGRAMMING_WHEN_TO_USE)
                report.added_when_to_use = True
                report.changes_summary.append("Added When to Use")
                match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
                if match:
                    rest = content[match.end():]

            if not has_section(rest, "Core Workflow"):
                content = insert_sections_after_title(content, PROGRAMMING_CORE_WORKFLOW)
                report.added_core_workflow = True
                report.changes_summary.append("Added Core Workflow")
                match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
                if match:
                    rest = content[match.end():]

            if not has_section(rest, "Constraints"):
                md = build_constraints_md(domain)
                content = insert_sections_after_title(content, md)
                report.added_constraints = True
                report.changes_summary.append("Added Constraints")

        elif domain == "writing":
            # Writing: add Constraints if missing
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if match:
                rest = content[match.end():]
            else:
                rest = ""

            if not has_section(rest, "Constraints"):
                md = build_constraints_md(domain)
                content = insert_sections_after_title(content, md)
                report.added_constraints = True
                report.changes_summary.append("Added Constraints")

        # Write the file if changed
        if content != original_content:
            if not dry_run:
                with open(filepath, "w") as f:
                    f.write(content)
            modified_count += 1

        reports.append(report)

    return reports, modified_count


# ─── Main ────────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Fix quality issues in SKILL.md files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without modifying files")
    parser.add_argument("--skills-dir", default="skills", help="Path to skills directory")
    args = parser.parse_args()

    skills_dir = args.skills_dir
    if not os.path.isdir(skills_dir):
        print(f"ERROR: Skills directory '{skills_dir}' not found")
        sys.exit(1)

    print(f"Scanning {skills_dir}/ for SKILL.md files...")
    if args.dry_run:
        print("DRY RUN — no files will be modified\n")

    reports, modified_count = fix_all_skills(skills_dir, dry_run=args.dry_run)

    # Aggregate stats
    total = len(reports)
    ct_fixed = sum(1 for r in reports if r.added_content_types)
    maturity_fixed = sum(1 for r in reports if r.added_maturity)
    constraints_fixed = sum(1 for r in reports if r.added_constraints)
    wtu_fixed = sum(1 for r in reports if r.added_when_to_use)
    cw_fixed = sum(1 for r in reports if r.added_core_workflow)
    modified = sum(1 for r in reports if r.changes_summary)

    print(f"\n{'='*60}")
    print(f"Audit & Fix Results")
    print(f"{'='*60}")
    print(f"Total SKILL.md files scanned: {total}")
    print(f"Files modified: {modified}")
    print(f"  + content-types added:    {ct_fixed}")
    print(f"  + maturity+completeness:  {maturity_fixed}")
    print(f"  + Constraints section:    {constraints_fixed}")
    print(f"  + When to Use section:    {wtu_fixed}")
    print(f"  + Core Workflow section:  {cw_fixed}")

    print(f"\nPer-domain breakdown:")
    domain_stats = {}
    for r in reports:
        d = r.domain
        if d not in domain_stats:
            domain_stats[d] = {"total": 0, "modified": 0, "changes": set()}
        domain_stats[d]["total"] += 1
        if r.changes_summary:
            domain_stats[d]["modified"] += 1
            domain_stats[d]["changes"].update(r.changes_summary)

    for d in sorted(domain_stats.keys()):
        s = domain_stats[d]
        print(f"  {d:12s}: {s['total']:3d} files, {s['modified']:3d} modified | {', '.join(sorted(s['changes']))}")

    print(f"\nDetailed changes:")
    for r in sorted(reports, key=lambda x: x.filepath):
        if r.changes_summary:
            print(f"  {r.summary()}")

    if args.dry_run:
        print(f"\n🔍 DRY RUN — run without --dry-run to apply changes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
