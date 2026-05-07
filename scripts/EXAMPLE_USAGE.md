# Example Usage Commands for generate_skill.py

## Basic Examples

### 1. Generate from Task Description

```bash
# Parse task and generate skill
python3 scripts/generate_skill.py --task "Create a code review skill that analyzes pull requests"

# Parse complex task description
python3 scripts/generate_skill.py --task "Build a trading risk management system with stop-loss mechanisms and position sizing"
```

### 2. Generate with Explicit Domain and Topic

```bash
# Basic skill generation
python3 scripts/generate_skill.py --domain coding --topic my-new-skill

# Trading skill
python3 scripts/generate_skill.py --domain trading --topic risk-stop-loss

# CNCF skill
python3 scripts/generate_skill.py --domain cncf --topic kubernetes-deployment

# Agent skill
python3 scripts/generate_skill.py --domain agent --topic confidence-based-selector

# Programming skill
python3 scripts/generate_skill.py --domain programming --topic sorting-algorithms
```

### 3. Dry Run (Generate Without Saving)

```bash
# Test skill generation without saving files
python3 scripts/generate_skill.py --task "Create a stop loss mechanism" --dry-run

# Test with explicit domain and topic
python3 scripts/generate_skill.py --domain coding --topic code-review --dry-run

# Test with custom description
python3 scripts/generate_skill.py --domain trading --topic risk-stop-loss --dry-run --description "Implements stop-loss strategies for risk management"
```

### 4. Generate and Contribute to Repository

```bash
# Generate and save to skills directory
python3 scripts/generate_skill.py --domain coding --topic my-skill --contribute

# Generate with custom description
python3 scripts/generate_skill.py \
  --domain trading \
  --topic risk-stop-loss \
  --description "Implements stop-loss strategies for risk management in algorithmic trading" \
  --contribute

# Generate with all options
python3 scripts/generate_skill.py \
  --task "Create a Kubernetes deployment skill" \
  --description "Creates Kubernetes deployment manifests with best practices" \
  --contribute
```

## Advanced Examples

### 5. Custom LLM Model

```bash
# Use cheaper model for generation
python3 scripts/generate_skill.py \
  --task "Create a skill" \
  --model gpt-4o-mini

# Use more capable model
python3 scripts/generate_skill.py \
  --task "Create a complex skill" \
  --model gpt-4o
```

### 6. Custom Timeout and Retries

```bash
# Increase timeout for complex skills
python3 scripts/generate_skill.py \
  --task "Create a comprehensive skill" \
  --timeout 120

# Increase retries for reliability
python3 scripts/generate_skill.py \
  --task "Create a skill" \
  --max-retries 5
```

### 7. Custom Cache Directory

```bash
# Use custom cache directory
python3 scripts/generate_skill.py \
  --task "Create a skill" \
  --cache-dir "/tmp/skill-cache/"

# Use project cache
python3 scripts/generate_skill.py \
  --task "Create a skill" \
  --cache-dir ".skill-cache/"
```

### 8. Domain-Specific Generation

```bash
# Coding skill with code examples
python3 scripts/generate_skill.py \
  --domain coding \
  --topic code-review \
  --description "Analyzes code diffs for bugs, security vulnerabilities, and code smells"

# Trading skill with risk constraints
python3 scripts/generate_skill.py \
  --domain trading \
  --topic risk-stop-loss \
  --description "Implements stop-loss strategies for position risk management"

# CNCF skill with YAML manifests
python3 scripts/generate_skill.py \
  --domain cncf \
  --topic prometheus \
  --description "Prometheus monitoring system for cloud-native environments"

# Agent skill with orchestration logic
python3 scripts/generate_skill.py \
  --domain agent \
  --topic task-router \
  --description "Routes tasks to appropriate agents based on confidence scores"

# Programming skill with algorithms
python3 scripts/generate_skill.py \
  --domain programming \
  --topic sorting-algorithms \
  --description "Reference guide for common sorting algorithms with Python implementation"
```

## Workflow Examples

### 9. Iterative Development Workflow

```bash
# Step 1: Dry run to test generation
python3 scripts/generate_skill.py --task "Create a code review skill" --dry-run

# Step 2: Review the generated content
# (Open the content in your editor)

# Step 3: Regenerate with improvements
python3 scripts/generate_skill.py --domain coding --topic code-review --contribute

# Step 4: Validate the skill
bash scripts/validate_skill.sh skills/coding/code-review/SKILL.md
```

