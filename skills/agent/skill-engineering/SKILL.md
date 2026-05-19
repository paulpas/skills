---
name: skill-engineering
description: Engineers production-ready AI skills following framework standards, including YAML frontmatter, trigger design, workflow structuring, and stub prevention for reliable agent routing.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: agent
  triggers: skill design, skill creation, AI skill, framework standards, trigger engineering, workflow pattern, agent configuration, skill routing
  role: implementation
  scope: infrastructure
  output-format: code
  content-types: [guidance, examples, do-dont, config]
  related-skills: confidence-based-selector, task-routing-engine, dependency-graph-builder
---

# AI Skill Engineering Framework

Applies structured engineering discipline to create and validate SKILL.md files for the agent-skill-router platform. Enforces stub prevention through content depth audits, designs effective two-tier trigger sets (technical + conversational), and structures workflows with explicit checkpoints so every produced skill routes reliably and produces actionable model behavior.

## TL;DR Checklist

- [ ] Validate `name` matches directory kebab-case exactly
- [ ] Confirm `description` starts with an active verb and includes 1–2 domain-specific terms
- [ ] Verify triggers include both technical terms AND conversational variants (two-tier)
- [ ] Check file size ≥ 3,000 bytes of actual content
- [ ] Ensure Core Workflow has numbered steps with **Checkpoint** annotations
- [ ] Run `validate_skill.sh` before committing — zero tolerance for stub sentinels

---

## When to Use

Use this skill when:

- You are creating a new SKILL.md from scratch and need the full engineering workflow
- A reviewer flagged an existing skill as "too thin," generic, or stub-like
- You are redesigning trigger sets that fire on irrelevant conversations
- You need to audit a skill's content depth against the zero-tolerance stub policy
- You are refactoring a skill with missing sections (When NOT to Use, Constraints, etc.)
- You want to batch-validate multiple skills using the provided validation patterns

---

## When NOT to Use

Avoid this skill for:

- Writing application logic that is unrelated to skill authoring (use `coding/*` instead)
- Simple documentation updates that do not change skill structure or behavior
- Uncommitted prototypes you intend to rewrite from scratch — write them directly into the final format
- Reviewing non-agent, non-infrastructure code (load the appropriate domain-specific review skill)

---

## Core Workflow

```
User Request: "I need to create/fix a skill"
      ↓
┌─────────────────────────────────────────┐
│ Step 1: Define Scope & Domain           │
│   - Identify target domain              │
│   - Determine role/scope/output-format  │
│   - Check existing related skills       │
│   **Checkpoint:** Domain confirmed,     │
│     no conflicting skill exists         │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Step 2: Draft Frontmatter               │
│   - Write kebab-case name matching dir  │
│   - Craft active-verb description       │
│   - Design two-tier trigger set         │
│   - Set metadata per domain defaults    │
│   **Checkpoint:** YAML parses cleanly,  │
│     all required fields present         │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Step 3: Structure Content               │
│   - Write H1 title (human-readable)     │
│   - Draft role/purpose paragraph        │
│   - Populate When to Use / NOT to Use   │
│   - Add ASCII flow diagram (agent only) │
│   **Checkpoint:** All four minimum      │
│     required sections present           │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Step 4: Implement Patterns              │
│   - Write domain-specific workflow      │
│     steps with checkpoints              │
│   - Include BAD vs. GOOD code/config    │
│     examples                            │
│   - Add MUST DO / MUST NOT DO rules     │
│   **Checkpoint:** ≥2 real code blocks,  │
│     no generic "identify → apply" flow  │
└───────────────┬─────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│ Step 5: Validate & Test                 │
│   - Run `validate_skill.sh`             │
│   - Check file size ≥ 3,000 bytes       │
│   - Verify no stub sentinels            │
│   - Confirm reciprocal related-skills   │
│   **Checkpoint:** Validation exit code  │
│     = 0 (PASS), README regenerated      │
└─────────────────────────────────────────┘
                ↓
         Skill ready to commit
```

Apply the 5 Laws of Elegant Defense throughout this workflow: guide data naturally through each pipeline stage, parse inputs at boundaries, fail fast on invalid frontmatter or trigger sets, and return validated skill structures without mutating partial drafts.

