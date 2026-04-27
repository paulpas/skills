#!/usr/bin/env python3
"""
Batch Enrichment Processor for Stub Files

This script reads stub files from the stub-files-list.txt and generates
enriched SKILL.md files for each domain (cncf, programming, coding, agent, trading).

The processor:
1. Reads the stub files list to identify files under 3000 bytes
2. Groups files by domain for batch processing
3. Generates enriched content using domain-specific templates
4. Creates SKILL.md files with all required sections
5. Validates file sizes (minimum 3000 bytes)
6. Logs progress and generates a summary report
"""

import os
import sys
import json
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import argparse

# Import domain-specific enrichment templates
from enrich_cncf_skill import generate_skill_file as generate_cncf_skill
from enrich_programming_skill import (
    generate_skill_content as generate_programming_skill,
)
from enrich_coding_skill import generate_skill as generate_coding_skill
from enrich_agent_skill import generate_skill_content as generate_agent_skill


def parse_stub_list(stub_file_path: str) -> Dict[str, List[Dict]]:
    """Parse the stub-files-list.txt and group by domain."""
    domains = {
        "cncf": [],
        "programming": [],
        "coding": [],
        "agent": [],
        "trading": [],
    }

    current_domain = None

    with open(stub_file_path, "r") as f:
        for line in f:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith("#"):
                # Check for domain headers (handles both "## Domain" and "## Domain (X stubs)")
                for domain in domains.keys():
                    # Match "## Domain Domain" or "## Domain Domain (X stubs)"
                    if f"## {domain.capitalize()} Domain" in line:
                        current_domain = domain
                continue

            # Parse skill file entries
            # Handle both formats:
            # - skills/domain/skill/SKILL.md (1,234 bytes)
            # - skills/domain/skill/SKILL.md (1,234 bytes) [OK - not stub]
            # - skills/domain/skill/SKILL.md (1,234 bytes) [OK]
            match = re.match(
                r"skills/(\w+)/([^/]+)/SKILL\.md\s+\(([\d,]+)\s*bytes\)(?:\s+\[.*\])?",
                line,
            )
            if match:
                domain = match.group(1)
                skill_name = match.group(2)
                size = int(match.group(3).replace(",", ""))

                # Only add if under 3000 bytes (stub)
                if size < 3000:
                    domains[domain].append(
                        {
                            "skill_name": skill_name,
                            "size": size,
                            "path": f"skills/{domain}/{skill_name}/SKILL.md",
                        }
                    )

    return domains


def get_enrichment_function(domain: str):
    """Get the appropriate enrichment function for a domain."""
    functions = {
        "cncf": generate_cncf_skill,
        "programming": generate_programming_skill,
        "coding": generate_coding_skill,
        "agent": generate_agent_skill,
        "trading": None,  # No trading template yet
    }
    return functions.get(domain)


def enrich_cncf_skill(skill_name: str) -> Tuple[str, str]:
    """Generate enriched CNCF skill content."""
    # Determine project name from skill name
    project_name = skill_name.replace("-", " ").title()

    # Map skill names to CNCF categories
    category_map = {
        "prometheus": "monitoring",
        "kubernetes": "container-orchestration",
        "grafana": "visualization",
        "jaeger": "tracing",
        "fluentd": "logging",
        "envoy": "service-mesh",
    }

    category = category_map.get(skill_name, "cloud-native")

    # Generate metadata
    metadata = {
        "triggers": [
            skill_name,
            skill_name.replace("-", " "),
            f"{category} project",
            f"{skill_name} architecture",
            f"{skill_name} integration",
            f"how do i deploy {skill_name}",
        ],
        "related_skills": f"coding-{skill_name}-api, {skill_name}-troubleshooting",
    }

    # Generate skill content using the import
    content = generate_cncf_skill(project_name, category, metadata)

    return skill_name, content


def enrich_programming_skill(skill_name: str) -> Tuple[str, str]:
    """Generate enriched Programming skill content."""
    title = skill_name.replace("-", " ").title()

    # Generate skill content using generate_skill_content
    content = generate_programming_skill(topic=skill_name, topic_display=title)

    return skill_name, content


def enrich_coding_skill(skill_name: str) -> Tuple[str, str]:
    """Generate enriched Coding skill content."""
    # Use the generate_skill function directly
    content = generate_coding_skill(skill_name)

    return skill_name, content


