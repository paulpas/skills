# LLM Prompt Template for Skill Generation

This document provides the prompt template used by `generate_skill.py` to generate SKILL.md files using an LLM.

## Main Generation Prompt

```
You are creating a SKILL.md file for the agent-skill-router repository.

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
- metadata.scope: {default_scope}
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
{domain_requirements}

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

Generate the complete SKILL.md file content. Start with --- for YAML frontmatter.
```

## Domain Requirements Template

```python
{
    "agent": "- Include ASCII flow diagram for orchestration logic\n- Reference code-philosophy (5 Laws of Elegant Defense)\n- Fallback/error routing for every branching point",
    "cncf": "- Complete working YAML manifest example\n- Architecture diagram or table\n- Common Pitfalls section",
    "coding": "- At least one BAD vs GOOD code example pair\n- MUST DO/MUST NOT DO constraints\n- Reference to standard (OWASP, SOLID, etc.)",
    "trading": "- Python functions with typed signatures and docstrings\n- Risk constraints section\n- File path conventions (risk_engine/, data_pipeline/, execution/, tests/)",
    "programming": "- Implementation in specific language\n- Complexity table\n- Algorithm steps",
}
```

## Task Parsing Prompt

```
Extract the domain and topic from this task description.

Task: "{task}"

Return a JSON object with:
- domain: one of (agent, cncf, coding, programming, trading)
- topic: kebab-case topic name (e.g., "code-review", "risk-stop-loss")

Examples:
- Task: "Create a code review skill" → {"domain": "coding", "topic": "code-review"}
- Task: "Build a stop loss mechanism" → {"domain": "trading", "topic": "risk-stop-loss"}
- Task: "Create a Kubernetes deployment skill" → {"domain": "cncf", "topic": "kubernetes"}

Respond with ONLY the JSON object, no other text.
```

## Example Generation Prompt (for Coding Domain)

```
You are creating a SKILL.md file for the agent-skill-router repository.

DOMAIN: coding
TOPIC: code-review
DESCRIPTION: Analyzes code diffs for bugs and security vulnerabilities
ROLE: review
OUTPUT FORMAT: report

Create a complete, high-quality SKILL.md file following SKILL_FORMAT_SPEC.md requirements:

**YAML Frontmatter Requirements:**
- name: code-review (must match topic directory name exactly)
- description: Single line, 1-2 sentences. Active verb. Domain-specific terms.
- license: MIT
- compatibility: opencode
- metadata.version: "1.0.0"
- metadata.domain: coding
- metadata.role: review
- metadata.scope: review
- metadata.output-format: report
- metadata.triggers: 5-8 comma-separated keywords (technical + conversational)
- metadata.related-skills: coding-security-review, coding-test-driven-development

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
- At least one BAD vs GOOD code example pair
- MUST DO/MUST NOT DO constraints
- Reference to standard (OWASP, SOLID, etc.)

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

Generate the complete SKILL.md file content. Start with --- for YAML frontmatter.
```

## Example Output (for Coding Code-Review Skill)

```markdown
---
name: code-review
description: Analyzes code diffs and files to identify bugs, security vulnerabilities, code smells, and architectural concerns, producing a structured review report with prioritized, actionable feedback
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  role: review
  scope: review
  output-format: report
  triggers: code review, pull request, PR review, code quality, security audit, OWASP, architectural review
  related-skills: coding-security-review, coding-test-driven-development
---

# Code Reviewer

Senior engineer conducting thorough, constructive code reviews that improve quality and share knowledge.

## TL;DR Checklist

- [ ] Read PR description and understand the problem being solved
- [ ] Check for security vulnerabilities (OWASP Top 10 as baseline)
- [ ] Validate test coverage and quality
- [ ] Provide specific, actionable feedback with code examples
- [ ] Prioritize feedback (critical → minor)

## TL;DR for Code Generation

- Return simple types (bool, str, int, list)
- Handle null/empty cases explicitly
- Cyclomatic complexity ≤ 10 per function
- Use guard clauses for early returns
- No subprocess calls in pure logic functions

## When to Use

- Reviewing pull requests
- Conducting code quality audits
- Checking for security vulnerabilities
- Validating architectural decisions
- Identifying refactoring opportunities

## When NOT to Use

- For style-only reviews (use linters or formatters)
- When you don't understand the business context
- For quick fixes without proper review
- When under time pressure that compromises quality

## Core Workflow

1. **Context** — Read PR description, understand the problem. **Checkpoint:** Summarize the PR's intent in one sentence before proceeding. If you cannot, ask the author to clarify.
2. **Structure** — Review architecture and design decisions. Ask: Does this follow existing patterns in the codebase? Are new abstractions justified?
3. **Details** — Check code quality, security, and performance. Apply the checks in the Reference Guide below. Ask: Are there N+1 queries, hardcoded secrets, or injection risks?
4. **Tests** — Validate test coverage and quality. Ask: Are edge cases covered? Do tests assert behavior, not implementation?
5. **Feedback** — Produce a categorized report using the Output Template. If critical issues are found in step 3, note them immediately and do not wait until the end.

## Reference Guide

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Review Checklist | `references/review-checklist.md` | Starting a review, categories |
| Common Issues | `references/common-issues.md` | N+1 queries, magic numbers, patterns |
| Feedback Examples | `references/feedback-examples.md` | Writing good feedback |
| Report Template | `references/report-template.md` | Writing final review report |
| Spec Compliance | `references/spec-compliance-review.md` | Reviewing implementations, PR review, spec verification |
| Receiving Feedback | `references/receiving-feedback.md` | Responding to review comments, handling feedback |

## Review Patterns (Quick Reference)

### N+1 Query — Bad vs Good

```python
# BAD: query inside loop
for user in users:
    orders = Order.objects.filter(user=user)  # N+1

