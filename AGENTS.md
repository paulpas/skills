# Agents Guide — Adding New Skills

This guide explains how to create new skills for the agent-skill-router repository.

> **Quick Reference:** Skills are self-contained documentation files that provide specialized expertise to AI agents. Each skill lives in `skills/<domain>-<topic>/SKILL.md` and follows a strict format.

---

## Table of Contents

- [Overview](#overview)
- [Skill Repository Structure](#skill-repository-structure)
- [Domain Categories](#domain-categories)
- [Creating a New Skill](#creating-a-new-skill)
- [Frontmatter Requirements](#frontmatter-requirements)
- [Content Structure](#content-structure)
- [Naming Conventions](#naming-conventions)
- [Triggers Guidelines](#triggers-guidelines)
- [Workflow to Add a Skill](#workflow-to-add-a-skill)
- [Common Mistakes to Avoid](#common-mistakes-to-avoid)
- [Quality Checklist](#quality-checklist)
- [Related Documentation](#related-documentation)

---

## Overview

### What Skills Are

A **skill** is a self-contained Markdown document that injects specialized behavior, knowledge, and constraints into an OpenCode AI agent session. When loaded, the skill's full content becomes part of the model's active context, shaping how it responds to the current task.

Skills enable auto-routing: when the skill-router detects trigger keywords in conversation, the appropriate skill is automatically loaded and injected into context — no manual `/skill` commands required.

### How Skills Are Used

OpenCode loads skills in two ways:

| Loading Mode | Mechanism | When It Fires |
|---|---|---|
| **Manual** | User runs `/skill <name>` | Explicitly requested |
| **Auto-load** | `metadata.triggers` keyword match | Detected in conversation context |

**Auto-loading flow:**

```
User message contains trigger keyword
        ↓
OpenCode scans metadata.triggers fields of all installed skills
        ↓
Match found → skill content injected into context
        ↓
Model reads skill and applies its constraints
```

---

## Skill Repository Structure

```
skills/
├── agent-*/          ← Agent orchestration, routing, analysis skills
├── cncf-*/           ← CNCF cloud-native project reference skills
├── coding-*/         ← Software engineering patterns skills
├── trading-*/        ← Algorithmic trading implementation skills
└── programming-*/    ← CS fundamentals, algorithms reference skills
    └── <skill-name>/
        ├── SKILL.md          ← Required: skill documentation
        ├── references/       ← Optional: referenced sub-documents
        └── scripts/          ← Optional: helper scripts
```

**Current Statistics:**
- **266 skills** across 5 domains
- **5 domain categories**: agent, cncf, coding, trading, programming

---

## Domain Categories

Each domain has a prefix and default metadata values:

| Domain Prefix | Category | Default Role | Default Scope | Default Output Format |
|---|---|---|---|---|
| `agent-` | AI agent orchestration patterns | `orchestration` | `orchestration` | `analysis` |
| `cncf-` | CNCF cloud-native projects | `reference` | `infrastructure` | `manifests` |
| `coding-` | Software engineering patterns | `implementation` | `implementation` | `code` |
| `trading-` | Algorithmic trading implementation | `implementation` | `implementation` | `code` |
| `programming-` | CS fundamentals, algorithms | `reference` | `implementation` | `code` |

**Note:** These defaults can be overridden for specific skills that don't fit the typical pattern.

---

## Creating a New Skill

### Step 1: Create the Directory

Create a new directory under `skills/` using kebab-case naming:

```
skills/<domain>-<topic>/
```

Examples:
- `skills/trading-risk-stop-loss/`
- `skills/coding-code-review/`
- `skills/agent-task-decomposition-engine/`
- `skills/cncf-prometheus/`

### Step 2: Create SKILL.md

Inside the new directory, create `SKILL.md` with the required YAML frontmatter and content sections.

---

## Frontmatter Requirements

Every `SKILL.md` must begin with a YAML frontmatter block delimited by `---`.

### Required Fields

| Field | Type | Rules |
|---|---|---|
| `name` | string | Must exactly match the directory name in kebab-case |
| `description` | string | Single line. State what the skill does, not what it is about. Use an active verb. Max ~200 characters. |

**Description Writing Rules:**
- State *what the skill makes the model do*
- Lead with an active verb: `Implements…`, `Selects…`, `Analyzes…`, `Detects…`
- Include 1–2 key domain terms that distinguish this skill from similar ones
- Examples:
  ```yaml
  # ❌ BAD — too vague
  description: Stop loss for trading
  
  # ❌ BAD — describes the topic instead of the skill's action
  description: Information about Prometheus monitoring
  
  # ✅ GOOD — specific action + domain context
  description: Implements stop-loss strategies (fixed percentage, ATR-based, trailing, volatility-adjusted) for position risk management in algorithmic trading systems
  ```

### Recommended Fields

| Field | Value | Purpose |
|---|---|---|
| `license` | `MIT` | Signals the skill is freely redistributable |
| `compatibility` | `opencode` | Confirms this skill follows OpenCode format conventions |

### The `metadata` Block

The `metadata` block enables auto-loading, categorization, and skill discovery.

| Field | Type | Values / Rules |
|---|---|---|
| `metadata.version` | string | Semantic version: `"1.0.0"` |
| `metadata.domain` | string | One of: `agent`, `cncf`, `coding`, `trading`, `programming` |
| `metadata.role` | string | One of: `implementation`, `reference`, `orchestration`, `review` |
| `metadata.scope` | string | One of: `implementation`, `infrastructure`, `orchestration`, `review` |
| `metadata.output-format` | string | One of: `code`, `manifests`, `analysis`, `report` |
| `metadata.triggers` | string | Comma-separated keywords (3–8 terms). **Drives auto-loading.** |
| `metadata.related-skills` | string | Comma-separated skill names (e.g. `trading-risk-kill-switches`) |
| `metadata.author` | string | GitHub URL — **only for externally-sourced skills** |
| `metadata.source` | string | Source repo URL — **only for externally-sourced skills** |

---

## Content Structure

### Minimum Required Sections

Every skill must have these four elements:

1. **H1 Title** — Human-readable name (not the kebab-case identifier)
2. **Role/purpose paragraph** — 1–3 sentences explaining what this skill makes the model do
3. **When to Use** — Bulleted list of situations where this skill applies
4. **Core Workflow or Constraints** — The primary instructions the model must follow

### Recommended Full Structure

Use this template as a starting point:

```markdown
# Skill Title (Human-Readable)

Brief role description — 1–3 sentences. What does loading this skill make the model do?

## TL;DR Checklist

- [ ] Step or check 1
- [ ] Step or check 2
- [ ] Step or check 3

---

## When to Use

Use this skill when:

- Concrete situation 1
- Concrete situation 2
- Concrete situation 3

---

## When NOT to Use

Avoid this skill for:

- Anti-pattern 1 (use X instead)
- Anti-pattern 2
- Situation where overhead outweighs benefit

---

## Core Workflow

1. **Step name** — Description. **Checkpoint:** What to verify before proceeding.
2. **Step name** — Description.
3. **Step name** — Description.

---

## Implementation Patterns / Reference Guide

### Pattern 1: Pattern Name

Brief description.

```python
# Good example
```

### Pattern 2: Pattern Name

Brief description.

```python
# ❌ BAD — reason
bad_code_here()

# ✅ GOOD — reason  
good_code_here()
```

---

## Constraints

### MUST DO
- Constraint 1
- Constraint 2

### MUST NOT DO
- Anti-pattern 1
- Anti-pattern 2

---

## Output Template

Describe what the model's output must contain when this skill is active.

1. **Section 1** — Description
2. **Section 2** — Description

---

## Related Skills

| Skill | Purpose |
|---|---|
| `skill-name` | Why you'd use this instead or alongside |
| `skill-name` | Complementary capability |
```

---

## Naming Conventions

### Directory Names

**Must be kebab-case:** lowercase with hyphens between words.

| Valid | Invalid |
|---|---|
| `trading-risk-stop-loss` | `TradingRiskStopLoss` |
| `cncf-prometheus` | `cncf_prometheus` |
| `coding-code-review` | `coding_codeReview` |
| `agent-confidence-based-selector` | `agentConfidenceSelector` |

### Frontmatter `name` Field

The `name` field in frontmatter **must exactly match** the directory name.

```yaml
# Directory: skills/trading-risk-stop-loss/
---
name: trading-risk-stop-loss  # ✅ Must match directory name
# ❌ name: trading_risk_stop_loss  (wrong format)
# ❌ name: trading-risk-stopLoss  (wrong case)
---
```

### H1 Title

Use a human-readable title, not the kebab-case name.

```markdown
# ✅ Stop Loss Manager
# ✅ Confidence-Based Selector (Agent Skill Selection)
# ✅ Prometheus in Cloud-Native Engineering

# ❌ trading-risk-stop-loss
# ❌ agent-confidence-based-selector
```

---

## Triggers Guidelines

### What Triggers Do

The `metadata.triggers` field contains comma-separated keywords that OpenCode matches against the active conversation. When a match is found, the skill is automatically injected into context — no `/skill` command required.

**Auto-loading is the primary way skills get used.** A skill with no triggers relies entirely on users knowing to load it manually.

### Rules for Good Triggers

| Rule | Explanation |
|---|---|
| **3–8 terms** | Fewer than 3 is too narrow. More than 8 dilutes signal and causes false positives. |
| **Include the core topic name** | Always include the primary name: `prometheus`, `stop loss`, `code review` |
| **Include abbreviations** | `ATR`, `PromQL`, `VWAP`, `TDD` — models use these in conversation |
| **Include hyphenated variants** | `stop-loss` alongside `stop loss` |
| **Include common adjacent terms** | What words appear in conversation when someone needs this skill? |
| **Avoid ultra-generic terms** | `risk`, `code`, `data` will trigger on nearly everything |

### Good vs Bad Trigger Examples

#### `trading-risk-stop-loss`

```yaml
# ✅ GOOD
triggers: stop loss, trailing stop, ATR stop, stop placement, position protection, emergency stop, stop-loss

# ❌ TOO BROAD — will fire on nearly any trading conversation
triggers: risk, trading, loss, price

# ❌ TOO NARROW — misses most natural phrasings
triggers: StopLossManager
```

#### `cncf-prometheus`

```yaml
# ✅ GOOD
triggers: prometheus, promql, alerting rules, metrics scraping, kube-state-metrics, servicemonitor, time-series database

# ❌ TOO BROAD — fires whenever anyone mentions monitoring anything
triggers: monitoring, metrics, alerts, kubernetes

# ❌ MISSES ABBREVIATIONS — PromQL is very common in conversation
triggers: prometheus, prometheus operator, alertmanager
```

#### `coding-code-review`

```yaml
# ✅ GOOD
triggers: code review, pull request, PR review, code quality, security audit, OWASP, architectural review

# ❌ TOO BROAD — fires on any coding conversation
triggers: code, review, bugs, security

# ❌ MISSES NATURAL PHRASING — "review this PR" would not match
triggers: code-review, code_review
```

### Trigger Calibration Heuristic

Ask these questions for each trigger candidate:

1. **If someone says this word/phrase, would they plausibly need this skill?** → Include it
2. **Is this word used heavily in other unrelated contexts?** → Exclude or be more specific
3. **Is this a natural abbreviation or shorthand for the topic?** → Include it
4. **Is this only used internally (class name, file name)?** → Exclude it

---

## Workflow to Add a Skill

1. **Create directory**: `skills/<name>/`

2. **Create SKILL.md**: Write YAML frontmatter + content

3. **Run reformat script**: `python3 reformat_skills.py`
   - This fills in any missing frontmatter fields from templates
   - Validates format compliance

4. **Update index**: `python3 generate_index.py`
   - This regenerates `skills-index.json` with the new skill
   - The skill-router reads this file for routing decisions
   - Without this step, the new skill won't be routable

5. **Commit and push**:
   ```bash
   git add -A
   git commit -m "feat: add <name> skill"
   git push
   ```

6. **Verify auto-discovery** (takes up to 1 hour by default):
   - The skill-router automatically fetches updated `skills-index.json` every `SKILL_SYNC_INTERVAL` seconds (default: 1 hour)
   - For immediate pickup: `curl -X POST http://localhost:3000/reload`

---

## Common Mistakes to Avoid

| Mistake | Problem | Fix |
|---|---|---|
| Directory name uses underscores | Skill may not be found | Use kebab-case: `trading-risk-stop-loss`, not `trading_risk_stop_loss` |
| `name` in frontmatter doesn't match directory | Validation fails | Make them exactly match (case-sensitive) |
| Missing `triggers` field | Skill never auto-loads | Add 3–8 specific keywords |
| Generic triggers (`code`, `data`, `risk`) | Fires on nearly everything | Use domain-specific phrases |
| Skipping `generate_index.py` | Skill not routable | Always run this after adding a skill |
| H1 title equals kebab-case name | Unreadable | Use human-readable title |
| Missing "When NOT to Use" section | Model applies skill inappropriately | Always include exclusion cases for complex skills |
| Code without typing | Ambiguous signatures | Add Python type hints and docstrings |
| Links to placeholder URLs | Broken references | Use real URLs or omit the link |

---

## Quality Checklist

Use this checklist when writing a new skill or auditing an existing one.

### Frontmatter

- [ ] `name` exactly matches the directory name (kebab-case)
- [ ] `description` clearly states what the skill makes the model do in one sentence
- [ ] `description` leads with an active verb and includes 1–2 domain-specific terms
- [ ] `license: MIT` is present
- [ ] `compatibility: opencode` is present
- [ ] `metadata.version` is present (format: `"1.0.0"`)
- [ ] `metadata.domain` matches the directory name prefix
- [ ] `metadata.triggers` is set with 3–8 meaningful, specific terms
- [ ] `metadata.role` is set to one of: `implementation`, `reference`, `orchestration`, `review`
- [ ] `metadata.scope` is set to one of: `implementation`, `infrastructure`, `orchestration`, `review`
- [ ] `metadata.output-format` is set to one of: `code`, `manifests`, `analysis`, `report`
- [ ] `metadata.related-skills` lists adjacent skills (if any exist)
- [ ] `metadata.author` and `metadata.source` are present **only** if externally sourced

### Content

- [ ] H1 title is present and human-readable (not the kebab-case name)
- [ ] Role/purpose paragraph is present (1–3 sentences, model-perspective)
- [ ] "When to Use" section is present with specific, concrete bullet points
- [ ] "When NOT to Use" section is present (for complex skills)
- [ ] Core Workflow or Constraints section is present
- [ ] Code examples are present if `role = implementation` or `role = review`
- [ ] At least one BAD vs. GOOD example pair if `domain = coding` or `domain = trading`
- [ ] Output Template is present if `role = review`
- [ ] Related Skills table is present if `metadata.related-skills` is non-empty
- [ ] No debug statements or placeholder text (e.g. "TODO", "FIXME", "example.com" links)
- [ ] External links point to real, stable URLs (not placeholder `example.com`)

### Domain-Specific

**For `agent-*`:**
- [ ] Orchestration flow diagram (ASCII) is present
- [ ] Fallback/error routing is explicitly described
- [ ] References `code-philosophy` (5 Laws of Elegant Defense)

**For `cncf-*`:**
- [ ] Purpose and Use Cases section present
- [ ] Architecture Design Patterns section present
- [ ] Integration Approaches section present
- [ ] Common Pitfalls section present
- [ ] At least one complete working YAML manifest example

**For `coding-*`:**
- [ ] At least one BAD/GOOD code example pair
- [ ] References a relevant standard (OWASP, SOLID, DRY, etc.)
- [ ] MUST DO / MUST NOT DO constraints present

**For `trading-*`:**
- [ ] Python implementation with typed signatures
- [ ] Risk constraints explicitly stated
- [ ] File path conventions follow APEX platform layout

---

## Related Documentation

- [SKILL_FORMAT_SPEC.md](./SKILL_FORMAT_SPEC.md) — Complete format specification with examples
- [README.md](./README.md) — Quick start and overview
- [agent-skill-routing-system/README.md](./agent-skill-routing-system/README.md) — Complete router documentation

---

## Examples

### Simple Skill Template

```markdown
---
name: trading-risk-stop-loss
description: Implements stop-loss strategies (fixed percentage, ATR-based, trailing, support/resistance, volatility-adjusted) to limit position losses in algorithmic trading systems.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: trading
  triggers: stop loss, trailing stop, ATR stop, stop placement, position protection, emergency stop, stop-loss
  role: implementation
  scope: implementation
  output-format: code
  related-skills: trading-risk-position-sizing, trading-risk-kill-switches
---

# Stop Loss Manager

Implements stop loss mechanisms to limit losses and protect capital.

## When to Use

- Implementing position risk controls for any long or short position
- Designing or reviewing a stop loss strategy for a new trading algorithm
- Choosing between stop types for a specific market condition

## Core Workflow

1. **Assess Market Regime** — Determine if market is trending, ranging, or high-volatility.
2. **Select Stop Type** — Choose the appropriate stop strategy for the regime.
3. **Calculate Stop Level** — Apply the selected formula.

## Implementation Patterns

### Pattern 1: ATR-Based Stop

```python
def atr_stop(current_price: float, atr: float, multiplier: float = 2.0) -> float:
    """Calculate ATR-based stop loss level."""
    return current_price - (atr * multiplier)
```

## Constraints

### MUST DO
- Layer an emergency stop on top of every other stop type
- Base trailing stop distance on ATR, not a fixed price

### MUST NOT DO
- Use stop type as the only risk control layer
- Disable or bypass stops "temporarily"
```

---

*This guide applies to all skills in the agent-skill-router repository. When in doubt, favor specificity over brevity — skills read by LLMs benefit from explicit, concrete guidance.*