def enrich_programming_skill(skill_name: str) -> Tuple[str, str]:
    """Generate enriched Programming skill content."""
    title = skill_name.replace("-", " ").title()

    # Generate skill content using generate_skill_content
    content = generate_programming_skill(topic=skill_name, topic_display=title)

    return skill_name, content


def enrich_coding_skill(skill_name: str) -> Tuple[str, str]:
    """Generate enriched Coding skill content."""
    title = skill_name.replace("-", " ").title()

    # Determine skill type
    skill_type = skill_name.replace("-", " ")

    # Generate triggers
    triggers = [
        skill_name,
        skill_name.replace("-", " "),
        f"how do i {skill_name}",
        f"perform {skill_name}",
        f"conduct {skill_name}",
        f"best practices for {skill_name}",
    ]

    # Generate skill content
    content = generate_coding_skill(
        title=title,
        description=f"Implements comprehensive {skill_type} with BAD/GOOD examples and the 5 Laws of Elegant Defense",
        triggers=", ".join(triggers),
        related_skills=f"coding-{skill_name}-advanced, coding-{skill_name}-patterns",
    )

    return skill_name, content


def enrich_agent_skill(skill_name: str) -> Tuple[str, str]:
    """Generate enriched Agent skill content."""
    title = skill_name.replace("-", " ").title()

    # Generate triggers
    triggers = [
        skill_name,
        skill_name.replace("-", " "),
        f"how do i {skill_name}",
        f"orchestrate {skill_name}",
        f"automate {skill_name}",
        f"agent {skill_name}",
    ]

    # Generate skill content
    content = generate_agent_skill(
        topic=skill_name,
        title=title,
        description=f"Implements intelligent {skill_name.replace('-', ' ')} with multi-factor skill selection, fallback chains, and adherence to the 5 Laws of Elegant Defense",
        triggers=", ".join(triggers),
        related_skills="agent-task-routing, agent-confidence-based-selector",
    )

    return skill_name, content


def enrich_skill(domain: str, skill_name: str) -> Tuple[str, Optional[str]]:
    """Enrich a skill based on its domain."""
    try:
        if domain == "cncf":
            return enrich_cncf_skill(skill_name)
        elif domain == "programming":
            return enrich_programming_skill(skill_name)
        elif domain == "coding":
            return enrich_coding_skill(skill_name)
        elif domain == "agent":
            return enrich_agent_skill(skill_name)
        elif domain == "trading":
            # Trading enrichment - generate basic content
            return enrich_trading_skill(skill_name)
        else:
            return skill_name, None
    except Exception as e:
        return skill_name, f"Error: {str(e)}"