### 10. Batch Generation

```bash
# Generate multiple skills in sequence
for skill in "code-review" "risk-stop-loss" "kubernetes-deployment"; do
    echo "Generating skill: $skill"
    python3 scripts/generate_skill.py \
        --task "Create a $skill skill" \
        --dry-run
done

# Generate skills with custom descriptions
python3 scripts/generate_skill.py \
    --domain coding \
    --topic my-skill \
    --description "Custom description for this skill" \
    --contribute
```

### 11. Integration with CI/CD

```bash
# CI/CD workflow example
python3 scripts/generate_skill.py \
    --task "${SKILL_TASK}" \
    --description "${SKILL_DESCRIPTION}" \
    --contribute
```

## Environment Variable Examples

### 12. Using Environment Variables

```bash
# Set required environment variables
export OPENAI_API_KEY="your-api-key-here"
export AUTO_SKILL_MODEL="gpt-4o-mini"
export AUTO_SKILL_TIMEOUT=60
export AUTO_SKILL_MAX_RETRIES=3
export AUTO_SKILL_CACHE_DIR=".skill-cache/"
export AUTO_SKILL_CONTRIBUTE=false

# Now run the script
python3 scripts/generate_skill.py --task "Create a skill"
```

### 13. Environment Variable in One Line

```bash
# Set and run in one command
OPENAI_API_KEY="your-api-key-here" \
AUTO_SKILL_MODEL="gpt-4o-mini" \
python3 scripts/generate_skill.py --task "Create a skill"
```

## Quality Control Examples

### 14. Validation Before Saving

```bash
# Dry run to validate
python3 scripts/generate_skill.py --task "Create a skill" --dry-run

# Check quality manually
bash scripts/validate_skill.sh skills/coding/my-skill/SKILL.md

# Check with LLM validation
bash scripts/validate_skill.sh --llm skills/coding/my-skill/SKILL.md
```

### 15. Quality Gate Checks

```bash
# Check file size (must be >= 3000 bytes)
wc -c skills/coding/my-skill/SKILL.md

# Check for sentinel string (must NOT contain it)
grep -q "Implementing this specific pattern or feature" skills/coding/my-skill/SKILL.md && echo "FAIL: sentinel found" || echo "PASS"

# Check code block count
grep -c '```' skills/coding/my-skill/SKILL.md

# Check trigger count
grep "triggers:" skills/coding/my-skill/SKILL.md
```

## Debugging Examples

### 16. Troubleshooting

```bash
# Check if OpenAI API key is set
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:+SET (hidden)}"
echo "AUTO_SKILL_MODEL: $AUTO_SKILL_MODEL"

# Increase verbosity
python3 scripts/generate_skill.py --task "Create a skill" --debug

# Use shorter timeout for faster failure
python3 scripts/generate_skill.py --task "Create a skill" --timeout 10
```

### 17. Fallback Options

```bash
# If LLM generation fails, try manual generation
# Create a minimal skill manually and enhance it

# Or use a simpler task
python3 scripts/generate_skill.py --task "Create a basic skill" --dry-run
```

## Performance Optimization Examples

### 18. Speed Optimization

```bash
# Use cheaper model
python3 scripts/generate_skill.py --task "Create a skill" --model gpt-4o-mini

# Reduce timeout for fast iteration
python3 scripts/generate_skill.py --task "Create a skill" --timeout 30

# Skip automation scripts for testing
python3 scripts/generate_skill.py --task "Create a skill" --dry-run
```

### 19. Cost Optimization

```bash
# Use dry run for testing
python3 scripts/generate_skill.py --task "Create a skill" --dry-run

# Use cheaper model
python3 scripts/generate_skill.py --task "Create a skill" --model gpt-4o-mini

# Reduce retries
python3 scripts/generate_skill.py --task "Create a skill" --max-retries 2
```

## Domain-Specific Examples

### 20. Coding Skills

```bash
# Security-focused code review
python3 scripts/generate_skill.py \
  --domain coding \
  --topic security-review \
  --description "Analyzes code for security vulnerabilities following OWASP guidelines" \
  --contribute

# Testing patterns
python3 scripts/generate_skill.py \
  --domain coding \
  --topic unit-testing \
  --description "Implements unit testing patterns with pytest and mocking" \
  --contribute

