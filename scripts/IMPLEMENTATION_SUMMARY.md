# Skill Generation Script - Implementation Summary

## Overview

Created `scripts/generate_skill.py` - an automated skill generation script for the agent-skill-router repository that:

- Parses user task descriptions to extract domain and topic
- Uses LLM (OpenAI) to generate complete SKILL.md files
- Validates against quality gates
- Integrates with automation scripts
- Follows SKILL_FORMAT_SPEC.md guidelines

## Files Created

### 1. Main Script
- **File**: `scripts/generate_skill.py`
- **Size**: ~700 lines
- **Permissions**: Executable

### 2. Documentation
- **File**: `scripts/README_generate_skill.md` - Quick start guide
- **File**: `scripts/GENERATE_SKILL_README.md` - Full documentation
- **File**: `scripts/PROMPT_TEMPLATES.md` - LLM prompt templates
- **File**: `scripts/EXAMPLE_USAGE.md` - 35 example usage commands

### 3. Dependencies
- **File**: `scripts/generate_skill_requirements.txt` - Python package requirements

## Key Features

### 1. Task Parsing
```python
def parse_task_to_domain_topic(self, task: str) -> Tuple[str, str]:
    """Extract domain and topic from task description using LLM."""
```
- Parses natural language task descriptions
- Returns domain (agent/cncf/coding/programming/trading) and topic (kebab-case)

### 2. Content Generation
```python
def generate_skill_content(
    self, domain: str, topic: str, description: str,
    role: Optional[str] = None, output_format: Optional[str] = None
) -> str:
    """Generate complete SKILL.md content using LLM."""
```
- Generates YAML frontmatter with all required fields
- Creates all content sections (H1 title, TL;DR, When to Use, etc.)
- Domain-specific templates for different skill types

### 3. Quality Gate Validation
```python
def validate_skill_content(self, content: str) -> Tuple[bool, List[str]]:
    """Validate generated skill content against quality gates."""
```
- Checks for sentinel string
- Validates file size (≥3000 bytes)
- Verifies code blocks (≥2 for implementation skills)
- Validates trigger count (3-8)
- Checks required sections

### 4. Integration Points

#### Reformat Skills Script
```python
def run_reformat_script(self, skill_file: Path) -> bool:
    """Run reformat_skills.py to normalize YAML."""
```
- Validates YAML syntax
- Normalizes formatting
- Fills in missing optional metadata fields

#### Enhance Triggers Script
```python
def run_enhance_triggers_script(self, skill_file: Path) -> bool:
    """Run enhance_triggers.py to improve triggers."""
```
- Adds user-friendly conversational variants
- Includes "how do I..." questions
- Adds business language and colloquialisms

#### Generate Index Script
```python
def run_generate_index_script(self, skill_file: Path) -> bool:
    """Run generate_index.py to update skills-index.json."""
```
- Extracts metadata from SKILL.md files
- Generates `skills-index.json` for skill-router
- Enables auto-loading based on triggers

#### Validation Script
```python
def run_validation_script(self, skill_file: Path) -> bool:
    """Run validate_skill.sh for quality checks."""
```
- Checks for sentinel string
- Verifies file size
- Counts code blocks
- Detects generic Core Workflow patterns
- Optional LLM quality check

## Command Line Interface

### Basic Usage
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
  --description "Custom description"
```

### All Options
```
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

### Validation Checks

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

### Trigger Enhancement

The script integrates with `enhance_triggers.py` to add:
- User-friendly conversational variants
- Common "how do I..." questions
- Business language and colloquialisms
- Adjacent technology names

## Domain-Specific Templates

| Domain | Default Role | Default Output Format | Required Elements |
|--------|-------------|----------------------|-------------------|
| agent | orchestration | analysis | ASCII flow diagram, code-philosophy, fallback routing |
| cncf | reference | manifests | YAML manifests, architecture diagrams, common pitfalls |
| coding | implementation | code | BAD/GOOD examples, MUST DO/MUST NOT DO, OWASP/SOLID |
| programming | reference | code | Implementation, complexity table, algorithm steps |
| trading | implementation | code | Typed Python, risk constraints, APEX file paths |

## LLM Prompt Templates

### Main Generation Prompt
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

## Workflow

### 1. Parse Task Description
```
User: "Create a code review skill"
→ LLM extracts: domain="coding", topic="code-review"
```

### 2. Generate Skill Content
```
→ LLM generates complete SKILL.md with:
   - YAML frontmatter (all required fields)
   - H1 title
   - Role/purpose paragraph
   - TL;DR Checklist
   - TL;DR for Code Generation
   - When to Use section
   - When NOT to Use section
   - Core Workflow section
   - Implementation Patterns with code examples
   - Constraints section
   - Output Template (if needed)
   - Related Skills table
```

### 3. Validate Content
```
→ Check:
   - No sentinel string
   - 3000+ bytes
   - Required sections present
   - Code blocks present (if implementation)
   - Triggers count (3-8)
```