# GOOD: prefetch in bulk
users = User.objects.prefetch_related('orders').all()
```

### Magic Number — Bad vs Good

```python
# BAD
if status == 3:
    ...

# GOOD
ORDER_STATUS_SHIPPED = 3
if status == ORDER_STATUS_SHIPPED:
    ...
```

### Security: SQL Injection — Bad vs Good

```python
# BAD: string interpolation in query
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# GOOD: parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
```

## Constraints

### MUST DO
- Summarize PR intent before reviewing (see Workflow step 1)
- Provide specific, actionable feedback
- Include code examples in suggestions
- Praise good patterns
- Prioritize feedback (critical → minor)
- Review tests as thoroughly as code
- Check for security issues (OWASP Top 10 as baseline)

### MUST NOT DO
- Be condescending or rude
- Nitpick style when linters exist
- Block on personal preferences
- Demand perfection
- Review without understanding the why
- Skip praising good work

## Output Template

Code review report must include:
1. **Summary** — One-sentence intent recap + overall assessment
2. **Critical issues** — Must fix before merge (bugs, security, data loss)
3. **Major issues** — Should fix (performance, design, maintainability)
4. **Minor issues** — Nice to have (naming, readability)
5. **Positive feedback** — Specific patterns done well
6. **Questions for author** — Clarifications needed
7. **Verdict** — Approve / Request Changes / Comment

## Knowledge Reference

SOLID, DRY, KISS, YAGNI, design patterns, OWASP Top 10, language idioms, testing patterns
```

## Trigger Generation Prompt

```
Generate 5-8 triggers for a skill about {topic} in the {domain} domain.

Triggers should include:
1. Core topic name
2. Technical terms (abbreviations, jargon)
3. Conversational variants ("how do I...", "what is...")
4. Business language and colloquialisms
5. Adjacent technologies

Format as comma-separated list, no numbers.

Examples:
- For "code-review" in "coding": code review, pull request, PR review, code quality, security audit, OWASP, architectural review
- For "stop-loss" in "trading": stop loss, trailing stop, ATR stop, risk management, position protection, emergency stop, stop-loss
- For "prometheus" in "cncf": prometheus, promql, alerting rules, metrics scraping, kube-state-metrics, servicemonitor, time-series database
```

## Validation Prompt

```
You are validating a SKILL.md file. Respond with EXACTLY ONE LINE — nothing else.

FAIL this skill if ANY are true:
1. Core Workflow section has only vague steps with no real commands, file paths, or code
2. MUST DO / MUST NOT DO section is absent or contains only generic advice like 'follow best practices'
3. Code examples are empty pseudocode with no real implementation (e.g., 'your code here', 'implement logic')
4. Triggers are only ultra-generic single words with no domain-specific phrases

PASS the skill if it has: real working code, specific command-line steps, and domain-specific constraints.

Respond with EXACTLY one of:
PASS
FAIL: <one sentence naming the specific problem>
```

## Best Practices for Prompt Engineering

### 1. Be Specific and Action-Oriented

**Good**: "Create a code review skill that analyzes pull requests for security vulnerabilities"

**Bad**: "Make a skill"

### 2. Provide Context

**Good**: "Create a trading skill for risk management that implements stop-loss mechanisms with ATR-based calculations"

**Bad**: "Make a trading skill"

### 3. Include Domain-Specific Requirements

**Good**: "Create a CNCF skill for Kubernetes that includes YAML manifests and architecture diagrams"

**Bad**: "Make a CNCF skill"

### 4. Specify Quality Requirements

