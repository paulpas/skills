# generate_skill.py

**Auto-generate SKILL.md files for the agent-skill-router repository**

## Quick Start

```bash
# Install dependencies
pip install -r scripts/generate_skill_requirements.txt

# Generate a skill from a task description
python3 scripts/generate_skill.py --task "Create a code review skill"

# Generate with explicit domain and topic
python3 scripts/generate_skill.py --domain coding --topic my-skill

# Dry run (generate without saving)
python3 scripts/generate_skill.py --task "Create a stop loss mechanism" --dry-run

# Generate and contribute to repository
python3 scripts/generate_skill.py --domain trading --topic risk-stop-loss --contribute
```

## Overview

`generate_skill.py` is an automated skill generation script that:

- **Parses task descriptions** to extract domain and topic
- **Uses LLM** to generate high-quality SKILL.md content
- **Validates quality gates** before saving
- **Integrates with automation scripts** for YAML normalization, trigger enhancement, and index generation
- **Follows SKILL_FORMAT_SPEC.md** for consistent format

## Features

✅ **Automatic Domain/Topic Extraction** - Parse natural language task descriptions  
✅ **LLM-Powered Generation** - Use OpenAI models for content generation  
✅ **Quality Gate Validation** - Check for sentinel strings, file size, code blocks, triggers  
✅ **Domain-Specific Templates** - Custom templates for agent, cncf, coding, programming, trading  
✅ **Automation Integration** - Run reformat, enhance, and index scripts automatically  
✅ **Dry Run Mode** - Test generation without saving files  
✅ **Custom Configuration** - Environment variables for model, timeout, retries, cache  

## Requirements

### Python Packages

```bash
pip install openai pyyaml python-dotenv
```

### Environment Variables

```bash
export OPENAI_API_KEY="your-api-key-here"
export AUTO_SKILL_MODEL="gpt-4o-mini"        # Optional
export AUTO_SKILL_TIMEOUT=60                  # Optional
export AUTO_SKILL_MAX_RETRIES=3               # Optional
export AUTO_SKILL_CACHE_DIR=".skill-cache/"  # Optional
```

## Usage

### Basic Commands

```bash
# Generate from task description
python3 scripts/generate_skill.py --task "Create a code review skill"

# Generate with explicit domain and topic
python3 scripts/generate_skill.py --domain coding --topic my-skill

# Dry run (no files saved)
python3 scripts/generate_skill.py --task "Create a skill" --dry-run

# Contribute to repository
python3 scripts/generate_skill.py --domain trading --topic risk-stop-loss --contribute
```

### Advanced Options

```bash
# Custom LLM model
python3 scripts/generate_skill.py --task "Create a skill" --model gpt-4o

# Custom timeout and retries
python3 scripts/generate_skill.py --task "Create a skill" --timeout 120 --max-retries 5

# Custom cache directory
python3 scripts/generate_skill.py --task "Create a skill" --cache-dir "/tmp/cache/"

# Custom description
python3 scripts/generate_skill.py \
  --domain coding \
  --topic my-skill \
  --description "Custom description for this skill"
```

### All Options

```bash
python3 scripts/generate_skill.py [OPTIONS]

Options:
  --task TEXT              Task description to parse for domain and topic
  --domain [agent|cncf|coding|programming|trading]
                           Skill domain
  --topic TEXT             Skill topic (kebab-case)
  --description TEXT       Skill description (overrides auto-generated)
  --dry-run                Generate skill content without saving
  --contribute             Save to skills directory and run automation scripts
  --model TEXT             LLM model for generation (default: gpt-4o-mini)
  --timeout INTEGER        Request timeout in seconds (default: 60)
  --max-retries INTEGER    Maximum retries on failure (default: 3)
  --cache-dir TEXT         Cache directory (default: .skill-cache/)
  -h, --help               Show this message and exit.
```

## Quality Gates

The script validates against these quality gates:

| Check | Requirement | Fail if |
|-------|-------------|---------|
| Sentinel String | Must not contain | "Implementing this specific pattern or feature" |
| File Size | Must be >= | 3000 bytes |
| Code Blocks | For implementation skills | Fewer than 2 code blocks |
| Triggers | Must have | 3-8 triggers |
| Required Sections | Must have | "When to Use", "Core Workflow" |

### Validation Output

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

Runs `scripts/reformat_skills.py` to:
- Validate YAML syntax
- Normalize formatting (indentation, field order)
- Fill in missing optional metadata fields

### 2. Enhance Triggers Script

Runs `scripts/enhance_triggers.py` to:
- Add user-friendly conversational variants
- Include common "how do I..." questions
- Add business language and colloquialisms

### 3. Generate Index Script

Runs `scripts/generate_index.py` to:
- Extract metadata from SKILL.md files
- Generate `skills-index.json` for skill-router
- Enable auto-loading of skills based on triggers

### 4. Validation Script

Runs `scripts/validate_skill.sh` to:
- Check for sentinel string
- Verify file size
- Count code blocks
- Detect generic Core Workflow patterns
- (Optional) Run LLM quality check

## Workflow

1. **Parse Task Description** - Extract domain and topic using LLM
2. **Generate Skill Content** - Generate complete SKILL.md using LLM
3. **Validate Content** - Check against quality gates
4. **Save File** - Save to `skills/{domain}/{topic}/SKILL.md`
5. **Run Automation** - Execute reformat, enhance, and index scripts
6. **Run Validation** - Execute quality validation script