# Refactoring patterns
python3 scripts/generate_skill.py \
  --domain coding \
  --topic refactoring \
  --description "Applies refactoring patterns to improve code quality" \
  --contribute
```

### 21. Trading Skills

```bash
# Stop loss implementation
python3 scripts/generate_skill.py \
  --domain trading \
  --topic risk-stop-loss \
  --description "Implements stop-loss strategies for position risk management" \
  --contribute

# Position sizing
python3 scripts/generate_skill.py \
  --domain trading \
  --topic position-sizing \
  --description "Calculates optimal position sizes based on risk tolerance" \
  --contribute

# Risk management
python3 scripts/generate_skill.py \
  --domain trading \
  --topic risk-engine \
  --description "Builds a comprehensive risk management engine" \
  --contribute
```

### 22. CNCF Skills

```bash
# Kubernetes deployment
python3 scripts/generate_skill.py \
  --domain cncf \
  --topic kubernetes-deployment \
  --description "Creates Kubernetes deployment manifests with best practices" \
  --contribute

# Prometheus monitoring
python3 scripts/generate_skill.py \
  --domain cncf \
  --topic prometheus \
  --description "Prometheus monitoring system for cloud-native environments" \
  --contribute

# Helm charts
python3 scripts/generate_skill.py \
  --domain cncf \
  --topic helm-charts \
  --description "Creates Helm charts for Kubernetes applications" \
  --contribute
```

### 23. Agent Skills

```bash
# Task routing
python3 scripts/generate_skill.py \
  --domain agent \
  --topic task-router \
  --description "Routes tasks to appropriate agents based on confidence scores" \
  --contribute

# Parallel execution
python3 scripts/generate_skill.py \
  --domain agent \
  --topic parallel-execution \
  --description "Executes multiple tasks in parallel with proper coordination" \
  --contribute

# Dynamic replanning
python3 scripts/generate_skill.py \
  --domain agent \
  --topic dynamic-replanner \
  --description "Dynamically replans task execution based on changing conditions" \
  --contribute
```

### 24. Programming Skills

```bash
# Sorting algorithms
python3 scripts/generate_skill.py \
  --domain programming \
  --topic sorting-algorithms \
  --description "Reference guide for common sorting algorithms with Python implementation" \
  --contribute

# Graph algorithms
python3 scripts/generate_skill.py \
  --domain programming \
  --topic graph-algorithms \
  --description "Reference guide for graph traversal and pathfinding algorithms" \
  --contribute

# Dynamic programming
python3 scripts/generate_skill.py \
  --domain programming \
  --topic dynamic-programming \
  --description "Reference guide for dynamic programming patterns" \
  --contribute
```

## Complete Examples

### 25. Complete Trading Skill Generation

```bash
# Full workflow for trading skill
python3 scripts/generate_skill.py \
  --domain trading \
  --topic risk-stop-loss \
  --description "Implements stop-loss strategies (fixed percentage, ATR-based, trailing, support/resistance, volatility-adjusted) to limit position losses in algorithmic trading systems." \
  --contribute

# Expected output:
# - Saves to skills/trading/risk-stop-loss/SKILL.md
# - Runs reformat_skills.py
# - Runs enhance_triggers.py
# - Runs generate_index.py
# - Runs validate_skill.sh
```

### 26. Complete CNCF Skill Generation

```bash
# Full workflow for CNCF skill
python3 scripts/generate_skill.py \
  --domain cncf \
  --topic prometheus \
  --description "Prometheus architecture, PromQL patterns, alerting rules, ServiceMonitor configuration, and Kubernetes integration for cloud-native observability." \
  --contribute

# Expected output:
# - Saves to skills/cncf/prometheus/SKILL.md
# - Includes YAML manifests
# - Includes architecture diagrams
# - Includes common pitfalls
```

### 27. Complete Agent Skill Generation

```bash
# Full workflow for agent skill
python3 scripts/generate_skill.py \
  --domain agent \
  --topic confidence-based-selector \
  --description "Selects and executes the most appropriate skill based on confidence scores and relevance metrics, enabling intelligent skill routing for dynamic task resolution." \
  --contribute

# Expected output:
# - Saves to skills/agent/confidence-based-selector/SKILL.md
# - Includes ASCII flow diagram
# - References code-philosophy
# - Includes fallback/error routing
```

## Advanced Configuration Examples

### 28. Custom Script Integration

```bash
# Integrate with your own validation
python3 scripts/generate_skill.py \
  --task "Create a skill" \
  --contribute