### 4. Save and Automate
```
→ If --contribute flag:
   1. Save to skills/{domain}/{topic}/SKILL.md
   2. Run reformat_skills.py
   3. Run enhance_triggers.py
   4. Run generate_index.py
   5. Run validate_skill.sh
```

## Example Usage

### Basic Example
```bash
# Generate skill from task
python3 scripts/generate_skill.py --task "Create a code review skill"

# Output:
# ✓ Quality gate passed
#   Domain: coding
#   Topic: code-review
#   File: /home/paulpas/git/agent-skill-router/skills/coding/code-review/SKILL.md
#   Size: 5234 bytes
```

### Dry Run Example
```bash
# Test generation without saving
python3 scripts/generate_skill.py --task "Create a stop loss mechanism" --dry-run

# Output:
# ============================================================
# DRY RUN - No files will be saved
# ============================================================
# Generated SKILL.md content:
# --- 
# name: risk-stop-loss
# ...
```

### Contribute Example
```bash
# Generate and contribute to repository
python3 scripts/generate_skill.py \
  --domain trading \
  --topic risk-stop-loss \
  --description "Implements stop-loss strategies for risk management" \
  --contribute

# Output:
# ✓ Skill generated successfully
#   Domain: trading
#   Topic: risk-stop-loss
#   File: skills/trading/risk-stop-loss/SKILL.md
#   Size: 6123 bytes
#   Contribute: True
```

## Integration with Existing Scripts

### 1. reformat_skills.py
```bash
# Automatically runs after skill creation
python3 scripts/reformat_skills.py
```
- Validates YAML syntax
- Normalizes formatting
- Fills in missing optional metadata fields

### 2. enhance_triggers.py
```bash
# Automatically runs after skill creation
python3 scripts/enhance_triggers.py
```
- Adds user-friendly conversational variants
- Includes common "how do I..." questions
- Adds business language and colloquialisms

### 3. generate_index.py
```bash
# Automatically runs after skill creation
python3 scripts/generate_index.py
```
- Extracts metadata from SKILL.md files
- Generates `skills-index.json` for skill-router
- Enables auto-loading based on triggers

### 4. validate_skill.sh
```bash
# Automatically runs after skill creation
bash scripts/validate_skill.sh skills/coding/my-skill/SKILL.md
```
- Checks for sentinel string
- Verifies file size
- Counts code blocks
- Detects generic Core Workflow patterns

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

## Environment Variables

```bash
# Required for LLM generation
export OPENAI_API_KEY="your-api-key-here"

# Optional configuration
export AUTO_SKILL_MODEL="gpt-4o-mini"        # Default LLM model
export AUTO_SKILL_TIMEOUT=60                  # Request timeout in seconds
export AUTO_SKILL_MAX_RETRIES=3               # Maximum retries on failure
export AUTO_SKILL_CACHE_DIR=".skill-cache/"   # Local cache directory
export AUTO_SKILL_CONTRIBUTE=false            # Whether to commit to git
```

## Dependencies

### Required Packages
```bash
pip install openai pyyaml python-dotenv
```

### Requirements File
```
# scripts/generate_skill_requirements.txt
openai>=1.0.0
pyyaml>=6.0.0
python-dotenv>=1.0.0
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

## Documentation Files

### Main Documentation
- **README_generate_skill.md** - Quick start guide
- **GENERATE_SKILL_README.md** - Full documentation

### Reference Documentation
- **PROMPT_TEMPLATES.md** - LLM prompt templates
- **EXAMPLE_USAGE.md** - 35 example usage commands

### Related Documentation
- **SKILL_FORMAT_SPEC.md** - Skill format specification
- **AGENTS.md** - Agent orchestration guide
- **FAQ.md** - Common questions and answers

## Quality Checklist

### Before Committing

- [ ] Test with `--dry-run` first
- [ ] Review generated content
- [ ] Run validation: `bash scripts/validate_skill.sh`
- [ ] Check file size >= 3000 bytes
- [ ] Check no sentinel string
- [ ] Check code blocks (if implementation)
- [ ] Check triggers count (3-8)
- [ ] Test with real agent interactions
- [ ] Update README if needed

### Quality Gates

- [ ] No sentinel string "Implementing this specific pattern or feature"
- [ ] File size >= 3000 bytes
- [ ] At least 2 code blocks for implementation skills
- [ ] 3-8 triggers in metadata
- [ ] All required sections present

## Summary

The `generate_skill.py` script provides:

✅ **Automated skill generation** from task descriptions  
✅ **LLM-powered content creation** with domain-specific templates  
✅ **Quality gate validation** before saving  
✅ **Integration with automation scripts** for YAML normalization, trigger enhancement, and index generation  
✅ **Flexible CLI options** for customization  
✅ **Comprehensive documentation** and examples  

The script follows SKILL_FORMAT_SPEC.md guidelines and integrates seamlessly with the existing automation infrastructure.