## Example Output

### Generated Skill File

```markdown
---
name: code-review
description: Analyzes code diffs and files to identify bugs, security vulnerabilities, code smells, and architectural concerns
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  role: review
  scope: review
  output-format: report
  triggers: code review, pull request, PR review, code quality, security audit, OWASP, architectural review
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

## When to Use

- Reviewing pull requests
- Conducting code quality audits
- Checking for security vulnerabilities

## Core Workflow

1. **Context** — Read PR description. **Checkpoint:** Summarize in one sentence.
2. **Structure** — Review architecture and design decisions.
3. **Details** — Check code quality, security, and performance.
4. **Tests** — Validate test coverage and quality.
5. **Feedback** — Produce categorized report.

## Implementation Patterns

### N+1 Query — Bad vs Good

```python
# BAD: query inside loop
for user in users:
    orders = Order.objects.filter(user=user)

# GOOD: prefetch in bulk
users = User.objects.prefetch_related('orders').all()
```

## Constraints

### MUST DO
- Summarize PR intent before reviewing
- Provide specific, actionable feedback
- Include code examples in suggestions

### MUST NOT DO
- Be condescending or rude
- Nitpick style when linters exist
- Block on personal preferences

## Output Template

1. **Summary** — One-sentence intent recap
2. **Critical issues** — Must fix before merge
3. **Major issues** — Should fix
4. **Minor issues** — Nice to have
5. **Positive feedback** — Specific patterns done well
6. **Questions for author** — Clarifications needed
7. **Verdict** — Approve / Request Changes / Comment
```

## Domain-Specific Templates

| Domain | Default Role | Default Output Format | Required Elements |
|--------|-------------|----------------------|-------------------|
| agent | orchestration | analysis | ASCII flow diagram, code-philosophy, fallback routing |
| cncf | reference | manifests | YAML manifests, architecture diagrams, common pitfalls |
| coding | implementation | code | BAD/GOOD examples, MUST DO/MUST NOT DO, OWASP/SOLID |
| programming | reference | code | Implementation, complexity table, algorithm steps |
| trading | implementation | code | Typed Python, risk constraints, APEX file paths |

## Troubleshooting

### LLM Generation Fails

```bash
# Check API key
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:+SET}"

# Increase timeout
python3 scripts/generate_skill.py --task "Create a skill" --timeout 120

# Increase retries
python3 scripts/generate_skill.py --task "Create a skill" --max-retries 5

# Use different model
python3 scripts/generate_skill.py --task "Create a skill" --model gpt-4o
```

### Validation Fails

```bash
# Check file size
wc -c skills/coding/my-skill/SKILL.md

# Check for sentinel string
grep "Implementing this specific pattern or feature" skills/coding/my-skill/SKILL.md

# Check code blocks
grep -c '```' skills/coding/my-skill/SKILL.md

# Check triggers
grep "triggers:" skills/coding/my-skill/SKILL.md
```

### Automation Scripts Fail

```bash
# Run scripts manually
python3 scripts/reformat_skills.py
python3 scripts/enhance_triggers.py
python3 scripts/generate_index.py

# Check dependencies
pip install pyyaml

# Verify script permissions
chmod +x scripts/*.py
```

## Best Practices

### 1. Test with Dry Run

```bash
python3 scripts/generate_skill.py --task "Create a skill" --dry-run
```

### 2. Review Generated Content

```bash
code skills/coding/my-skill/SKILL.md
```

### 3. Run Validation Before Committing

```bash
bash scripts/validate_skill.sh skills/coding/my-skill/SKILL.md
```

### 4. Use Domain-Specific Descriptions

```bash
python3 scripts/generate_skill.py \
  --domain trading \
  --topic risk-stop-loss \
  --description "Implements stop-loss strategies (fixed percentage, ATR-based, trailing, support/resistance, volatility-adjusted) to limit position losses in algorithmic trading systems." \
  --contribute
```

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
# Use cheaper model
python3 scripts/generate_skill.py --task "Create a skill" --model gpt-4o-mini

# Use dry run for testing
python3 scripts/generate_skill.py --task "Test skill" --dry-run
```

## CI/CD Integration

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
          pip install -r scripts/generate_skill_requirements.txt
      
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

## Documentation

- [GENERATE_SKILL_README.md](GENERATE_SKILL_README.md) - Full documentation
- [PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md) - LLM prompt templates
- [EXAMPLE_USAGE.md](EXAMPLE_USAGE.md) - Example usage commands
- [SKILL_FORMAT_SPEC.md](../SKILL_FORMAT_SPEC.md) - Skill format specification

## See Also

- `scripts/generate_skill.py` - Main script
- `scripts/validate_skill.sh` - Quality validation
- `scripts/reformat_skills.py` - YAML reformatting
- `scripts/enhance_triggers.py` - Trigger enhancement
- `scripts/generate_index.py` - Index generation
- `scripts/validate_skills.py` - Python-based validation

## License

MIT

## Contributing

When contributing new skills:

1. Test with `--dry-run` first
2. Review generated content
3. Run validation: `bash scripts/validate_skill.sh`
4. Test with real agent interactions
5. Update README if needed