# Then run custom validation
bash scripts/custom_validate.sh skills/coding/my-skill/SKILL.md
```

### 29. Post-Processing

```bash
# Generate skill
python3 scripts/generate_skill.py \
  --domain coding \
  --topic my-skill \
  --contribute

# Post-process with custom script
bash scripts/post_process.sh skills/coding/my-skill/SKILL.md

# Run additional automation
bash scripts/custom_automation.sh
```

### 30. Version Control Integration

```bash
# Generate skill
python3 scripts/generate_skill.py \
  --domain coding \
  --topic my-skill \
  --contribute

# Review changes
git diff

# Commit if satisfied
git add -A
git commit -m "feat: add my-skill skill"

# Push changes
git push
```

## Best Practices

### 31. Recommended Workflow

```bash
# 1. Test generation with dry run
python3 scripts/generate_skill.py --task "Create a skill" --dry-run

# 2. Review generated content
# (Open in editor and review)

# 3. Regenerate with improvements
python3 scripts/generate_skill.py --domain coding --topic my-skill --contribute

# 4. Validate the skill
bash scripts/validate_skill.sh skills/coding/my-skill/SKILL.md

# 5. Test with agent
# (Run agent with the new skill)

# 6. Commit changes
git add -A
git commit -m "feat: add my-skill skill"
```

### 32. Quality Assurance

```bash
# Before committing, run all checks
echo "=== Quality Checks ==="

echo "1. File size (must be >= 3000 bytes):"
wc -c skills/coding/my-skill/SKILL.md

echo "2. No sentinel string:"
grep -q "Implementing this specific pattern or feature" skills/coding/my-skill/SKILL.md && echo "FAIL: sentinel found" || echo "PASS"

echo "3. Code blocks (must be >= 2):"
grep -c '```' skills/coding/my-skill/SKILL.md

echo "4. Trigger count (must be 3-8):"
grep "triggers:" skills/coding/my-skill/SKILL.md

echo "5. YAML validation:"
python3 scripts/validate_skills.py

echo "=== All checks complete ==="
```

## Troubleshooting Examples

### 33. Common Issues

```bash
# Issue: LLM generation fails
# Solution: Increase timeout and retries
python3 scripts/generate_skill.py --task "Create a skill" --timeout 120 --max-retries 5

# Issue: Content is too short
# Solution: Use more capable model
python3 scripts/generate_skill.py --task "Create a skill" --model gpt-4o

# Issue: Missing code examples
# Solution: Add description with more detail
python3 scripts/generate_skill.py \
  --domain coding \
  --topic my-skill \
  --description "Includes comprehensive code examples with typed Python signatures and BAD/GOOD patterns" \
  --contribute
```

### 34. Debug Mode

```bash
# Run with verbose output
python3 scripts/generate_skill.py --task "Create a skill" --verbose

# Check environment variables
python3 -c "import os; print('OPENAI_API_KEY:', 'SET' if os.environ.get('OPENAI_API_KEY') else 'NOT SET')"
python3 -c "import os; print('AUTO_SKILL_MODEL:', os.environ.get('AUTO_SKILL_MODEL', 'gpt-4o-mini'))"
```

### 35. Fallback Generation

```bash
# If LLM generation fails, try manual generation
# Create a minimal skill manually

# Or use a simpler task
python3 scripts/generate_skill.py --task "Create a basic skill" --dry-run

# Or use a template from an existing skill
cp skills/coding/code-review/SKILL.md skills/coding/my-skill/SKILL.md
# Edit the copy
```

## See Also

- [generate_skill.py](generate_skill.py) - Main script
- [GENERATE_SKILL_README.md](GENERATE_SKILL_README.md) - Full documentation
- [PROMPT_TEMPLATES.md](PROMPT_TEMPLATES.md) - LLM prompt templates
- [SKILL_FORMAT_SPEC.md](../SKILL_FORMAT_SPEC.md) - Skill format specification
- [scripts/validate_skill.sh](../scripts/validate_skill.sh) - Quality validation
- [scripts/reformat_skills.py](../scripts/reformat_skills.py) - YAML reformatting
- [scripts/enhance_triggers.py](../scripts/enhance_triggers.py) - Trigger enhancement
- [scripts/generate_index.py](../scripts/generate_index.py) - Index generation
