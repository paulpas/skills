# Skill Generation Script Documentation

## Overview

The `scripts/generate_skill.py` script automatically generates high-quality `SKILL.md` files for the agent-skill-router repository. It parses user task descriptions to extract domain and topic, then uses an LLM to generate complete skill content following the SKILL_FORMAT_SPEC.md guidelines.

## Quick Start

```bash
# Generate a skill from a task description
python3 scripts/generate_skill.py --task "Create a code review skill"

# Generate a skill with explicit domain and topic
python3 scripts/generate_skill.py --domain coding --topic my-skill

# Dry run (generate without saving)
python3 scripts/generate_skill.py --task "Create a stop loss mechanism" --dry-run

# Generate and contribute to the repository
python3 scripts/generate_skill.py --domain trading --topic risk-stop-loss --contribute
```

## Requirements

### Python Packages

```bash
pip install openai pyyaml python-dotenv
```

### Environment Variables

```bash
# Required for LLM generation
export OPENAI_API_KEY="your-api-key-here"

# Optional configuration
export AUTO_SKILL_MODEL="gpt-4o-mini"        # Default LLM model
export AUTO_SKILL_TIMEOUT=60                   # Request timeout in seconds
export AUTO_SKILL_MAX_RETRIES=3                # Maximum retries on failure
export AUTO_SKILL_CACHE_DIR=".skill-cache/"   # Local cache directory
export AUTO_SKILL_CONTRIBUTE=false            # Whether to commit to git
```

## Usage

### Command Line Arguments

```bash
python3 scripts/generate_skill.py [OPTIONS]
```

| Argument | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| `--task` | string | conditional | - | Task description to parse for domain and topic |
| `--domain` | string | conditional | - | Skill domain (agent, cncf, coding, programming, trading) |
| `--topic` | string | conditional | - | Skill topic (kebab-case) |
| `--description` | string | no | auto-generated | Skill description (overrides auto-generated) |
| `--dry-run` | flag | no | false | Generate skill content without saving |
| `--contribute` | flag | no | false | Save to skills directory and run automation scripts |
| `--model` | string | no | gpt-4o-mini | LLM model for generation |
| `--timeout` | integer | no | 60 | Request timeout in seconds |
| `--max-retries` | integer | no | 3 | Maximum retries on failure |
| `--cache-dir` | string | no | .skill-cache/ | Cache directory |

### Argument Combinations

```bash
# Option 1: Parse from task description
python3 scripts/generate_skill.py --task "Build a code review skill that analyzes pull requests"

# Option 2: Explicit domain and topic
python3 scripts/generate_skill.py --domain coding --topic code-review --description "Analyzes code diffs for bugs and security issues"

# Option 3: Dry run for review
python3 scripts/generate_skill.py --task "Create a Kubernetes deployment skill" --dry-run

# Option 4: Contribute to repository
python3 scripts/generate_skill.py --domain trading --topic risk-stop-loss --contribute
```

## Quality Gates

The script validates generated skills against the following quality gates:

### 1. Sentinel String Check
- **FAILS**: Contains "Implementing this specific pattern or feature"
- **PASS**: No sentinel string found

### 2. File Size Check
- **FAILS**: Less than 3000 bytes
- **PASS**: 3000+ bytes

### 3. Code Blocks Check (for implementation skills)
- **FAILS**: Fewer than 2 complete code blocks (4 fence markers)
- **PASS**: 2+ code blocks

### 4. Triggers Check
- **WARNING**: Fewer than 3 or more than 8 triggers
- **PASS**: 3-8 triggers

### 5. Required Sections
- **WARNING**: Missing "When to Use" or "Core Workflow" sections
- **PASS**: All required sections present

## Quality Gate Validation

```bash
# The script runs validation automatically
python3 scripts/generate_skill.py --domain coding --topic my-skill --contribute
```

Validation output:
```
✓ Quality gate passed
  Domain: coding
  Topic: my-skill
  File: /path/to/skills/coding/my-skill/SKILL.md
  Size: 5234 bytes
```

If validation fails:
```
❌ Quality gate failed:
  - Contains sentinel string 'Implementing this specific pattern or feature'
  - File size (2500 bytes) is under 3000 bytes minimum
```