**Good**: "Generate a skill with typed Python functions, BAD/GOOD code examples, and concrete constraints"

**Bad**: "Make a skill"

## Troubleshooting Prompt Issues

### Issue: Generated content is too short

**Solution**: Add to prompt:
```
Ensure the skill is at least 3000 bytes with comprehensive code examples and detailed workflows.
```

### Issue: Missing code examples

**Solution**: Add to prompt:
```
Include at least 2 complete code blocks with typed Python signatures, docstrings, and BAD vs GOOD examples.
```

### Issue: Triggers are too generic

**Solution**: Add to prompt:
```
Generate 5-8 specific triggers including technical terms, conversational variants, and domain-specific phrases.
```

### Issue: Content is too generic

**Solution**: Add to prompt:
```
Use domain-specific language and terminology. Include concrete examples with file paths, commands, and actual code.
```

## Template Customization

### For Custom Domains

Add to domain requirements:
```python
{
    "custom-domain": "- Custom requirement 1\n- Custom requirement 2\n- Custom requirement 3",
}
```

### For Custom Roles

Update role defaults:
```python
{
    "custom-role": {
        "default_scope": "custom-scope",
        "default_output_format": "custom-format",
    }
}
```

### For Custom Quality Gates

Add validation checks:
```python
def custom_validation(content: str) -> List[str]:
    errors = []
    # Add custom checks
    return errors
```

## Advanced Usage

### Multi-Stage Generation

1. **Stage 1**: Generate outline
2. **Stage 2**: Expand each section
3. **Stage 3**: Add code examples
4. **Stage 4**: Final review and polish

### Iterative Refinement

```bash
# Generate initial skill
python3 scripts/generate_skill.py --task "Create a skill" --dry-run

# Review and refine
# Edit the generated content

# Regenerate with improvements
python3 scripts/generate_skill.py --domain coding --topic my-skill --contribute
```

### Batch Generation

```bash
# Generate multiple skills
for skill in "code-review" "risk-stop-loss" "kubernetes-deployment"; do
    python3 scripts/generate_skill.py --task "Create a $skill skill" --dry-run
done
```

## Integration with Other Tools

### With reformat_skills.py

The generated skill is automatically reformatted:
```bash
python3 scripts/generate_skill.py --task "Create a skill" --contribute
# Automatically runs: python3 scripts/reformat_skills.py
```

### With enhance_triggers.py

Triggers are automatically enhanced:
```bash
python3 scripts/generate_skill.py --task "Create a skill" --contribute
# Automatically runs: python3 scripts/enhance_triggers.py
```

### With generate_index.py

The skill index is automatically updated:
```bash
python3 scripts/generate_skill.py --task "Create a skill" --contribute
# Automatically runs: python3 scripts/generate_index.py
```

### With validate_skill.sh

The skill is automatically validated:
```bash
python3 scripts/generate_skill.py --task "Create a skill" --contribute
# Automatically runs: bash scripts/validate_skill.sh
```

## Performance Optimization

### Use Cheaper Models

```bash
python3 scripts/generate_skill.py --task "Create a skill" --model gpt-4o-mini
```

### Reduce Timeout for Fast Iteration

```bash
python3 scripts/generate_skill.py --task "Create a skill" --timeout 30
```

### Skip Automation for Testing

```bash
python3 scripts/generate_skill.py --task "Create a skill" --dry-run
```

## Common Patterns

### Pattern 1: Start with Dry Run

```bash
python3 scripts/generate_skill.py --task "Create a code review skill" --dry-run
```

### Pattern 2: Review and Regenerate

```bash
# Generate
python3 scripts/generate_skill.py --task "Create a skill" --dry-run

# Review content
# Make adjustments

# Regenerate
python3 scripts/generate_skill.py --domain coding --topic my-skill --contribute
```

### Pattern 3: Domain-Specific Generation

```bash
python3 scripts/generate_skill.py \
  --domain trading \
  --topic risk-stop-loss \
  --description "Implements stop-loss strategies for risk management in algorithmic trading" \
  --contribute
```

## See Also

- [SKILL_FORMAT_SPEC.md](../SKILL_FORMAT_SPEC.md) - Complete skill format specification
- [AGENTS.md](../AGENTS.md) - Agent orchestration guide
- [generate_skill.py](generate_skill.py) - Main generation script
- [validate_skill.sh](../scripts/validate_skill.sh) - Quality validation script
- [reformat_skills.py](../scripts/reformat_skills.py) - YAML normalization script
- [enhance_triggers.py](../scripts/enhance_triggers.py) - Trigger enhancement script
- [generate_index.py](../scripts/generate_index.py) - Skill index generator