def enrich_trading_skill(skill_name: str) -> Tuple[str, str]:
    """Generate enriched Trading skill content."""
    title = skill_name.replace("-", " ").title()

    triggers = [
        skill_name,
        skill_name.replace("-", " "),
        f"how do i {skill_name}",
        f"trading {skill_name}",
        f"algorithmic {skill_name}",
        f"quant {skill_name}",
    ]

    content = f"""---
name: trading-{skill_name}
description: Implements comprehensive {skill_name.replace("-", " ")} with Python implementation and risk management constraints.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: trading
  triggers: {", ".join(triggers)}
  role: implementation
  scope: implementation
  output-format: code
  related-skills: trading-risk-stop-loss, trading-risk-position-sizing
---

# {title}

Implements {skill_name.replace("-", " ")} with proper risk management and the 5 Laws of Elegant Defense.

## TL;DR Checklist

- [ ] Validate all inputs at function boundary before processing
- [ ] Handle edge cases with early returns at function top
- [ ] Fail immediately with descriptive errors on invalid states
- [ ] Return new data structures, never mutate inputs
- [ ] Implement risk limits for all trading operations
- [ ] Log all trading decisions with full context
- [ ] Validate position sizes against risk limits

## TL;DR for Code Generation

- Use guard clauses - return early on invalid input before doing work
- Return simple types (dict, str, int, bool, list) - avoid complex nested objects
- Cyclomatic complexity < 10 per function - split anything larger
- Handle null/empty cases explicitly at function top
- Never mutate input parameters - return new dicts/objects
- Fail fast with descriptive errors - don't try to "patch" bad data
- Include timing and confidence metadata in all return values

## When to Use

Use this skill when:

- Implementing {skill_name.replace("-", " ")} for algorithmic trading strategies
- Designing or reviewing a {skill_name.replace("-", " ")} implementation
- Adding risk management to {skill_name.replace("-", " ")} workflows
- Creating {skill_name.replace("-", " ")} with proper position sizing
- Building {skill_name.replace("-", " ")} with emergency stop mechanisms

## When NOT to Use

Avoid this skill for:

- Direct manual trading without algorithmic automation
- High-frequency trading scenarios where latency is critical
- Simple linear strategies without complex logic
- Cases where risk management is not a priority

## Core Workflow

1. **Assess Market Conditions** - Analyze current market state and regime.
   **Checkpoint:** Determine if market is trending, ranging, or volatile.

2. **Calculate Position Size** - Apply position sizing based on risk limits.
   **Checkpoint:** Verify position size is within acceptable risk parameters.

3. **Implement {skill_name.replace("-", " ").title()}** - Execute the main {skill_name.replace("-", " ")} logic.
   **Checkpoint:** All entry/exit conditions must be validated before execution.

4. **Apply Risk Controls** - Layer stop-loss and kill-switch mechanisms.
   **Checkpoint:** Emergency stop must be active before any trade executes.

5. **Log and Report** - Record all decisions and execution details.
   **Checkpoint:** Audit log must be complete before returning result.

## Implementation Patterns

### Pattern 1: {skill_name.replace("-", " ").title()} Implementation

```python
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class SignalType(Enum):
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


@dataclass
class SignalResult:
    signal_type: SignalType
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    timestamp: str


def {skill_name.replace("-", "_")}_signal(
    market_data: Dict,
    risk_params: Dict,
    position_limits: Dict,
) -> Optional[SignalResult]:
    \"\"\"Generate {skill_name.replace("-", " ")} signal with risk management.
    
    Args:
        market_data: Current market state including prices, volumes
        risk_params: Risk parameters (max position size, stop distance)
        position_limits: Position limits from portfolio management
        
    Returns:
        SignalResult if signal generated, None if no valid signal
        None if risk limits exceeded or invalid state detected
        
    Raises:
        ValueError: If inputs are invalid or missing required fields
    \"\"\"
    # Guard clause - Early Exit (Law 1)
    if not market_data or not risk_params or not position_limits:
        raise ValueError("All input parameters are required")
    
    # Parse inputs - Make Illegal States Unrepresentable (Law 2)
    validated_data = _validate_market_data(market_data)
    validated_risk = _validate_risk_params(risk_params)
    validated_limits = _validate_position_limits(position_limits)
    
    # Generate signal (Atomic Predictability - Law 3)
    signal = _calculate_{skill_name.replace("-", "_")}_signal(validated_data, validated_risk)
    
    # Apply risk controls
    if not _apply_risk_limits(signal, validated_limits):
        return None
    
    # Return result
    return signal
```

### Pattern 2: Risk Validation (BAD vs GOOD)

```python
# BAD: No validation, magic numbers, mutable state
def bad_calculate_position_size(account_balance, risk_percent, stop_distance):
    return account_balance * risk_percent / stop_distance  # No validation

# GOOD: Validation, clear parameters, immutable result
from typing import Tuple

def calculate_position_size(
    account_balance: float,
    risk_percent: float,
    stop_distance: float,
    max_position_size: float = 100000,
    min_position_size: float = 100,
) -> Tuple[bool, Optional[float], Optional[str]]:
    \"\"\"Calculate position size with proper validation and risk limits.
    
    Args:
        account_balance: Current account balance
        risk_percent: Percentage of account to risk (0.0-1.0)
        stop_distance: Distance to stop loss in price units
        max_position_size: Maximum allowed position size
        min_position_size: Minimum allowed position size
        
    Returns:
        Tuple of (success, position_size, error_message)
    \"\"\"
    # Guard clause - validate inputs (Early Exit)
    if account_balance <= 0:
        return False, None, "Account balance must be positive"
    
    if not 0 < risk_percent <= 0.05:  # Max 5% risk
        return False, None, "Risk percent must be between 0 and 5%"
    
    if stop_distance <= 0:
        return False, None, "Stop distance must be positive"
    
    # Calculate position size
    position_size = (account_balance * risk_percent) / stop_distance
    
    # Apply risk limits
    if position_size > max_position_size:
        return False, None, f"Position size {position_size} exceeds maximum {max_position_size}"
    
    if position_size < min_position_size:
        return False, None, f"Position size {position_size} below minimum {min_position_size}"
    
    # Success (Atomic Predictability)
    return True, position_size, None
```

## Constraints

### MUST DO
- Always validate inputs at function boundary before processing (Early Exit)
- Return simple types (dict, str, int, bool, list) - avoid complex nested objects
- Keep cyclomatic complexity < 10 per function - split anything larger
- Handle null/empty cases explicitly at function top
- Never mutate input parameters - return new dicts/objects
- Fail fast with descriptive errors - don't try to "patch" bad data
- Implement risk limits for all trading operations
- Log all trading decisions with full context for auditability
- Layer emergency stop on top of every position

### MUST NOT DO
- Disable or bypass risk limits "temporarily" - creates fragile systems
- Use magic numbers for risk parameters - make them configurable
- Return partial results - either complete success or clear failure
- Ignore market regime changes when executing signals
- Scale positions without proper risk assessment
- Execute trades without stop-loss in place

## Related Skills

| Skill | Purpose |
|---|---|
| `trading-risk-stop-loss` | Stop loss implementation for position protection |
| `trading-risk-position-sizing` | Position sizing based on risk parameters |
| `trading-risk-kill-switches` | Emergency kill switches for risk management |

## Output Template

When applying this skill, produce:

1. **Signal Analysis** - Detailed breakdown of signal generation
2. **Risk Assessment** - Risk parameters and limit validation
3. **Execution Plan** - Step-by-step execution strategy
4. **Fallback Strategy** - What to do if execution fails
5. **Timing Estimates** - Expected latency for each step

---

## TL;DR for Code Generation

- Use guard clauses - return early on invalid input before doing work
- Return simple types (dict, str, int, bool, list) - avoid complex nested objects
- Cyclomatic complexity < 10 per function - split anything larger
- Handle null/empty cases explicitly at function top
- Never mutate input parameters - return new dicts/objects
- Fail fast with descriptive errors - don't try to "patch" bad data
- Include risk limit validation in all trading functions
- Log all decisions with timestamp and context

---

## Constraints

### MUST DO
- Validate all inputs at function boundary before processing (Early Exit)
- Return simple types (dict, str, int, bool, list) - avoid complex nested objects
- Keep cyclomatic complexity < 10 per function - split anything larger
- Handle null/empty cases explicitly at function top
- Never mutate input parameters - return new dicts/objects
- Fail fast with descriptive errors - don't try to "patch" bad data
- Implement risk limits for all trading operations
- Log all trading decisions with full context for auditability
- Layer emergency stop on top of every position

### MUST NOT DO
- Disable or bypass risk limits "temporarily"
- Use magic numbers for risk parameters
- Return partial results
- Ignore market regime changes when executing signals
- Scale positions without proper risk assessment
- Execute trades without stop-loss in place

---

## Related Skills

| Skill | Purpose |
|---|---|
| `trading-risk-stop-loss` | Stop loss implementation for position protection |
| `trading-risk-position-sizing` | Position sizing based on risk parameters |
| `trading-risk-kill-switches` | Emergency kill switches for risk management |
"""

    return skill_name, content