## Integration Points

### 1. Reformat Skills Script
After skill creation, the script runs `scripts/reformat_skills.py` to:
- Validate YAML syntax
- Normalize formatting (indentation, field order)
- Fill in missing optional metadata fields

### 2. Enhance Triggers Script
The script runs `scripts/enhance_triggers.py` to:
- Add user-friendly conversational variants
- Include common "how do I..." questions
- Add business language and colloquialisms
- Maintain the 5-8 term trigger limit

### 3. Generate Index Script
The script runs `scripts/generate_index.py` to:
- Extract metadata from SKILL.md files
- Generate `skills-index.json` for skill-router
- Enable auto-loading of skills based on triggers

### 4. Validation Script
The script runs `scripts/validate_skill.sh` to:
- Check for sentinel string
- Verify file size
- Count code blocks
- Detect generic Core Workflow patterns
- (Optional) Run LLM quality check

## Workflow

### 1. Parse Task Description
The script uses an LLM to extract domain and topic from the task description:

```python
# Input: "Create a code review skill"
# Output: domain="coding", topic="code-review"
```

### 2. Generate Skill Content
The script uses an LLM to generate complete SKILL.md content:

```python
# Generates:
# - YAML frontmatter with all required fields
# - H1 title
# - Role/purpose paragraph
# - TL;DR Checklist
# - TL;DR for Code Generation (for implementation skills)
# - When to Use section
# - When NOT to Use section
# - Core Workflow section
# - Implementation Patterns with code examples
# - Constraints section
# - Output Template (if needed)
# - Related Skills table
```

### 3. Validate Content
The script validates against quality gates:

```python
# Checks:
# - No sentinel string
# - 3000+ bytes
# - Required sections present
# - Code blocks present (if implementation)
# - Triggers count (3-8)
```

### 4. Save and Automate
If `--contribute` flag is set:
1. Save to `skills/{domain}/{topic}/SKILL.md`
2. Run `reformat_skills.py`
3. Run `enhance_triggers.py`
4. Run `generate_index.py`
5. Run `validate_skill.sh`

## Example Output

### Generated Skill File

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

- [ ] Read PR description and understand the problem
- [ ] Check for security vulnerabilities (OWASP Top 10)
- [ ] Validate test coverage and quality
- [ ] Provide specific, actionable feedback with code examples

## TL;DR for Code Generation

- Return simple types (bool, str, int, list)
- Handle null/empty cases explicitly
- Cyclomatic complexity ≤ 10 per function
- Use guard clauses for early returns

## When to Use

- Reviewing pull requests
- Conducting code quality audits
- Checking for security vulnerabilities
- Validating architectural decisions

## When NOT to Use

- For style-only reviews (use linters)
- When you don't understand the business context
- For quick fixes without proper review

## Core Workflow

1. **Context** — Read PR description, understand the problem. **Checkpoint:** Summarize in one sentence before proceeding.
2. **Structure** — Review architecture and design decisions.
3. **Details** — Check code quality, security, and performance.
4. **Tests** — Validate test coverage and quality.
5. **Feedback** — Produce categorized report using Output Template.

## Implementation Patterns

### N+1 Query — Bad vs Good

```python
# BAD: query inside loop
for user in users:
    orders = Order.objects.filter(user=user)  # N+1

# GOOD: prefetch in bulk
users = User.objects.prefetch_related('orders').all()
```

## Constraints

### MUST DO
- Summarize PR intent before reviewing
- Provide specific, actionable feedback
- Include code examples in suggestions
- Praise good patterns
- Prioritize feedback (critical → minor)

### MUST NOT DO
- Be condescending or rude
- Nitpick style when linters exist
- Block on personal preferences
- Demand perfection

## Output Template

Code review report must include:
1. **Summary** — One-sentence intent recap + overall assessment
2. **Critical issues** — Must fix before merge
3. **Major issues** — Should fix
4. **Minor issues** — Nice to have
5. **Positive feedback** — Specific patterns done well
6. **Questions for author** — Clarifications needed
7. **Verdict** — Approve / Request Changes / Comment

## Related Skills