1. **Define Scope & Domain** — Identify the target domain (`agent`, `cncf`, `coding`, `go`, `linux`, `trading`, `programming`, `writing`). Determine role, scope, output-format, and content-types using the [Domain Defaults Table](#domain-defaults). Check existing skills to avoid overlap.
   **Checkpoint:** Confirm no existing skill in the same domain covers this exact topic with overlapping triggers.

2. **Draft Frontmatter** — Write kebab-case `name` matching the directory. Craft a single-line `description` starting with an active verb and including 1–2 domain-specific terms. Design trigger set following two-tier strategy (technical + conversational). Set all metadata fields per domain defaults.
   **Checkpoint:** Validate YAML parses without errors — use `python3 -c "import yaml; yaml.safe_load(open('SKILL.md'))"`. All required frontmatter fields present.

3. **Structure Content** — Write an H1 title that is human-readable (not the kebab-case name). Draft the role/purpose paragraph in 1–3 sentences from the model's perspective. Populate "When to Use" with at least 4 concrete bullets and "When NOT to Use" with explicit exclusion cases referencing related skills by name.
   **Checkpoint:** All four minimum required sections present (H1, role paragraph, When to Use, Core Workflow or Constraints).

4. **Implement Patterns** — Write domain-specific workflow steps with numbered order and **Checkpoint** annotations after steps requiring verification. Include at least two real code/config example blocks. Add BAD vs. GOOD pairs where the domain requires it (coding, trading, go, linux). Write specific MUST DO / MUST NOT DO rules that reference actual framework requirements, not generic "follow best practices."
   **Checkpoint:** File is ≥ 3,000 bytes. Core Workflow has at least 4 steps with checkpoints. No generic "identify → apply → validate" sequences. Stub sentinel string absent.

5. **Validate & Test** — Run the validation script against the skill file. Check size, check for stub sentinels, verify trigger quality (3–8 terms, mix of technical and conversational). Confirm reciprocal related-skills entries exist. Regenerate README catalog.
   **Checkpoint:** `validate_skill.sh` returns exit code 0. `wc -c` confirms ≥ 3,000 bytes. Related skills list this skill in their own `related-skills`.

---

## Implementation Patterns / Reference Guide

### Pattern 1: Two-Tier Trigger Design

Effective triggers combine technical precision (Tier 1) with conversational accessibility (Tier 2). Always include the primary topic name, its abbreviation if applicable, at least one "how do I..." variant, and operational task phrases.

```yaml
# ❌ BAD — only technical terms, misses natural user language
triggers: skill-design, skill-creation, yaml-frontmatter

# ❌ BAD — ultra-generic, fires on nearly everything
triggers: agent, code, routing, design

# ❌ GOOD — two-tier strategy for a trading skill
triggers: stop loss, trailing stop, ATR stop, how do i limit losses, position protection, stop placement, emergency stop, stop-loss

# ❌ GOOD — two-tier strategy for a CNCF skill
triggers: prometheus, promql, time-series database, how do i monitor systems, metrics scraping, kube-state-metrics, grafana

# ✅ GOOD — two-tier strategy for this skill-engineering skill
triggers: skill design, skill creation, AI skill, framework standards, trigger engineering, workflow pattern, agent configuration, skill routing
```

**Two-Tier Design Checklist:**

| Tier | What to Include | Example Triggers |
|------|-----------------|------------------|
| **Tier 1: Technical** | Domain terms, abbreviations, product names, API names | `promql`, `ATR stop`, `goroutine pool` |
| **Tier 2: Conversational** | "how do I..." questions, operational tasks, business language | `how do i monitor systems`, `scaling apps` |

**Calibration Heuristic:** For each trigger candidate, ask: "If someone said this exact phrase in conversation, would they need this skill?" If yes → include. If the word is used heavily in unrelated contexts → exclude or be more specific.

---

### Pattern 2: Workflow Checkpoint Structuring

Every workflow step should either stand alone with a clear action or end with a **Checkpoint** that tells the model what to verify before proceeding. This prevents the model from skipping critical validation steps.

```markdown
# ❌ BAD — generic sequence, no checkpoints
1. Identify use case → apply pattern → validate
2. Write code following best practices
3. Test and fix any issues

# ✅ GOOD — specific steps with verification gates
1. **Assess Market Regime** — Determine if market is trending, ranging, or high-volatility using ATR(14).
   **Checkpoint:** ATR value must be calculated before choosing stop type.

2. **Select Stop Type** — Map regime to appropriate strategy:
   - Trending → trailing stop or ATR-based stop
   - Ranging → support/resistance-based stop
   - All regimes → layer emergency stop independently
   
   **Checkpoint:** Confirm at least two stop layers are configured before proceeding.

3. **Calculate Stop Level** — Apply formula from the selected pattern.
   **Checkpoint:** Verify calculated stop is beyond obvious round-number levels to avoid stop hunting.

4. **Place and Monitor** — Submit order or register with manager, track highest/lowest price.
```

**Checkpoint Patterns:**

| Situation | Checkpoint Format | Example |
|-----------|-------------------|---------|
| Prerequisite computation | "X must be calculated before Y" | `ATR value must be calculated before choosing stop type` |
| Layering requirement | "Confirm at least N layers configured" | `Confirm at least two stop layers are configured` |
| Boundary validation | "Verify X is beyond/below/above Y" | `Verify calculated stop is below entry price` |
| Completeness gate | "Check that all N items present" | `Check that all required sections are in frontmatter` |

---

### Pattern 3: Stub Prevention Validation

Stub detection operates on five concrete signals. Run this audit checklist before every commit:

```python
#!/usr/bin/env python3
"""Stub prevention validator for SKILL.md files."""
import os
import re
import sys


def validate_skill_file(path: str) -> dict:
    """Run all stub prevention checks on a SKILL.md file.
    
    Returns validation report with pass/fail for each check.
    """
    content = _read_file(path)
    frontmatter = _parse_frontmatter(content)
    
    report = {
        "path": path,
        "checks": [],
        "passed": True,
    }
    
    # Check 1: Size >= 3000 bytes (excluding frontmatter)
    body = content.split("---", 2)[-1] if "---" in content else content
    size_ok = len(body.encode("utf-8")) >= 3000
    report["checks"].append({
        "name": "content-size",
        "passed": size_ok,
        "detail": f"{len(body.encode('utf-8'))} bytes (minimum: 3000)",
    })
    if not size_ok:
        report["passed"] = False
    
    # Check 2: No stub sentinel
    # Check for stub sentinel using regex to avoid literal phrase matching
    stub_pattern = r"[Ii]mplementing\s+this\s+specific\s+pattern\.*"
    has_sentinel = bool(re.search(stub_pattern, body))
    sentinel_ok = not has_sentinel
    report["checks"].append({
        "name": "no-stub-sentinel",
        "passed": sentinel_ok,
        "detail": f"Stub sentinel {'found' if has_sentinel else 'absent'}",
    })
    if not sentinel_ok:
        report["passed"] = False
    
    # Check 3: At least 2 code blocks with real implementations
    code_blocks = re.findall(r"```(?:\w+)?\n(.*?)\n```", body, re.DOTALL)
    non_empty_blocks = [b for b in code_blocks if b.strip() and not _is_placeholder(b)]
    blocks_ok = len(non_empty_blocks) >= 2
    report["checks"].append({
        "name": "code-blocks-count",
        "passed": blocks_ok,
        "detail": f"{len(non_empty_blocks)} real code blocks (minimum: 2)",
    })
    if not blocks_ok:
        report["passed"] = False
    
    # Check 4: Triggers quality (3-8 specific terms)
    triggers_text = frontmatter.get("metadata", {}).get("triggers", "")
    trigger_terms = [t.strip() for t in triggers_text.split(",") if t.strip()]
    has_generic = any(t.lower() in ("code", "data", "risk", "pattern", "system") for t in trigger_terms)
    trigger_ok = 3 <= len(trigger_terms) <= 8 and not has_generic
    report["checks"].append({
        "name": "trigger-quality",
        "passed": trigger_ok,
        "detail": f"{len(trigger_terms)} triggers, {'contains generic terms' if has_generic else 'no generics'}",
    })
    if not trigger_ok:
        report["passed"] = False
    
    # Check 5: Core Workflow has specific steps (not generic)
    workflow_section = _extract_section(body, "## Core Workflow")
    has_specific_steps = bool(re.search(r"\*\*(?:[A-Z][a-z]+(?:\s+[a-z]+){2,})\*\*", workflow_section)) if workflow_section else False
    has_generic_sequence = re.search(r"identify.*apply.*validate|analyze.*implement.*test", workflow_section) if workflow_section else None
    steps_ok = has_specific_steps and not has_generic_sequence
    report["checks"].append({
        "name": "workflow-specificity",
        "passed": steps_ok,
        "detail": f"Specific step names {'found' if has_specific_steps else 'missing'}, generic sequence {'found' if has_generic_sequence else 'absent'}",
    })
    if not steps_ok:
        report["passed"] = False
    
    return report


def _read_file(path: str) -> str:
    with open(path, "r") as f:
        return f.read()


def _parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from SKILL.md content."""
    try:
        import yaml
        parts = content.split("---")
        if len(parts) >= 3:
            return yaml.safe_load(parts[1]) or {}
    except Exception:
        pass
    return {}


def _is_placeholder(block: str) -> bool:
    """Return True if a code block is placeholder/stub content."""
    stripped = block.strip()
    stub_patterns = [
        r"\bpass\b",
        r"return\s+\{\}",
        r"TODO.*example",
        r"PLACEHOLDER",
        r"#\s*\.\.\.",
    ]
    for pattern in stub_patterns:
        if re.search(pattern, stripped):
            return True
    return False


def _extract_section(body: str, section_header: str) -> str:
    """Extract markdown content under a given ## header."""
    pattern = rf"(?m)^## {re.escape(section_header)}\s*\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, body)
    return match.group(1).strip() if match else ""


# CLI entry point
if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "SKILL.md"
    result = validate_skill_file(path)
    
    for check in result["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"  [{status}] {check['name']}: {check['detail']}")
    
    overall = "✅ ALL CHECKS PASSED" if result["passed"] else "❌ VALIDATION FAILED"
    print(f"\n{overall}")
    sys.exit(0 if result["passed"] else 1)
```

**Quick CLI Validation:**

```bash
# Static checks (recommended for every commit)
./scripts/validate_skill.sh skills/agent/skill-engineering/SKILL.md

# Static + LLM quality check (optional, deeper analysis)
./scripts/validate_skill.sh --llm skills/agent/skill-engineering/SKILL.md

# File size check
wc -c skills/agent/skill-engineering/SKILL.md

# Stub sentinel sweep (uses regex to avoid literal match on own file)
grep -rnP "[Ii]mplementing\s+this\s+specific\s+pattern\.*" skills/*/SKILL.md
```

---

### Pattern 4: Domain Default Compliance

Each domain has default `role`, `scope`, `output-format`, and `content-types`. Override only when the skill's actual purpose differs. This table is your reference for correctness validation:

| Domain | Default Role | Default Scope | Default Output Format | Default Content Types |
|--------|-------------|---------------|----------------------|-----------------------|
| `agent` | `orchestration` | `orchestration` | `analysis` | `guidance, examples, do-dont` |
| `cncf` | `reference` | `infrastructure` | `manifests` | `guidance, examples, do-dont, config` |
| `coding` | `implementation` | `implementation` | `code` | `code, guidance, do-dont, examples` |
| `go` | `implementation` | `implementation` | `code` | `code, guidance, do-dont, examples` |
| `linux` | `implementation` | `implementation` | `code` | `code, guidance, config, do-dont` |
| `trading` | `implementation` | `implementation` | `code` | `code, guidance, config, do-dont` |
| `programming` | `reference` | `implementation` | `code` | `code, guidance, examples, diagrams` |
| `writing` | `reference` | `implementation` | `guidance` | `guidance, examples, do-dont` |

```yaml
# ✅ GOOD — overrides with justification (trading skill producing analysis reports)
metadata:
  role: reference
  scope: implementation
  output-format: analysis
  content-types: [code, guidance, config, do-dont]

# ❌ BAD — mismatched domain defaults without reason
metadata:
  domain: cncf
  role: implementation          # CNCF defaults to reference
  scope: orchestration         # CNCF defaults to infrastructure
  output-format: code          # CNCF defaults to manifests
```

---

## Constraints

### MUST DO
- Enforce kebab-case naming for both directory name and frontmatter `name` field (they must match exactly)
- Use active-verb descriptions that state what the skill makes the model do, not what it is about (e.g., "Implements…", "Selects…", "Analyzes…")
- Design trigger sets with 5–8 terms following the two-tier strategy: technical terms plus conversational variants
- Include **Checkpoint** annotations in at least every other Core Workflow step
- Provide ≥2 real, non-placeholder code or config example blocks (for implementation-role skills)
- Include BAD vs. GOOD example pairs for `coding`, `trading`, `go`, and `linux` domain skills
- Ensure `content-types` matches the array format `[guidance, examples, do-dont]` — never a comma-separated string
- Validate file size ≥ 3,000 bytes of actual content (body, excluding frontmatter) before committing
- Run `validate_skill.sh` and confirm exit code 0 with no stub sentinels
- Add reciprocal `related-skills` entries: if A lists B, then B must list A
- For agent skills: include an ASCII orchestration flow diagram and explicit fallback/error routing paths
- Reference `code-philosophy` (5 Laws of Elegant Defense) in workflow or constraints for agent skills

### MUST NOT DO
- Use generic workflow steps like "identify use case → apply pattern → validate" — every step must be domain-specific with named actions
- Trigger on ultra-generic words alone: `code`, `data`, `risk`, `pattern`, `system` — these fire on nearly every conversation
- Commit unvalidated skills — always run the validation pipeline first
- Create skills under 3,000 bytes or containing stub sentinels — zero tolerance enforcement
- Use fixed confidence thresholds without adaptive tuning in agent skills — make them configurable
- Leave orphaned related-skills references — if you list a skill as related, that skill must reference this one back
- Apply `role: implementation` to skills that produce no code or configuration examples
- Include placeholder URLs (`example.com`) or TODO/FIXME markers in committed content
- Ignore domain-specific requirements (e.g., missing YAML manifests for CNCF, missing typed Python signatures for trading)

---

## Output Template

When applying this skill, produce a complete SKILL.md draft containing every section below. The output must be ready for validation without further structural edits.

1. **YAML Frontmatter Block** — All required fields (`name`, `description`) and recommended fields (`license`, `compatibility`). Complete metadata block with version, domain, triggers (3–8 terms), role, scope, output-format, content-types array, and related-skills list.

2. **H1 Title** — Human-readable skill title in sentence case, not the kebab-case directory name.

3. **Role/Purpose Paragraph** — 1–3 sentences from the model's perspective describing what behavior this skill injects into an agent session.

4. **TL;DR Checklist** — 5–6 checkbox items that the model uses as a quick verification pass. Each item must be a concrete action, not a topic name.

5. **When to Use Section** — At least 4 specific bullet points describing real situations where this skill should load.

6. **When NOT to Use Section** — Explicit exclusion cases referencing other skills by `related-skills` name or domain prefix.

7. **Core Workflow** — Numbered steps (minimum 5) with bold step names and **Checkpoint** annotations at verification gates. Include an ASCII orchestration flow diagram for agent-domain skills.

8. **Implementation Patterns / Reference Guide** — At least 2 numbered patterns with code/config examples, including BAD vs. GOOD pairs where the domain mandates them.

9. **Constraints** — Imperative MUST DO and MUST NOT DO rules that are specific to the domain and framework requirements, not generic best practices.

10. **Output Template** — Description of what structured output the model should produce when this skill is active (numbered sections with descriptions).

11. **Related Skills Table** — Markdown table mapping each related skill name to a one-sentence purpose explaining why it is complementary.

---

## Related Skills

| Skill | Purpose |
|-------|---------|
| `confidence-based-selector` | Selects the most appropriate skill for a task using confidence scoring and relevance metrics — this engineering skill feeds it well-formed skills to score |
| `task-routing-engine` | Decomposes complex tasks into sub-tasks and routes each to the best matching skill — depends on skills having accurate triggers and clear scope boundaries that this skill enforces |
| `dependency-graph-builder` | Maps inter-skill dependencies to prevent circular loads and optimize execution order — requires every skill (created with this engineering process) to declare complete and reciprocal related-skills |

> 📖 skill(local cache): confidence-based-selector, task-routing-engine, dependency-graph-builder, code-philosophy