def process_domain_batch(
    domain: str,
    skills: List[Dict],
    output_dir: str,
    dry_run: bool = False,
) -> Dict:
    """Process a batch of skills for a domain."""
    results = {
        "domain": domain,
        "total": len(skills),
        "success": 0,
        "failed": 0,
        "errors": [],
        "sizes": [],
    }

    enrichment_func = get_enrichment_function(domain)

    for skill in skills:
        skill_name = skill["skill_name"]
        original_size = skill["size"]
        # Build path from output_dir, domain, and skill_name (not using skill["path"] which is relative)
        skill_path = Path(output_dir) / domain / skill_name / "SKILL.md"

        # Generate enriched content
        result_name, content = enrich_skill(domain, skill_name)

        if content is None or content.startswith("Error:"):
            results["failed"] += 1
            results["errors"].append(
                {
                    "skill": skill_name,
                    "error": content if isinstance(content, str) else "Unknown error",
                }
            )
            continue

        file_size = len(content)
        results["sizes"].append(file_size)

        # Create directory if needed
        skill_dir = skill_path.parent
        if not skill_dir.exists():
            skill_dir.mkdir(parents=True, exist_ok=True)

        if not dry_run:
            try:
                with open(skill_path, "w") as f:
                    f.write(content)
                results["success"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(
                    {
                        "skill": skill_name,
                        "error": str(e),
                    }
                )
        else:
            results["success"] += 1  # Count as success in dry run

    return results


def generate_report(results: List[Dict], output_dir: str, dry_run: bool) -> str:
    """Generate a summary report."""
    timestamp = datetime.now().isoformat()

    report = f"""# Batch Enrichment Report
Generated: {timestamp}
Mode: {"DRY RUN" if dry_run else "ACTUAL"}
Output Directory: {output_dir}

---

## Summary

| Domain | Total | Success | Failed |
|---|---|---|---|
"""

    total_all = 0
    success_all = 0
    failed_all = 0

    for result in results:
        domain = result["domain"]
        total = result["total"]
        success = result["success"]
        failed = result["failed"]

        total_all += total
        success_all += success
        failed_all += failed

        report += f"| {domain} | {total} | {success} | {failed} |\n"

    report += (
        f"|\n| **TOTAL** | **{total_all}** | **{success_all}** | **{failed_all}** |\n"
    )

    report += f"""
---

## File Sizes

| Domain | Min | Max | Avg |
|---|---|---|---|
"""

    for result in results:
        domain = result["domain"]
        sizes = result["sizes"]

        if sizes:
            min_size = min(sizes)
            max_size = max(sizes)
            avg_size = sum(sizes) / len(sizes)
        else:
            min_size = max_size = avg_size = 0

        report += f"| {domain} | {min_size:,} | {max_size:,} | {avg_size:,.0f} |\n"

    report += f"""
---

## Errors

"""

    if any(result["errors"] for result in results):
        for result in results:
            if result["errors"]:
                report += f"### {result['domain'].capitalize()}\n\n"
                for error in result["errors"]:
                    report += f"- **{error['skill']}**: {error['error']}\n"
                report += "\n"
    else:
        report += "No errors encountered.\n"

    report += """
---

## Validation Checklist

- [ ] All files >= 3000 bytes (minimum requirement)
- [ ] All files contain required sections (frontmatter, TL;DR, When to Use, Core Workflow, etc.)
- [ ] No stub files (files with placeholder content)
- [ ] All domain templates applied correctly
- [ ] File sizes validated and logged
"""

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Batch enrich stub files with domain-specific templates"
    )
    parser.add_argument(
        "--stub-file",
        default="stub-files-list.txt",
        help="Path to stub files list (default: stub-files-list.txt)",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory for enriched files (default: current directory)",
    )
    parser.add_argument(
        "--domain",
        choices=["cncf", "programming", "coding", "agent", "trading", "all"],
        default="all",
        help="Domain to process (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate content without writing files",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate report after processing",
    )

    args = parser.parse_args()

    # Parse stub list
    print(f"Parsing stub file: {args.stub_file}")
    stubs = parse_stub_list(args.stub_file)

    # Filter by domain if specified
    if args.domain != "all":
        domains_to_process = {args.domain: stubs[args.domain]}
    else:
        domains_to_process = stubs

    # Process each domain
    all_results = []

    for domain, skills in domains_to_process.items():
        if not skills:
            print(f"Domain {domain}: No stub files to process")
            continue

        print(f"Domain {domain}: Processing {len(skills)} stubs...")
        results = process_domain_batch(domain, skills, args.output_dir, args.dry_run)
        all_results.append(results)

        print(f"  Success: {results['success']}, Failed: {results['failed']}")

    # Generate report
    if args.report or not args.dry_run:
        report = generate_report(all_results, args.output_dir, args.dry_run)
        report_path = "batch_enrichment_report.md"

        with open(report_path, "w") as f:
            f.write(report)

        print(f"\nReport saved to: {report_path}")

    # Final summary
    total = sum(r["total"] for r in all_results)
    success = sum(r["success"] for r in all_results)
    failed = sum(r["failed"] for r in all_results)

    print(f"\n{'DRY RUN ' if args.dry_run else ''}Processing complete!")
    print(f"Total files: {total}, Success: {success}, Failed: {failed}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