| Skill | Purpose |
|---|---|
| `coding-security-review` | Security-focused code review |
| `coding-test-driven-development` | TDD patterns and practices |
```

## Troubleshooting

### LLM Generation Fails

**Problem**: OpenAI API error or timeout

**Solutions**:
1. Check `OPENAI_API_KEY` is set
2. Increase timeout: `--timeout 120`
3. Increase retries: `--max-retries 5`
4. Try a different model: `--model gpt-4o`

### Validation Fails

**Problem**: Quality gate validation fails

**Solutions**:
1. Generate longer content (increase LLM temperature or max_tokens)
2. Add more code examples
3. Expand the Core Workflow section
4. Add more triggers

### Automation Scripts Fail

**Problem**: reformat/enhance/generate scripts fail

**Solutions**:
1. Run scripts manually: `python3 scripts/reformat_skills.py`
2. Check Python dependencies are installed
3. Verify script permissions
4. Run without automation: `--dry-run`

## Dry Run Mode

Dry run mode generates and validates skill content without saving files:

```bash
python3 scripts/generate_skill.py --task "Create a stop loss mechanism" --dry-run
```

Output:
```
============================================================
DRY RUN - No files will be saved
============================================================

Generated SKILL.md content:

---
name: risk-stop-loss
description: Implements stop loss strategies for risk management in algorithmic trading
...

============================================================
Dry run complete - content validated successfully
```

## Customization

### Domain-Specific Templates

The script uses domain-specific templates for different domains:

| Domain | Default Role | Default Output Format |
|--------|-------------|----------------------|
| agent | orchestration | analysis |
| cncf | reference | manifests |
| coding | implementation | code |
| programming | reference | code |
| trading | implementation | code |

### Trigger Enhancement

The script integrates with `enhance_triggers.py` to add:
- User-friendly conversational variants
- Common "how do I..." questions
- Business language and colloquialisms
- Adjacent technology names

## Performance

### Typical Generation Times

| Step | Time |
|------|------|
| Task parsing | 1-2 seconds |
| Content generation | 10-30 seconds |
| Quality validation | <1 second |
| Automation scripts | 2-5 seconds |

### Cost Optimization

```bash
# Use cheaper model for generation
python3 scripts/generate_skill.py --task "Create a skill" --model gpt-4o-mini

# Use dry run for testing
python3 scripts/generate_skill.py --task "Test skill" --dry-run
```

## Best Practices

### 1. Provide Clear Task Descriptions

```bash
# Good
python3 scripts/generate_skill.py --task "Create a code review skill that analyzes pull requests for security vulnerabilities"

# Bad
python3 scripts/generate_skill.py --task "Make a skill"
```

### 2. Use Dry Run for Testing

```bash
# Test generation before saving
python3 scripts/generate_skill.py --task "Test skill" --dry-run
```

### 3. Review Generated Content

Always review generated content before committing:
```bash
# Open the file in your editor
code skills/coding/my-skill/SKILL.md
```

### 4. Run Validation Before Committing

```bash
# Run the validation script manually
bash scripts/validate_skill.sh skills/coding/my-skill/SKILL.md
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Generate Skill

on:
  push:
    branches: [main]
    paths: ['skills/**']

jobs:
  generate-skill:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install openai pyyaml python-dotenv
      
      - name: Generate skill
        run: |
          python3 scripts/generate_skill.py --task "${{ github.event.head_commit.message }}" --contribute
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      
      - name: Commit changes
        run: |
          git add -A
          git commit -m "feat: auto-generate skill" || echo "No changes to commit"
          git push
```

## Contributing

When contributing new skills:

1. Test with `--dry-run` first
2. Review generated content
3. Run validation: `bash scripts/validate_skill.sh`
4. Test with real agent interactions
5. Update README if needed

## See Also

- [SKILL_FORMAT_SPEC.md](../SKILL_FORMAT_SPEC.md) - Complete skill format specification
- [AGENTS.md](../AGENTS.md) - Agent orchestration guide
- [FAQ.md](../FAQ.md) - Common questions and answers
- `scripts/validate_skill.sh` - Quality validation script
- `scripts/reformat_skills.py` - YAML normalization script
- `scripts/enhance_triggers.py` - Trigger enhancement script
- `scripts/generate_index.py` - Skill index generator
