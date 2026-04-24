# Agent-Skill-Router FAQ

Comprehensive questions and answers about the agent-skill-router MCP system, how it works, and best practices for managing and using skills.

---

## Section 1: Why MCP is Better Than Direct File Loading

### Q1: Why should I use the MCP skill-router instead of just loading all SKILL.md files directly?

The MCP skill-router solves a fundamental problem: **context efficiency**. With 387+ skills in the repository, loading all of them directly would consume ~30MB of tokens for every single request—making responses slow, expensive, and often irrelevant.

The MCP router acts as an intelligent gatekeeper. Instead of loading everything, it:

1. **Indexes** all skill metadata (name, description, triggers, domain, role) into `skills-index.json` (~126KB)
2. **Matches** your task against this index using embeddings + LLM ranking
3. **Injects only** the top 1-3 most relevant skills (typically ~2-5KB per skill)

This means you're working with **highly contextual expertise** instead of overwhelming noise. A security review task loads `coding-security-review` (not `trading-vwap-execution`). A Kubernetes deployment loads `cncf-kubernetes` (not `programming-sorting-algorithms`).

The result: **faster responses, lower API costs, and better quality answers because the AI isn't distracted by irrelevant context.**

### Q2: What are the performance benefits of using MCP skill-router?

The performance gains are substantial:

| Metric | Direct Loading | MCP Router |
|--------|---|---|
| **Context per request** | ~30MB (all 387 skills) | ~5-10KB (top 1-3 skills) |
| **Response latency** | +3-5 seconds | +10ms warm / +3.5s cold |
| **API cost** | ~$0.50-1.00 per request | ~$0.01-0.05 per request |
| **Quality (relevance)** | Low (distraction) | High (focused) |
| **Memory footprint** | High | Low |

In warm-cache scenarios (repeated queries), the MCP router adds just **~10ms** of overhead. In cold scenarios, it adds ~3.5s **once**, then caches for future queries.

The token savings alone justify the approach: if you save 25MB of tokens per request and make 100 requests/day, that's **2.5GB of tokens saved per day**—equivalent to $500-1000/month in API costs at OpenAI rates.

### Q3: How does the skill-router handle 387 skills without blowing up the context window?

The answer is **lazy loading with intelligent indexing**:

1. **Pre-compute metadata**: Each skill is indexed once when added. This extracts:
   - Name, description, domain, role, triggers
   - Related skills, author, source
   - Word count and estimated token cost
   - This metadata lives in `skills-index.json` (~126KB total)

2. **Query-time matching**: When you ask a question:
   - Task is embedded as a vector
   - Router performs cosine similarity search against 387 embeddings (< 1ms)
   - Top 20 candidates are returned with confidence scores
   - LLM re-ranks top 20 to select best 1-3
   - Only those 1-3 skill files are read from disk

3. **Context injection**: The matched skills are injected into your message, but earlier in the context pipeline—they don't count as "context" in the LLM's response generation.

This architecture means: **you can have 5,000 skills and still get sub-second matching**. The index is tiny, matching is fast, and you only load what's relevant.

### Q4: Can I just load all skills at once? Why shouldn't I?

Technically, yes—but it's a bad idea for several reasons:

**Token & Cost Impact:**
- 387 skills × ~2-5KB each = ~1-2MB of raw Markdown
- Encoded as tokens = ~300,000-500,000 tokens per request
- At OpenAI rates: ~$0.20-0.50 per request
- MCP router: ~$0.01-0.05 per request
- **Result: 5-10x higher costs**

**Quality Degradation:**
- LLM has to parse irrelevant context ("should I use Kubernetes for this bug fix?")
- Context confusion: similar skill names (e.g., `trading-risk-stop-loss` vs `trading-risk-position-sizing`)
- Attention splitting: model splits focus across 387 instructions instead of 1-3 focused ones
- **Result: slower, lower-quality responses**

**Response Latency:**
- All 387 skills must be read from disk/GitHub
- All must be parsed, validated, injected
- LLM must process massive context before generating responses
- **Result: 2-5 second overhead per request**

**Memory & Infrastructure:**
- 1-2MB+ per request means more memory usage
- Larger context requires better hardware
- Caching becomes inefficient (cold requests require full reload)
- **Result: increased infrastructure costs**

**Example:** If you ask "How do I format a Python string?" and all 387 skills are loaded, the model has to:
- Read instructions on Kubernetes deployments
- Read instructions on trading algorithms
- Read instructions on database replication
- Filter through noise to find `coding-python-strings`
- Finally answer your question

With MCP routing: it loads `coding-python-strings` directly. **Much faster, much cheaper, much clearer.**

---

## Section 2: How the Skill-Router Works

### Q5: How does skill auto-routing work?

Here's the complete workflow, step by step:

```
┌─────────────────────────────────────────────────────────┐
│  1. USER ASKS A QUESTION                                │
│     "I need to implement a stop-loss strategy"          │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  2. OPENCODE INVOKES route_to_skill() MCP TOOL          │
│     - Passes user message + context                     │
│     - No manual intervention needed                      │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  3. SKILL-ROUTER API (:3000) RECEIVES REQUEST           │
│     - Validates request (safety checks)                 │
│     - Extracts task: "implement stop-loss strategy"     │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  4. EMBEDDING SERVICE GENERATES TASK VECTOR             │
│     - Converts text to 1536-dim vector                  │
│     - Result cached for 1 hour                          │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  5. VECTOR DATABASE SEARCH                              │
│     - Loads skills-index.json (~126KB)                  │
│     - Computes cosine similarity: task vs 387 skills    │
│     - Returns top 20 candidates with scores             │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  6. LLM RE-RANKING (optional, for complex matches)      │
│     - Asks GPT-4: "Which 1-3 of these 20 are best?"     │
│     - Caches result for identical queries               │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  7. SKILL CONTENT FETCHED                               │
│     - Top 1-3 skills loaded from disk/GitHub            │
│     - Parsed and formatted                              │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  8. SKILL INJECTED INTO CONTEXT                         │
│     - Skill content prepended to conversation           │
│     - Model reads skill before answering                │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│  9. MODEL ANSWERS YOUR QUESTION                         │
│     - Response uses skill guidance & constraints        │
│     - Answer ends with: > 📖 skill: trading-risk-...    │
└─────────────────────────────────────────────────────────┘
```

**Timeline (cold vs warm):**
- **Cold (first request):** Embedding (~400ms) + Vector search (~1ms) + LLM rank (~3000ms) + Fetch (~150ms) = **~3.5 seconds total**
- **Warm (cached):** Embedding (~1ms) + Vector search (~1ms) + LLM rank (~5ms) + Fetch (~1ms) = **~10ms total**

The router is transparent—you don't need to do anything. Just ask your question, and the right skill automatically loads.

### Q6: What are "triggers" and why are they important?

**Triggers** are keywords and phrases in the `metadata.triggers` field that enable **conversational discovery**. They're how the router knows your question relates to a particular skill.

**Example trigger sets:**

```yaml
# trading-risk-stop-loss/SKILL.md
metadata:
  triggers: stop loss, trailing stop, ATR stop, stop placement, position protection, emergency stop, stop-loss

# cncf-kubernetes/SKILL.md
metadata:
  triggers: kubernetes, k8s, managing containers, deploying apps, how do i run containers

# coding-code-review/SKILL.md
metadata:
  triggers: code review, pull request, quality checks, security review, how do i review code
```

**Why are triggers important?**

1. **Conversational matching**: When you type "how do I review code?", the router matches `code-review` even though you never said "code review" exactly.

2. **Multilingual discovery**: Triggers include both technical terms (`kubernetes`) and business language (`managing containers`). This means:
   - Engineers find it by typing `k8s`
   - Managers find it by typing `managing containers`
   - Learners find it by typing `how do I run containers`

3. **False positive prevention**: Generic triggers like `code` or `risk` would match every request. Specific triggers (`code review`, `stop loss`) ensure precision.

4. **Vector search improvement**: Even with embeddings, explicit triggers improve matching accuracy. A question about "reviewing a Python function" might miss `coding-code-review` if triggers only said `peer-review`. With `code review, pull request, quality checks`, the match is guaranteed.

**Trigger quality directly impacts routing accuracy.** Poorly designed triggers cause:
- False positives (wrong skills loaded)
- False negatives (right skill not loaded)
- Wasted tokens on irrelevant context

That's why AGENTS.md includes extensive trigger engineering guidelines—see the "Trigger Engineering for Conversational Discovery" section.

### Q7: Can I manually request a skill without relying on auto-routing?

Yes, absolutely. OpenCode supports two loading mechanisms:

**Method 1: Auto-routing (recommended)**
```
You: "I need to implement a stop-loss strategy"
         ↓
Router detects "stop loss" trigger → trading-risk-stop-loss loads automatically
         ↓
You get an answer using that skill
```

**Method 2: Manual skill loading**
```
You: /skill trading-risk-stop-loss
         ↓
Skill loads immediately, persists for rest of conversation
         ↓
All subsequent answers use this skill (even if it doesn't match the task)
```

Manual loading is useful when:
- Auto-routing isn't matching correctly (triggers need adjustment)
- You want to force a specific skill for a conversation
- You're testing a new skill
- You know exactly which skill you need

To manually load a skill, use the `/skill` command:
```
/skill <skill-name>
```

Example:
```
/skill trading-risk-position-sizing
/skill cncf-kubernetes
/skill coding-security-review
```

You can also stack multiple skills:
```
/skill trading-risk-stop-loss
/skill trading-risk-kill-switches
```

Both skills now apply to your conversation. However, **auto-routing is preferred** because the router intelligently selects only the most relevant skills, keeping context lean and focused.

### Q8: What happens if the router matches multiple skills to my task?

The router supports **multi-skill loading**. This is a feature, not a bug:

**Example scenario:**
```
You: "Implement a trading algorithm with stop-loss and position sizing"
         ↓
Router finds:
  1. trading-risk-stop-loss (score: 0.92)
  2. trading-risk-position-sizing (score: 0.88)
  3. trading-strategy-backtesting (score: 0.71)
         ↓
Selects top 3 (or top 1-2 depending on confidence gap)
         ↓
All 3 skills injected into context
         ↓
Model answers using all three skills' guidance
```

**How selection works:**

1. **Vector search** returns top 20 candidate skills with similarity scores (0-1 scale)
2. **Confidence thresholding**: Only skills > 0.70 confidence are considered
3. **LLM ranking**: Top candidates sent to GPT-4 with task description
4. **Smart selection**:
   - If top skill is 0.92 and next is 0.88: both loaded (small gap)
   - If top skill is 0.92 and next is 0.65: only top loaded (big gap)
   - Default: load top 1-3 skills (configurable)

**Response citation:**
Every response ends with loaded skill names:
```
> 📖 skill: trading-risk-stop-loss, trading-risk-position-sizing
```

This transparency lets you verify which skills influenced the answer.

**Potential false positives:**
If two skills have overlapping triggers, the router might load both. Example:
```
You: "What's the best way to manage risk?"
         ↓
Both loaded:
  1. trading-risk-stop-loss (high confidence)
  2. trading-risk-kill-switches (medium confidence)
         ↓
Model uses both perspectives
```

This is usually **beneficial**—complementary skills provide more complete answers. However, if you get irrelevant skills, it indicates **trigger overlap** that should be fixed by improving trigger specificity (see AGENTS.md).

---

## Section 3: Skill Management

### Q9: How do I add a new skill to the repository?

Here's the complete step-by-step workflow:

**Step 1: Create the skill directory**
```bash
mkdir -p skills/domain-topic/
```

Naming conventions:
- Use kebab-case (lowercase with hyphens)
- Pattern: `domain-topic-subtopic`
- Examples: `trading-risk-stop-loss`, `cncf-kubernetes`, `coding-security-review`

**Step 2: Create SKILL.md**

Create `/skills/domain-topic/SKILL.md` with YAML frontmatter + content:

```markdown
---
name: domain-topic
description: One-line description of what this skill teaches the model to do (not what it's about).
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: trading  # or: agent, cncf, coding, programming
  role: implementation  # or: reference, orchestration, review
  scope: implementation  # or: infrastructure, orchestration, review
  output-format: code  # or: manifests, analysis, report
  triggers: keyword1, keyword2, keyword3, how do i ..., ...
  related-skills: skill-name-1, skill-name-2
---

# Skill Title (Human-Readable)

Brief paragraph explaining the skill's purpose.

## When to Use

- Situation 1
- Situation 2

## When NOT to Use

- Anti-pattern 1
- Situation where skill doesn't apply

## Core Workflow / Content

[Your skill content here]
```

See AGENTS.md for complete frontmatter requirements and content structure.

**Step 3: Validate YAML**
```bash
python3 scripts/reformat_skills.py
```

This checks YAML syntax and fills missing optional fields.

**Step 4: Enhance triggers (optional)**
```bash
python3 scripts/enhance_triggers.py
```

This tool suggests additional conversational triggers to improve discovery.

**Step 5: Regenerate indices**
```bash
python3 scripts/generate_index.py
```

This updates `skills-index.json`, which the router reads for skill discovery.

**Step 6: Regenerate README catalog**
```bash
python3 scripts/generate_readme.py
```

This updates the skills catalog in README.md with your new skill.

**Step 7: Commit and push**
```bash
git add -A
git commit -m "feat: add domain-topic skill

- New skill for [purpose]
- Triggers: [list key triggers]
- Related to: [list related skills]"
git push origin main
```

**Complete one-liner for steps 3-6:**
```bash
python3 scripts/reformat_skills.py && \
python3 scripts/enhance_triggers.py && \
python3 scripts/generate_index.py && \
python3 scripts/generate_readme.py && \
echo "✅ All automation complete!"
```

**How long does it take for the new skill to be routable?**

- Immediately in your local repo
- Auto-loaded on GitHub within minutes
- Picked up by the router on next sync (default: every 1 hour via `SKILL_SYNC_INTERVAL`)
- To force immediate pickup: `curl -X POST http://localhost:3000/reload`

### Q10: What is the relationship between skill domains, roles, and triggers?

Each skill has three classification axes that define its purpose and discoverability:

**Domain** (what field of expertise):

| Domain | Purpose | Examples |
|--------|---------|----------|
| `agent-` | AI agent orchestration, routing, multi-agent systems | task-routing, confidence-selection, fallback-handling |
| `cncf-` | Cloud-native infrastructure (Kubernetes, Prometheus, etc.) | kubernetes, prometheus, istio, kyverno |
| `coding-` | Software engineering patterns, quality practices | code-review, security-audit, refactoring, testing |
| `trading-` | Algorithmic trading, quantitative finance, execution | stop-loss, position-sizing, vwap-execution, backtesting |
| `programming-` | CS fundamentals, algorithms, data structures | sorting-algorithms, graph-traversal, dynamic-programming |

**Role** (what the skill is for):

| Role | Definition | When Used |
|------|-----------|-----------|
| `implementation` | Teaches the model **how to build** something | Writing code, creating systems, implementing strategies |
| `reference` | Provides **definitions, background, theory** | Understanding concepts, learning, documentation |
| `orchestration` | Defines **workflows, sequencing, decision-making** | Multi-step processes, agent routing, task decomposition |
| `review` | Provides **quality criteria and checklists** | Code review, security audit, compliance checking |

**Scope** (what context applies):

| Scope | Applies To |
|-------|-----------|
| `implementation` | Building, coding, feature development |
| `infrastructure` | Systems, deployment, operations |
| `orchestration` | Multi-step workflows, agent coordination |
| `review` | Quality assurance, validation |

**Output Format** (what kind of output the model should produce):

| Format | Output Type | Examples |
|--------|-----------|----------|
| `code` | Code in Python, JavaScript, etc. | Implementation skills, programming reference |
| `manifests` | Kubernetes YAML, Terraform, JSON | Infrastructure skills (cncf-*) |
| `analysis` | Reports, summaries, findings | Review skills, research |
| `report` | Formatted documentation, audit results | Quality assurance, compliance |

**How they work together:**

```
User asks: "How do I review this Python code for security?"
         ↓
Router looks for skills where:
  - Domain: coding (software engineering)
  - Role: review (quality/validation)
  - Scope: implementation (code context)
  - Output: analysis (findings report)
  - Triggers: "code review", "security review", "quality"
         ↓
Finds: coding-security-review
         ↓
Loads skill with all constraints
```

**Triggers** connect conversational language to this taxonomy:

```yaml
# coding-security-review/SKILL.md
metadata:
  domain: coding
  role: review
  triggers: code review, security review, vulnerability, OWASP, how do i review code
  # These triggers map to the domain/role above
```

Users might not know the skill name (`coding-security-review`), but they know what they need:
- "review this code" → triggers match → skill loads
- "check for vulnerabilities" → triggers match → skill loads
- "security audit" → triggers match → skill loads

### Q11: How do I update an existing skill without recreating it?

Updating a skill is straightforward—just edit the SKILL.md file in place:

**Step 1: Edit the skill**
```bash
# Edit the skill content
nano skills/domain-topic/SKILL.md
```

You can modify:
- Description, purpose, content
- Triggers (to improve discovery)
- Related skills
- Code examples
- Anything in the file

**Step 2: Validate**
```bash
python3 scripts/reformat_skills.py
```

This ensures YAML is still valid after your edits.

**Step 3: (Optional) Enhance triggers**
```bash
python3 scripts/enhance_triggers.py
```

If you modified triggers, this will suggest improvements.

**Step 4: Regenerate indices**
```bash
python3 scripts/generate_index.py
```

This updates the router's index with your new trigger keywords.

**Step 5: Regenerate README**
```bash
python3 scripts/generate_readme.py
```

This updates the skill's entry in the README catalog.

**Step 6: Commit**
```bash
git add skills/domain-topic/SKILL.md
git commit -m "docs: update domain-topic skill

- Improved description
- Added triggers: [list new triggers]
- Enhanced examples"
git push origin main
```

**When do updates become routable?**

- Immediately in your local repo (if running router locally)
- Within minutes on GitHub
- Next auto-sync (~1 hour, or manual `curl -X POST http://localhost:3000/reload`)

**Important:** The skill name (directory name) cannot be changed in-place—that requires deletion + recreation. But all content, triggers, and metadata can be freely edited.

### Q12: What happens when I run `generate_readme.py`?

The `generate_readme.py` script auto-generates the skills catalog in your README.md. It's a critical part of maintaining the repository.

**What it does:**

1. **Scans all skills** in the `skills/` directory
2. **Extracts metadata** from each SKILL.md frontmatter:
   - Name, description, domain, role, triggers
3. **Generates three organized sections:**
   - **Skills by Domain** — Table grouped by domain (agent, cncf, coding, trading, programming)
   - **Skills by Role** — Table grouped by role (implementation, reference, orchestration, review)
   - **Complete Skills Index** — Full alphabetical table with all 387 skills
4. **Inserts content** between `<!-- AUTO-GENERATED SKILLS INDEX START/END -->` markers
5. **Preserves** all other README content outside the markers
6. **Adds metadata**: timestamp, skill count, total lines

**Example output (abbreviated):**

```markdown
<!-- AUTO-GENERATED SKILLS INDEX START -->

# Skills Catalog

**Total Skills:** 387 | **Last Updated:** 2026-04-24T13:58:00Z

## Skills by Domain

### agent-* (AI Agent Orchestration)

| Name | Description | Role |
|------|-------------|------|
| [agent-confidence-selector](skills/agent-confidence-selector/SKILL.md) | Implements confidence scoring for multi-agent skill selection... | implementation |
| [agent-task-routing](skills/agent-task-routing/SKILL.md) | Routes tasks to optimal agent based on complexity... | orchestration |

### coding-* (Software Engineering)

| Name | Description | Role |
|------|-------------|------|
| [coding-code-review](skills/coding-code-review/SKILL.md) | Comprehensive code review methodology... | review |
| [coding-security-review](skills/coding-security-review/SKILL.md) | Security-focused code review with OWASP coverage... | review |

[... more tables ...]

<!-- AUTO-GENERATED SKILLS INDEX END -->
```

**Features:**

- ✅ **696+ hyperlinks** to all 387 skills (clickable to SKILL.md)
- ✅ **Smart description truncation** at word boundaries (no broken sentences)
- ✅ **Three organizational views** (Domain, Role, Alphabetical)
- ✅ **Zero manual work** — completely automated
- ✅ **Timestamps and counts** for easy auditing

**When to run it:**

- After adding new skills
- After modifying skill metadata (description, triggers, domain, role)
- Before committing changes (ensures README is up-to-date)
- As part of CI/CD pipeline (automatic skill catalog maintenance)

**Usage:**
```bash
# Update README.md in-place
python3 scripts/generate_readme.py

# Generate custom output file
python3 scripts/generate_readme.py --output custom_skills.md

# Specify custom repository root
python3 scripts/generate_readme.py --repo-root /path/to/repo
```

---

## Section 4: Skill Quality & Consistency

### Q13: What quality standards do skills need to meet?

Every skill submitted to the repository must meet the Quality Checklist from AGENTS.md. Here are the key standards:

**Frontmatter Standards:**
- [ ] `name` exactly matches directory name (kebab-case)
- [ ] `description` is one sentence starting with active verb
- [ ] `metadata.triggers` is 3-8 specific, meaningful keywords
- [ ] `metadata.domain` is one of: agent, cncf, coding, trading, programming
- [ ] `metadata.role` is one of: implementation, reference, orchestration, review
- [ ] `metadata.related-skills` lists adjacent skills (if any)
- [ ] YAML syntax is valid (checked by `reformat_skills.py`)

**Content Standards:**
- [ ] H1 title is human-readable (not kebab-case)
- [ ] "When to Use" section with concrete situations
- [ ] "When NOT to Use" section (for complex skills)
- [ ] Core content (workflow, patterns, constraints)
- [ ] No placeholder text ("TODO", "FIXME", broken links)
- [ ] Code examples are complete and runnable
- [ ] References to related documentation (AGENTS.md, SKILL_FORMAT_SPEC.md)

**Trigger Standards (Critical):**
- [ ] Includes **both** technical AND conversational terms
- [ ] At least one "how do I..." variant if skill solves a task
- [ ] Avoids ultra-generic terms (`code`, `risk`, `data`)
- [ ] All triggers are distinct and meaningful
- [ ] Follows domain-specific trigger engineering guidelines

**Domain-Specific Standards:**

For `coding-*` skills:
- [ ] At least one BAD/GOOD code example pair
- [ ] References a standard (SOLID, OWASP, DRY, etc.)
- [ ] MUST DO / MUST NOT DO constraints

For `trading-*` skills:
- [ ] Python code with type hints and docstrings
- [ ] Risk constraints explicitly stated
- [ ] Follows APEX platform conventions

For `cncf-*` skills:
- [ ] Complete YAML manifest examples
- [ ] Architecture design patterns
- [ ] Integration approaches
- [ ] Common pitfalls section

For `agent-*` skills:
- [ ] Orchestration flow diagram (ASCII)
- [ ] Fallback/error routing described
- [ ] References 5 Laws of Elegant Defense

**How violations are caught:**

1. **YAML validation**: `reformat_skills.py` catches syntax errors
2. **Manual review**: All PR submissions are reviewed against the checklist
3. **Automated linting** (future): CI/CD pipeline can enforce standards
4. **Content scanning**: Check for placeholder text, broken links

**Enforcement:**

Skills that don't meet these standards:
- Won't be merged to main branch
- Feedback provided on specific violations
- Author has chance to fix before resubmission

This ensures the skill repository maintains high quality and consistency across all 387 skills.

### Q14: How are skills tested before being added to the repository?

The testing process involves multiple layers:

**Layer 1: Automated Validation**
```bash
# Run this before PR submission
python3 scripts/reformat_skills.py   # YAML syntax
python3 scripts/generate_index.py     # Index compatibility
python3 scripts/generate_readme.py    # Catalog integration
```

This catches:
- YAML parsing errors
- Missing required fields
- Malformed metadata
- Index registration failures

**Layer 2: Quality Checklist Review**

All PRs are reviewed against the 40-point Quality Checklist from AGENTS.md:

✅ Frontmatter complete and valid  
✅ H1 title is human-readable  
✅ "When to Use" section present  
✅ "When NOT to Use" section present  
✅ Triggers are specific + conversational  
✅ Code examples (if applicable) are complete  
✅ No placeholder text or broken links  
✅ Content is actionable and clear  

**Layer 3: Trigger Quality Testing**

Triggers are validated for:
- **Specificity**: Do they match the right skill and nothing else?
- **Conversational**: Would real users search these terms?
- **Coverage**: Do they include technical AND business language?
- **False positives**: Would these trigger on unrelated tasks?

**Example trigger testing:**

```
Skill: trading-risk-stop-loss
Triggers: stop loss, trailing stop, ATR stop, stop placement, position protection

Test queries:
✅ "Implement a stop loss" → Should match (triggers: "stop loss")
✅ "How do I use a trailing stop?" → Should match (triggers: "trailing stop")
✅ "What's an ATR-based stop?" → Should match (triggers: "ATR stop")
❌ "I need to stop my database" → Should NOT match (unrelated)
❌ "Help with loss function" → Should NOT match (different context)
```

**Layer 4: Integration Testing**

Once merged, skills are tested for:
- Index registration: Can the router find it?
- Embedding quality: Do task queries match the skill?
- Multi-skill scenarios: Does it work alongside other skills?
- Citation accuracy: Does it appear in response footers correctly?

**Layer 5: Community Feedback**

After merge, users provide feedback:
- "This skill didn't load for my query"
- "These triggers are too broad"
- "Related skill X should be linked"
- Triggers are refined based on actual usage patterns

**Timeline from PR to Production:**

1. **Day 1**: PR submitted with new skill
2. **Day 1**: Automated validation runs (5 minutes)
3. **Day 1-2**: Manual quality review (30 minutes - 1 hour)
4. **Day 2**: Requested changes addressed (if any)
5. **Day 2**: PR approved and merged
6. **Hour 1**: Router picks up new skill (next sync)
7. **Day 1+**: Community uses and provides feedback
8. **Week 1**: Trigger refinements made if needed

**Example: Adding `trading-vwap-execution`**

```
Week 1:
  PR created with skill content
  YAML validation: ✅ PASS
  Trigger check: ⚠️ "execution" too generic, recommend adding "volume-weighted average price"
  Code examples: ✅ Complete Python with type hints
  Related skills: ✅ Linked to position-sizing and order-management

Week 2:
  Author updates triggers
  PR approved and merged
  Router syncs within 1 hour
  Users start testing

Week 3:
  User feedback: "VWAP didn't trigger for 'volume-weighted execution'"
  Trigger updated to include "volume-weighted execution"
  Router syncs, improves matching
```

The multi-layer approach ensures skills are high-quality from day 1, with continuous improvement through community use.

### Q15: What makes a "good trigger" vs a "bad trigger"?

This is critical because triggers determine whether skills are discoverable. Here's how to evaluate them:

**Good Trigger Characteristics:**

| Property | Example | Why |
|----------|---------|-----|
| **Specific domain term** | `kubernetes`, `postgresql`, `stop loss` | Unambiguous, matches skill scope |
| **Common abbreviation** | `k8s`, `postgres`, `ATR` | Power users search this way |
| **Conversational variant** | `how do I deploy apps`, `managing containers` | Non-technical users search this way |
| **Task-oriented phrase** | `scaling apps`, `backups`, `monitoring` | Users think in tasks first |
| **Business language** | `cost savings`, `reliability`, `compliance` | Managers/business users search this way |
| **3-8 terms total** | ✅ 6 terms | Sweet spot for specificity + coverage |

**Bad Trigger Characteristics:**

| Property | Example | Why |
|----------|---------|-----|
| **Ultra-generic** | `code`, `data`, `risk`, `system` | Matches nearly everything, high false positives |
| **Internal jargon** | `KubeletConfig`, `DeploymentController` | Team-specific, users don't know these terms |
| **Only abbreviations** | `k8s, pg, atm` | Non-technical users won't find it |
| **Hyphenation inconsistent** | Only `stop-loss`, not `stop loss` | Misses natural user phrasing |
| **Too narrow** | `Kubernetes StatefulSet with persistent volume networking` | One phrase too long, users search simpler terms |
| **Only technical, no conversational** | `kubernetes, k8s, container orchestration` | Misses business/manager searches |
| **Too many terms** | 12+ terms | Dilutes signal, causes false positives, hard to maintain |

**Good vs Bad Examples:**

**Example 1: Stop Loss Skill**

```yaml
# ❌ BAD — too broad
triggers: stop, loss, trading, risk, strategy, price, exit

# ❌ BAD — too narrow/technical
triggers: StopLossManager, PositionProtection, EmergencyStop

# ❌ BAD — only abbreviations
triggers: SL, TP, ATR

# ✅ GOOD — balanced mix
triggers: stop loss, trailing stop, ATR stop, how do i limit losses, position protection, emergency stop, stop-loss
```

**Example 2: Code Review Skill**

```yaml
# ❌ BAD — too generic
triggers: code, review, quality, check, best practices

# ❌ BAD — only PR/technical
triggers: pull request, code review, peer review, github

# ❌ BAD — missing conversational
triggers: code-review, code_review, CRMetrics

# ✅ GOOD — balanced
triggers: code review, pull request, quality checks, security review, peer review, how do i review code
```

**Example 3: Kubernetes Skill**

```yaml
# ❌ BAD — misses common usage
triggers: kubernetes

# ❌ BAD — too broad
triggers: kubernetes, container, orchestration, cloud, deployment, scaling

# ❌ BAD — only technical
triggers: kubernetes, k8s, pod, deployment, statefulset, daemonset

# ✅ GOOD — technical + conversational
triggers: kubernetes, k8s, managing containers, deploying apps, how do i scale containers
```

**Red Flags in Trigger Quality:**

1. **No conversational variants** → Add "how do I..." phrases
2. **Only abbreviations** → Add spelled-out terms
3. **Generic terms** → Remove or make more specific
4. **Hyphenation inconsistent** → Include both variants
5. **No business language** → Add business/manager perspective
6. **> 8 terms** → Prioritize and cut least important
7. **< 3 terms** → Expand coverage to more search patterns

**How to Test Your Triggers:**

Before submitting a skill, ask yourself:

1. **Real user test**: Would I actually search these terms?
2. **Non-technical test**: Could a manager/non-engineer find this?
3. **False positive test**: Would these triggers match irrelevant tasks?
4. **Coverage test**: Do my triggers hit the main way people describe this?

**Example questions to test:**
- "User asks 'how do I limit my losses?' → Does a stop-loss skill with trigger 'how do i limit losses' match?" ✅
- "User asks 'stop the server' → Does it match?" ❌ (good—not about trading)
- "User asks 'trailing stop-loss order' → Does it match?" ✅ (triggers include both)
- "User asks 'emergency stop button' → Does it match?" ✅ (triggers include "emergency stop")

High-quality triggers balance **precision** (only match when relevant) and **recall** (match all relevant queries).

### Q16: How are related skills determined and linked?

Related skills are essential for **skill discovery chains**—users load one skill and discover complementary ones.

**What Makes Skills "Related"?**

Skills are related if using one naturally leads to needing the other:

**Layering Relationships (strong):**
```
trading-risk-stop-loss ←→ trading-risk-kill-switches
  (normal risk layer)      (emergency layer)

User loads stop-loss skill, sees related-skills link to kill-switches
→ User realizes they should also learn about emergency stops
```

**Sequencing Relationships (strong):**
```
cncf-kubernetes ←→ cncf-helm
  (install K8s)     (manage apps)

User learning Kubernetes sees helm → realizes they'll need it for production
```

**Complementary Relationships (strong):**
```
cncf-prometheus ←→ cncf-alertmanager
  (metrics)           (alerts)

User setting up monitoring sees both → understands they work together
```

**Variant Relationships (medium):**
```
coding-code-review ←→ coding-security-review
  (general review)     (security-focused)

User doing general review sees security variant → loads if needed
```

**Weak Relationships (avoid linking):**
```
kubernetes ←→ docker (overlapping but separate skills)
trading-stop-loss ←→ trading-bollinger-bands (unrelated strategies)
code-review ←→ testing (both quality, but independent)
```

**How to Determine Related Skills:**

1. **Answer this question**: "If someone is learning this skill, what other skill would they naturally want next?"

2. **Reciprocity rule**: If A links to B, then B must link to A. Never one-way relationships.

3. **Optimal count**: 2-4 related skills
   - 0-1: Skill is isolated (OK, but less discoverable)
   - 2-4: Goldilocks zone
   - 5+: Too many options, dilutes focus

4. **Network thinking**: View related skills as a graph:
   ```
   foundation → tactical → advanced
   
   trading-position-sizing (how much to trade?)
        ↓ related-skills
   trading-stop-loss (where to exit?)
        ↓ related-skills
   trading-kill-switches (emergency out?)
   ```

**Example: Building a Trading Skills Network**

```yaml
# trading-position-sizing/SKILL.md
metadata:
  related-skills: trading-risk-kelly-criterion, trading-risk-stop-loss

# trading-risk-kelly-criterion/SKILL.md
metadata:
  related-skills: trading-position-sizing, trading-risk-portfolio-rebalancing

# trading-risk-stop-loss/SKILL.md
metadata:
  related-skills: trading-position-sizing, trading-risk-kill-switches

# trading-risk-kill-switches/SKILL.md
metadata:
  related-skills: trading-risk-stop-loss, trading-risk-maximum-drawdown
```

User journey:
```
"How much should I trade?" 
    → Loads: position-sizing
    → Sees related: kelly-criterion, stop-loss
    → Loads: stop-loss
    → Sees related: position-sizing, kill-switches
    → Full understanding of risk management ecosystem
```

**How Related Skills Work:**

1. **Metadata field**: Each skill lists related skills in frontmatter
   ```yaml
   metadata:
     related-skills: skill-name-1, skill-name-2, skill-name-3
   ```

2. **Documentation**: Often skills include a "Related Skills" section:
   ```markdown
   ## Related Skills
   
   | Skill | Purpose |
   |-------|---------|
   | trading-risk-stop-loss | Where to exit positions |
   | trading-risk-kill-switches | Emergency protection layer |
   ```

3. **Router awareness**: The router can recommend related skills when loading one
   ```
   You load: trading-position-sizing
   Router suggests: "Related: trading-risk-stop-loss, trading-risk-kill-switches"
   ```

**Maintenance:**

When you discover related skills during skill creation:

1. **Update your skill frontmatter**:
   ```yaml
   metadata:
     related-skills: existing-skill-1, existing-skill-2
   ```

2. **Update the linked skills**:
   - They must reciprocate the link
   - If they don't, add your skill to their `related-skills`

3. **Regenerate indices**:
   ```bash
   python3 scripts/generate_index.py
   ```

4. **Verify in README**:
   ```bash
   python3 scripts/generate_readme.py
   ```

**Anti-pattern: Too Many Related Skills**

```yaml
# ❌ BAD — overwhelming
related-skills: skill-1, skill-2, skill-3, skill-4, skill-5, skill-6, skill-7

# ✅ GOOD — focused discovery chain
related-skills: skill-1, skill-2, skill-3
```

With 387 total skills, having 5+ related skills per skill creates a dense network that overwhelms users. 2-4 is the sweet spot for guided discovery without paralysis.

---

## Section 5: OpenCode Integration

### Q17: How does the skill-router integrate with OpenCode?

The skill-router integrates via the **Model Context Protocol (MCP)**, which allows OpenCode to invoke external tools. Here's how it works:

**Architecture Overview:**

```
┌──────────────────────────────────────┐
│        OpenCode (LLM Interface)      │
│  - User types question               │
│  - Invokes MCP tools                 │
└─────────────┬────────────────────────┘
              │
              │ MCP Protocol (JSON-RPC)
              │
              ↓
┌──────────────────────────────────────┐
│     skill-router-mcp.js (Node.js)    │
│  - Converts OpenCode calls to API    │
│  - Fetches skill content             │
│  - Injects into context              │
└─────────────┬────────────────────────┘
              │
              │ HTTP REST API
              │
              ↓
┌──────────────────────────────────────┐
│   skill-router-api (Fastify :3000)   │
│  - Routes tasks to skills            │
│  - Manages embeddings + rankings     │
│  - Caches results                    │
└─────────────┬────────────────────────┘
              │
              ├→ Embedding Service (OpenAI/Local)
              ├→ Vector Database (in-memory index)
              ├→ LLM Ranker (GPT-4/Local)
              └→ GitHub/Disk (skill content)
```

**Detailed Integration Flow:**

1. **OpenCode startup** → Reads `skill-router-api.md` from GitHub
   - Learns about available MCP tools
   - Registers `route_to_skill()` tool

2. **User asks question** → OpenCode receives task

3. **MCP tool invoked** → `route_to_skill(task)`
   - OpenCode calls the MCP tool automatically (no user action)
   - Passes task description + context

4. **MCP forwards to API** → HTTP POST to `http://localhost:3000/route`
   - Sends task, user context, constraints
   - Waits for router response

5. **Router matches skills** → Follows workflow from Q5
   - Embedding + vector search + ranking
   - Returns top 1-3 skills with scores

6. **MCP fetches skill content** → Parallel requests
   - Calls `GET /skill/skill-name-1` for each matched skill
   - Receives full SKILL.md content

7. **Skills injected into context** → Prepended to conversation
   - Content appears before user's question
   - LLM reads skill before answering

8. **LLM generates response** → Using skill guidance
   - Answer follows skill constraints
   - Response includes skill citations

9. **Response ends with citation** → `> 📖 skill: skill-name`
   - Lists all loaded skills
   - User sees transparency

**Code Example: MCP Tool Implementation**

The `route_to_skill()` tool works like this:

```javascript
// In skill-router-mcp.js
async function route_to_skill(task) {
  // 1. Call router API
  const response = await fetch('http://localhost:3000/route', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ task })
  });
  
  const { skills } = await response.json();
  
  // 2. Fetch each skill in parallel
  const skillContents = await Promise.all(
    skills.map(skill => 
      fetch(`http://localhost:3000/skill/${skill.name}`)
        .then(r => r.text())
    )
  );
  
  // 3. Inject into context (OpenCode handles this automatically)
  return {
    skills: skills.map(s => s.name),
    contents: skillContents
  };
}
```

**When route_to_skill() Runs:**

The tool fires **automatically** on every task:
- ✅ User asks a question
- ✅ User submits code for review
- ✅ User requests help with a problem
- ✅ Every interaction triggers routing

No manual `/skill` command needed. It's transparent and automatic.

**Latency from User Perspective:**

| Scenario | Time | Experience |
|----------|------|-----------|
| Cold request (first ask) | +3.5 seconds | Noticeable pause, then answer |
| Warm request (cached) | +10ms | Instant, seamless |
| Repeated similar queries | +10ms | Very fast, good UX |

For users, the delay is transparent—they ask a question, and while the router works (~10ms-3.5s), the LLM's response generation starts (~2-5s). Total felt latency is similar to asking without routing.

### Q18: Do I need to restart OpenCode when skills are updated?

**Short answer:** No, but with caveats depending on what changed.

**Different update scenarios:**

**Scenario 1: Skill content changed (SKILL.md body)**
- Edit: `skills/domain-topic/SKILL.md` content
- Need restart?: **No**
- Why: Content is fetched fresh from the router API each time
- Timing: Changes available after next `SKILL_SYNC_INTERVAL` (default: 1 hour)
- Force immediate: `curl -X POST http://localhost:3000/reload`

**Scenario 2: Skill triggers changed**
- Edit: `metadata.triggers` in frontmatter
- Need restart?: **No** (for routing), but regenerate index
- Steps:
  ```bash
  python3 scripts/generate_index.py
  curl -X POST http://localhost:3000/reload
  ```
- Timing: Effective within 1 hour of repo push

**Scenario 3: New skill added**
- Add: `skills/new-skill/SKILL.md`
- Need restart?: **No**, if you force reload
- Steps:
  ```bash
  python3 scripts/generate_index.py
  curl -X POST http://localhost:3000/reload
  ```
- Timing: Routable immediately if using local repo, 1 hour if GitHub

**Scenario 4: Skill deleted**
- Delete: `skills/old-skill/SKILL.md`
- Need restart?: **No**, if you regenerate index
- Steps:
  ```bash
  python3 scripts/generate_index.py
  curl -X POST http://localhost:3000/reload
  ```

**Scenario 5: Metadata changed (domain, role, related-skills)**
- Edit: `metadata.*` in frontmatter
- Need restart?: **No**, if you regenerate and reload
- Steps:
  ```bash
  python3 scripts/generate_index.py
  curl -X POST http://localhost:3000/reload
  ```

**Automatic Refresh Without Manual Intervention:**

The router has built-in auto-sync:

```yaml
# Router configuration (default)
SKILL_SYNC_INTERVAL: 3600  # seconds (1 hour)
```

Every hour, the router:
- Fetches latest `skills-index.json` from GitHub
- Updates skill metadata
- Refreshes embeddings cache
- New skills become routable automatically

**To force immediate update:**
```bash
# If router is running locally
curl -X POST http://localhost:3000/reload
```

Response: `{"status": "reloading", "timestamp": "...", "skillsLoaded": 387}`

**Under the hood:**
```javascript
// Router reloads:
1. Fetch skills-index.json from GitHub
2. Re-index all skill metadata
3. Clear embedding cache
4. Clear LLM ranking cache
5. Skills ready to route immediately
```

**Best Practice Workflow:**

```bash
# 1. Make changes locally
# 2. Update skill content
# 3. Regenerate index
python3 scripts/generate_index.py

# 4. Push to GitHub
git push origin main

# 5. (Optional) Force immediate reload in router
curl -X POST http://localhost:3000/reload

# 6. New skills available immediately
```

**No OpenCode restart required.** The router is separate from OpenCode and updates independently.

### Q19: Can the skill-router run offline?

**Short answer:** Yes, fully offline mode is supported.

**Offline Architecture:**

```
Local Setup:
├── skills-index.json (local copy, ~126KB)
├── skills/ (local skill files)
└── skill-router API (:3000)
    ├── No external API calls
    ├── Embeddings: local llama.cpp
    └── LLM ranking: local model
    
Result: Zero internet required
```

**Two offline configurations:**

**Configuration 1: With llama.cpp (recommended for offline)**

```bash
# 1. Install llama.cpp (separate project)
# 2. Start llama.cpp server
./llama-server -m model.gguf

# 3. Start skill-router
EMBEDDING_PROVIDER=llamacpp \
LLM_PROVIDER=llamacpp \
LLAMACPP_URL=http://localhost:8080 \
npm start

# 4. All inference is local, no internet
```

**Configuration 2: With Docker (includes everything)**

```bash
# 1. Pull Docker image
docker pull skill-router:latest

# 2. Run container with volume mount
docker run -v $(pwd)/skills:/skills \
           -e EMBEDDING_PROVIDER=llamacpp \
           -p 3000:3000 \
           skill-router:latest

# 3. Fully offline, no external calls
```

**What Works Offline:**

| Feature | Offline | Online |
|---------|---------|--------|
| Task routing | ✅ Yes (llama.cpp) | ✅ Yes (OpenAI) |
| Embeddings | ✅ Yes (local) | ✅ Yes (OpenAI API) |
| LLM ranking | ✅ Yes (local) | ✅ Yes (OpenAI API) |
| Skill content | ✅ Yes (local disk) | ✅ Yes (GitHub) |
| Caching | ✅ Yes (in-memory) | ✅ Yes (in-memory) |

**What Requires Internet:**

| Feature | Offline | Online |
|---------|---------|--------|
| New skill sync | ❌ Requires manual | ✅ Auto-sync from GitHub |
| Embedding API | N/A (local only) | ✅ OpenAI API |
| LLM API | N/A (local only) | ✅ OpenAI API |
| GitHub skill fetch | ❌ Requires manual | ✅ On-demand fetch |

**Offline Limitations:**

1. **New skills require manual sync**
   - Skills-index.json doesn't auto-update from GitHub
   - Solution: Manually pull repo updates and regenerate index
   ```bash
   git pull origin main
   python3 scripts/generate_index.py
   ```

2. **Embedding quality varies**
   - Local llama.cpp embeddings may differ from OpenAI
   - Results: Slightly different routing decisions
   - Solution: If offline is temporary, switch back to OpenAI

3. **LLM inference speed**
   - Local inference: 200-800ms per ranking
   - OpenAI: 3000ms (cold) but faster with caching
   - Solution: Offline is acceptable for occasional use, not high-volume

**Full Offline Setup Example:**

```bash
# 1. Install llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# 2. Download model
wget https://huggingface.co/.../model.gguf

# 3. Start llama.cpp server
./llama-server -m model.gguf -ngl 35

# 4. Start skill-router
cd /path/to/skill-router
EMBEDDING_PROVIDER=llamacpp \
LLM_PROVIDER=llamacpp \
LLAMACPP_URL=http://localhost:8080 \
npm start

# 5. All requests now work offline
# No API keys needed, no internet required
```

**Cost Analysis (Offline vs Online):**

| Aspect | Offline | Online |
|--------|---------|--------|
| **API costs** | $0 | ~$0.01-0.05/request |
| **Hardware** | ~8GB RAM, GPU optional | None (use OpenAI) |
| **Latency (warm)** | ~10ms | ~10ms |
| **Latency (cold)** | ~200-800ms | ~3500ms |
| **Quality** | Good (local models) | Excellent (GPT-4) |

**Offline is ideal for:**
- ✅ Local development
- ✅ Privacy-sensitive work
- ✅ Bandwidth-constrained environments
- ✅ Cost optimization for high volume
- ❌ Optimal routing quality (needs OpenAI models)

---

## Section 6: Comparison & Context

### Q20: How do I troubleshoot when a skill isn't being auto-routed?

Skill routing failures usually fall into a few categories. Here's a systematic troubleshooting guide:

**Problem 1: Skill exists but isn't routing**

Diagnosis:
```bash
# 1. Verify skill exists in directory
ls -la skills/domain-topic/SKILL.md

# 2. Check if it's in the index
python3 -c "import json; \
idx = json.load(open('skills-index.json')); \
print([s['name'] for s in idx['skills'] if 'domain-topic' in s['name']])"

# 3. Test the skill-router API directly
curl http://localhost:3000/skills | grep domain-topic

# 4. Check skill content is valid
curl http://localhost:3000/skill/domain-topic
```

Solutions:
- **Not in index?** Regenerate: `python3 scripts/generate_index.py`
- **YAML invalid?** Validate: `python3 scripts/reformat_skills.py`
- **Still missing?** Force reload: `curl -X POST http://localhost:3000/reload`

**Problem 2: Query matches skill but doesn't trigger**

Diagnosis:
```bash
# 1. Check triggers for skill
python3 -c "import json; \
idx = json.load(open('skills-index.json')); \
s = [s for s in idx['skills'] if s['name'] == 'domain-topic'][0]; \
print('Triggers:', s['metadata']['triggers'])"

# 2. Query the router with your exact question
curl -X POST http://localhost:3000/route \
  -H "Content-Type: application/json" \
  -d '{"task":"your exact question here"}'

# 3. Check routing results
# Look at 'confidence' scores—anything < 0.70 is too low
```

Solutions:
- **No triggers defined?** Add them: Edit `metadata.triggers` in SKILL.md
- **Triggers too specific?** Add variants: "how do I...", abbreviations, business language
- **Confidence score low?** Improve trigger matching (see Q15)
- **Not in top 3?** Other skills ranking higher—adjust trigger specificity

**Problem 3: Wrong skill is routing instead**

Diagnosis:
```bash
# 1. Check router's top results
curl -X POST http://localhost:3000/route \
  -H "Content-Type: application/json" \
  -d '{"task":"your question"}'

# 2. See which skill ranked first (shouldn't be yours)

# 3. Check confidence scores
# If top skill is 0.92 and yours is 0.71, it's a trigger issue
```

Solutions:
- **Your skill's triggers overlap with another?** Make triggers more specific
- **Other skill's triggers are too broad?** File PR to improve those triggers
- **Both equally good matches?** This is expected—router loads both (see Q8)

**Problem 4: Skill was working, now stops routing**

Diagnosis:
```bash
# 1. Check if skill file still exists
ls -la skills/domain-topic/SKILL.md

# 2. Check index still has it
python3 scripts/generate_index.py

# 3. Check YAML validity
python3 scripts/reformat_skills.py

# 4. Check if router cache needs clear
curl -X POST http://localhost:3000/reload
```

Solutions:
- **Accidentally deleted?** Restore from git: `git checkout skills/domain-topic/SKILL.md`
- **Index stale?** Regenerate: `python3 scripts/generate_index.py`
- **YAML corrupted?** Validate and fix: `python3 scripts/reformat_skills.py`
- **Router cache stale?** Force reload: `curl -X POST http://localhost:3000/reload`

**Problem 5: Trigger matches but skill quality is poor**

Diagnosis:
```bash
# 1. Load skill manually to verify content
curl http://localhost:3000/skill/domain-topic | head -50

# 2. Read the full skill
cat skills/domain-topic/SKILL.md

# 3. Check if it's actually relevant to your task
```

Solutions:
- **Skill exists but is off-topic?** Triggers need refinement (see Q15)
- **Skill content is poor?** File PR with improvements
- **Triggers are misleading?** Document the issue and suggest better triggers

**Full Diagnostic Checklist:**

```bash
# Run this script to diagnose all routing issues
#!/bin/bash

echo "=== Skill Routing Diagnostics ==="

# 1. Check router health
echo -n "Router health: "
curl -s http://localhost:3000/health | python3 -m json.tool

# 2. Count skills
echo -n "Total skills: "
curl -s http://localhost:3000/skills | python3 -c "import sys, json; print(len(json.load(sys.stdin)))"

# 3. Verify index file
echo -n "Index file size: "
ls -lh skills-index.json | awk '{print $5}'

# 4. Test a sample query
echo "Sample routing test:"
curl -s -X POST http://localhost:3000/route \
  -H "Content-Type: application/json" \
  -d '{"task":"implement a stop loss"}' | python3 -m json.tool

echo "=== End Diagnostics ==="
```

**When to Ask for Help:**

If you've done all of the above and skills still aren't routing:
1. Check GitHub issues for similar problems
2. File an issue with:
   - Your query
   - Expected skill (name + reason)
   - Actual skill loaded
   - `curl http://localhost:3000/route` output
   - YAML validation results

---

## Section 7: Best Practices

### Q21: What's the recommended workflow for creating skills?

Follow this step-by-step process to ensure high-quality skills:

**Phase 1: Planning (5 min)**

1. **Identify the skill's purpose**
   - What is this skill teaching the model to do?
   - Not "it's about Kubernetes" but "it teaches how to deploy apps to Kubernetes"

2. **Choose domain correctly**
   - agent-*: Orchestration, routing, multi-agent patterns
   - cncf-*: Cloud-native infrastructure
   - coding-*: Software engineering practices
   - trading-*: Algorithmic trading
   - programming-*: CS fundamentals

3. **Define role and scope**
   - Role: implementation, reference, orchestration, or review?
   - Scope: implementation, infrastructure, orchestration, or review?

4. **Sketch triggers** (10+ candidates)
   - Technical terms: `kubernetes`, `k8s`, `ATR`, `postgresql`
   - Conversational: `how do I deploy apps`, `managing containers`
   - Business: `scaling`, `reliability`, `backups`
   - Task-oriented: `monitoring`, `alerting`, `load balancing`
   - Then narrow to 5-8 best ones

5. **Identify related skills**
   - What skills would users want after this one?
   - Are there 2-4 complementary skills?

**Phase 2: Creation (20-30 min)**

1. **Create directory**
   ```bash
   mkdir -p skills/domain-topic-subtopic/
   ```

2. **Write SKILL.md**
   - Use template from AGENTS.md
   - Fill frontmatter first
   - Write content (When to Use, Core Workflow, Examples, Constraints)
   - Code examples must be complete and runnable
   - No placeholder text

3. **Include concrete examples**
   - For coding: BAD/GOOD code example pairs
   - For infrastructure: Complete YAML manifests
   - For trading: Python with type hints
   - For agents: Workflow diagrams (ASCII)

4. **Document constraints**
   - MUST DO / MUST NOT DO sections
   - Anti-patterns to avoid
   - Common mistakes

**Phase 3: Validation (5-10 min)**

```bash
# Step 1: Validate YAML
python3 scripts/reformat_skills.py

# Step 2: Check syntax (should complete without errors)
# If errors: fix YAML formatting and re-run

# Step 3: Verify skill is readable
cat skills/domain-topic-subtopic/SKILL.md | head -50

# Step 4: Check for issues
grep -i "todo\|fixme\|example.com" skills/domain-topic-subtopic/SKILL.md
# Should return nothing
```

**Phase 4: Indexing (5 min)**

```bash
# Step 1: Update indices
python3 scripts/generate_index.py

# Step 2: Enhance triggers (optional)
python3 scripts/enhance_triggers.py

# Step 3: Update README
python3 scripts/generate_readme.py

# Step 4: Verify skill appears in README
grep -A2 "domain-topic-subtopic" README.md
```

**Phase 5: Quality Review (10 min)**

Before committing, check against the Quality Checklist:

```markdown
Frontmatter:
- [ ] name matches directory exactly
- [ ] description is 1 sentence with active verb
- [ ] triggers is 3-8 specific keywords
- [ ] domain, role, scope, output-format filled
- [ ] related-skills listed if applicable
- [ ] YAML is valid (no reformat errors)

Content:
- [ ] H1 title is human-readable
- [ ] "When to Use" section present
- [ ] "When NOT to Use" section present
- [ ] Core content complete (not placeholder)
- [ ] Code examples complete and runnable
- [ ] No TODOs, FIXMEs, or broken links
- [ ] Related skills documented

Triggers:
- [ ] Includes technical terms
- [ ] Includes conversational variants
- [ ] Includes at least one "how do I..." phrase
- [ ] No ultra-generic terms (code, risk, data)
- [ ] All triggers are distinct
```

**Phase 6: Commit (5 min)**

```bash
# Stage changes
git add skills/domain-topic-subtopic/
git add scripts/  # if indices changed
git add README.md

# Commit with meaningful message
git commit -m "feat: add domain-topic-subtopic skill

- New skill for [purpose in 1 sentence]
- Domain: [domain]
- Role: [role]
- Triggers: [key triggers listed]
- Related to: [list related skills]"

# Push
git push origin main
```

**Phase 7: Verification (2 min)**

```bash
# Verify on GitHub
# 1. Check PR appears
# 2. Verify CI/CD passes
# 3. Confirm README updated
# 4. Check skill appears in catalog

# Verify in router (1 hour after merge)
# 1. Force reload if needed: curl -X POST http://localhost:3000/reload
# 2. Test routing: curl -X POST http://localhost:3000/route ...
# 3. Verify top results include your skill
```

**Total Time: ~1 hour from idea to production**

**Workflow Diagram:**

```
Planning (5m) → Define domain, role, triggers, related skills
   ↓
Creation (20m) → Write SKILL.md with examples
   ↓
Validation (10m) → YAML check, no placeholders
   ↓
Indexing (5m) → generate_index.py, enhance_triggers.py
   ↓
Quality Review (10m) → Check 40-point checklist
   ↓
Commit (5m) → git add, git commit, git push
   ↓
Verification (2m) → Test routing, verify in README
   ↓
Done! Skill is routable (within 1 hour)
```

This structured approach ensures high-quality, discoverable skills every time.

### Q22: Should I create many specific skills or fewer general skills?

**Short answer: Be specific.** Many focused skills > few general ones.

**Why Specificity Wins:**

| Aspect | Specific Skills | General Skills |
|--------|---|---|
| **Routing accuracy** | High (triggers match exactly) | Low (triggers too broad) |
| **Context quality** | Focused, relevant | Bloated, noisy |
| **Discoverability** | Good (multiple trigger combinations) | Poor (generic triggers) |
| **Reusability** | High (applies to many tasks) | Low (applies to everything) |
| **Maintenance** | Easy (single concern) | Hard (many concerns) |
| **User experience** | Excellent (relevant) | Poor (lost in noise) |

**Examples: Specific > General**

```yaml
# ❌ GENERAL (avoid)
name: trading-risk-management
description: Covers all aspects of trading risk

# ✅ SPECIFIC (preferred)
name: trading-risk-stop-loss
description: Implements stop-loss strategies for position protection
---
name: trading-risk-position-sizing
description: Calculates optimal position sizes using Kelly Criterion
---
name: trading-risk-kill-switches
description: Implements emergency circuit breakers for portfolio protection
```

**Why?**
- User asks "how do I limit losses?" → `stop-loss` loads (specific)
- With general `risk-management`: model confused by position-sizing, kill-switches content
- Specific skills: user gets focused answer with fewer irrelevant constraints

**Another Example:**

```yaml
# ❌ GENERAL
name: cncf-kubernetes
description: Everything about Kubernetes

# ✅ SPECIFIC
name: cncf-kubernetes-deployment
description: Deploy applications to Kubernetes clusters
---
name: cncf-kubernetes-networking
description: Configure networking policies and service meshes
---
name: cncf-kubernetes-storage
description: Manage persistent storage and StatefulSets
```

**When to Be General:**

There are rare cases where broader scope makes sense:

1. **Introductory skills** (learning basics)
   - `programming-sorting-algorithms` (covers bubble, quick, merge sort)
   - Why: Learners want overview before specializing

2. **Reference materials** (definitions)
   - `trading-greek-letters` (explains Delta, Gamma, Vega, Theta)
   - Why: All are related concepts, often learned together

3. **Meta-skills** (about the skill system itself)
   - `agent-skill-routing` (how routers work)
   - Why: Single topic that benefits from breadth

4. **Foundational patterns** (many variations)
   - `coding-design-patterns` (Factory, Singleton, Observer, etc.)
   - Why: All are related patterns worth learning together

**Rule of Thumb:**

If you can split a skill into 2-3 narrower skills where each teaches one distinct concept or technique:
→ Do it. Create specific skills.

If combining skills would require repeating similar foundational content:
→ Keep it general. The efficiency is worth it.

**Practical Test:**

Before deciding on scope, ask:

1. **"Could someone master this skill in 30 minutes?"**
   - Yes → Probably good scope
   - No → Break into smaller skills

2. **"Would triggers for this skill be ultra-generic?"**
   - Yes → Too broad, split it
   - No → Good scope

3. **"Does this skill teach one main idea or many?"**
   - One main idea → Good scope
   - Many ideas → Split into specific skills

4. **"Would a user only need part of this skill?"**
   - Yes → Too broad, split it
   - No → Good scope

**Example: Should I Create `trading-execution` or `trading-vwap-execution` + `trading-twap-execution`?**

Apply the tests:

1. Master in 30 min? `trading-execution` (all algorithms) = No → Split it
2. Generic triggers? Yes (execution, algorithm) → Split it
3. One main idea or many? Many (VWAP, TWAP, ICEBERG, etc.) → Split it
4. Users need only part? Yes (just VWAP, not TWAP) → Split it

**Decision: Create specific skills:**
- `trading-vwap-execution` (Volume-Weighted Average Price)
- `trading-twap-execution` (Time-Weighted Average Price)
- `trading-iceberg-execution` (Iceberg orders)
- Each with focused content, specific triggers, concrete examples

---

## Section 8: Advanced Topics

### Q23: Can I extend the skill-router with custom matching logic?

**Short answer:** Yes, the router is extensible at multiple levels.

**Extension Points:**

**Level 1: Custom Triggers (easiest)**
```yaml
# Just edit metadata.triggers in any SKILL.md
metadata:
  triggers: your-custom, trigger-keywords
```

This is how most customization happens—improve triggers for better matching.

**Level 2: Custom Confidence Scoring**

The router supports custom confidence scoring for advanced use cases:

```bash
# Edit router config to adjust scoring weights
SIMILARITY_WEIGHT=0.6        # Vector similarity importance
TRIGGER_WEIGHT=0.3          # Explicit trigger match importance
RELATED_SKILL_WEIGHT=0.1    # Related skill bonus
```

Example: Emphasize trigger matches over embeddings:
```bash
# Original: 60% similarity, 30% triggers
# Custom: 40% similarity, 50% triggers (for precise matching)
SIMILARITY_WEIGHT=0.4
TRIGGER_WEIGHT=0.5
```

**Level 3: Custom Filtering**

You can add filters for specific contexts:

```javascript
// In skill-router-api/route.js
function customFilter(skill, context) {
  // Example: Exclude trading skills if user is not a trader
  if (context.userRole !== 'trader' && skill.domain === 'trading') {
    return false;  // Filter out
  }
  return true;  // Include
}
```

**Level 4: Custom Ranking Functions**

Replace the default LLM ranker with custom logic:

```javascript
// Example: Rank by domain first, then confidence
function customRank(candidates, task) {
  return candidates.sort((a, b) => {
    // Priority 1: Domain match
    const domainScore = (a.domain === taskDomain ? 1 : 0) -
                        (b.domain === taskDomain ? 1 : 0);
    if (domainScore !== 0) return domainScore;
    
    // Priority 2: Confidence
    return b.confidence - a.confidence;
  });
}
```

**Level 5: Custom Embedding Models**

The router supports any OpenAI-compatible embedding service:

```bash
# Use Ollama instead of OpenAI
EMBEDDING_PROVIDER=openai \
OPENAI_API_BASE=http://localhost:11434/v1 \
npm start

# Use local llama.cpp
EMBEDDING_PROVIDER=llamacpp \
LLAMACPP_URL=http://localhost:8080 \
npm start
```

**Level 6: Custom Vector Database**

The router uses in-memory cosine similarity by default. You can swap it:

```javascript
// Example: Use Pinecone for vector storage
import Pinecone from '@pinecone-database/pinecone';

const pinecone = new Pinecone({
  apiKey: process.env.PINECONE_API_KEY
});

// Replace in-memory search
async function searchSkills(taskEmbedding) {
  return pinecone.index('skills').query({
    vector: taskEmbedding,
    topK: 20
  });
}
```

**Level 7: Custom Task Preprocessing**

Add custom preprocessing before matching:

```javascript
// Example: Extract intent before routing
import { extractIntent } from './intent-extractor.js';

async function routeTask(task) {
  // Custom preprocessing
  const intent = extractIntent(task);
  const domain = inferDomain(task);
  
  // Route with enhanced context
  const candidates = await searchSkills(task, {
    intent,
    domain,
    userLevel: 'advanced'
  });
  
  return rank(candidates);
}
```

**Practical Extension Example: Domain-Specific Routing**

```javascript
// skill-router-api/custom.js

// Only route to trading skills for trading questions
export function isDomainLocked(userContext) {
  return userContext.domain === 'trading';
}

export function customRoute(candidates, userContext) {
  if (isDomainLocked(userContext)) {
    // Filter to trading domain only
    return candidates.filter(s => s.domain === 'trading');
  }
  return candidates;
}
```

**Extending via Environment Variables:**

```bash
# Router respects these custom variables
CUSTOM_FILTER_ENABLED=true
CUSTOM_RANKING_FUNCTION=domain_first
TRIGGER_WEIGHT_OVERRIDE=0.6
EXCLUDE_DOMAINS=agent,programming  # For specific use cases
ENFORCE_ROLE=implementation         # Only load implementation skills
```

**For Most Users:**

Custom extensions aren't necessary. Improving triggers (Level 1) solves 95% of problems. Only go to Level 2+ if you have specific requirements like:
- Domain-specific routing (traders vs engineers)
- Custom organization hierarchies
- Integration with specialized embeddings
- Performance optimization (custom vector DB)

---

## Section 9: Troubleshooting

### Q24: The README is showing old skill information. How do I refresh it?

**Quick fix:**
```bash
python3 scripts/generate_readme.py
```

This regenerates the skill catalog in README.md.

**What it does:**
1. Scans all skills in `skills/` directory
2. Extracts metadata from SKILL.md frontmatter
3. Regenerates tables between `<!-- AUTO-GENERATED ... -->` markers
4. Preserves everything outside those markers

**If README still shows old data:**

1. **Check if index is stale**
   ```bash
   python3 scripts/generate_index.py
   # Then regenerate README
   python3 scripts/generate_readme.py
   ```

2. **Verify skill metadata is valid**
   ```bash
   python3 scripts/reformat_skills.py
   # Checks YAML syntax and fills missing fields
   ```

3. **Force regeneration without cache**
   ```bash
   rm -f .cache/*  # Clear any caches
   python3 scripts/generate_readme.py
   ```

4. **Check if skill is in index**
   ```bash
   python3 -c "import json; \
   idx = json.load(open('skills-index.json')); \
   skill_names = [s['name'] for s in idx['skills']]; \
   print(f'Total: {len(skill_names)}'); \
   print('your-skill-name' in skill_names)"
   ```

---

### Q25: A skill appears in the directory but not in skills-index.json

**Diagnosis:**
```bash
ls -la skills/your-skill-name/SKILL.md  # Does file exist?
python3 scripts/generate_index.py       # Regenerate
python3 scripts/reformat_skills.py      # Check YAML
```

**Common causes:**

1. **YAML syntax error** → Skill is skipped
   ```bash
   python3 scripts/reformat_skills.py
   # Look for your skill name in error output
   ```

2. **Missing required frontmatter fields**
   - `name` field (must match directory name)
   - `description` field
   - `metadata.triggers` field
   - Solution: Add missing fields

3. **Index hasn't been regenerated**
   ```bash
   python3 scripts/generate_index.py
   # Then verify
   grep "your-skill-name" skills-index.json
   ```

4. **Name field doesn't match directory**
   ```yaml
   # Directory: skills/my-skill/
   # But frontmatter says:
   name: my_skill      # ❌ Wrong!
   
   # Fix:
   name: my-skill      # ✅ Correct
   ```

**Full fix:**
```bash
# 1. Fix YAML
nano skills/your-skill-name/SKILL.md

# 2. Validate
python3 scripts/reformat_skills.py

# 3. Regenerate index
python3 scripts/generate_index.py

# 4. Verify
python3 -c "import json; \
print(json.load(open('skills-index.json'))['totalSkills'])"
```

---

### Q26: Skill triggers aren't matching my natural language query

**Diagnosis:**
```bash
# 1. Check what triggers exist
python3 -c "import json; \
idx = json.load(open('skills-index.json')); \
s = [x for x in idx['skills'] if x['name'] == 'your-skill'][0]; \
print('Triggers:', s['metadata']['triggers'])"

# 2. Test routing with your query
curl -X POST http://localhost:3000/route \
  -H "Content-Type: application/json" \
  -d '{"task":"your natural language query"}'

# 3. Check confidence scores
# Anything < 0.70 won't be selected
```

**Solutions:**

1. **Triggers are too specific**
   - Current: `kubernetes-deployment-strategy`
   - Better: `kubernetes, k8s, deploying apps, how do i deploy`
   - Add more conversational variants

2. **Missing abbreviations**
   - If skill is about PostgreSQL but only has `postgresql` as trigger
   - Add: `postgres, pg, relational database`

3. **Missing "how do I..." variant**
   - If skill solves a task but no "how do I..." trigger
   - Add: `how do i [task]`
   - Example: `how do i deploy apps`, `how do i manage containers`

4. **Trigger too generic (false positives)**
   - Current: `stop, loss, risk`
   - Better: `stop loss, trailing stop, position protection`
   - Be more specific to avoid matching irrelevant tasks

**Fix triggers:**
```bash
# 1. Edit SKILL.md
nano skills/your-skill/SKILL.md

# 2. Update metadata.triggers
metadata:
  triggers: trigger1, trigger2, trigger3, ...

# 3. Regenerate index
python3 scripts/generate_index.py

# 4. Force router reload (optional)
curl -X POST http://localhost:3000/reload

# 5. Test again
curl -X POST http://localhost:3000/route \
  -H "Content-Type: application/json" \
  -d '{"task":"your query"}'
```

---

## Section 10: Questions & Community

### Q27: Where can I ask questions about the skill-router?

**Primary channels:**

1. **GitHub Issues** — Bug reports and feature requests
   ```
   https://github.com/paulpas/agent-skill-router/issues
   ```

2. **GitHub Discussions** — Q&A and community help
   ```
   https://github.com/paulpas/agent-skill-router/discussions
   ```

3. **This FAQ** — Check if your question is already answered (Q1-Q27)

4. **Documentation files:**
   - `AGENTS.md` — Skill creation guide
   - `SKILL_FORMAT_SPEC.md` — Format specification
   - `README.md` — Quick start and overview

**How to ask good questions:**

1. **Check existing issues first** — Your question might already be answered
2. **Provide context** — What you're trying to do, what you expected, what happened
3. **Include reproduction steps** — How can someone reproduce your problem?
4. **Share relevant logs** — Output from `generate_index.py`, router errors, etc.
5. **Be specific** — "Routing isn't working" (vague) vs "Query 'stop loss' loads trading-vwap-execution instead of trading-risk-stop-loss" (specific)

**Example good issue:**
```
Title: Stop-loss skill not routing for "trailing stop" queries

Description:
I created trading-risk-stop-loss skill with triggers including "trailing stop".
When I ask "How do I use a trailing stop?", the router loads a different skill.

Steps to reproduce:
1. Run: curl -X POST http://localhost:3000/route -d '{"task":"How do I use a trailing stop?"}'
2. Check response—trading-vwap-execution loads instead of trading-risk-stop-loss

Expected: trading-risk-stop-loss (confidence > 0.80)
Actual: trading-vwap-execution (confidence 0.92)

Logs:
[full curl response output here]

Skill file: skills/trading-risk-stop-loss/SKILL.md
Triggers: stop loss, trailing stop, ATR stop, ...
```

This is easy for maintainers to debug.

---

## FAQ Index

**Section 1: Why MCP is Better**
- [Q1: Why use MCP instead of loading all skills?](#q1-why-should-i-use-the-mcp-skill-router-instead-of-just-loading-all-skillmd-files-directly)
- [Q2: Performance benefits](#q2-what-are-the-performance-benefits-of-using-mcp-skill-router)
- [Q3: Handling 387 skills](#q3-how-does-the-skill-router-handle-387-skills-without-blowing-up-the-context-window)
- [Q4: Why not load everything at once?](#q4-can-i-just-load-all-skills-at-once-why-shouldnt-i)

**Section 2: How the Router Works**
- [Q5: Auto-routing workflow](#q5-how-does-skill-auto-routing-work)
- [Q6: What are triggers?](#q6-what-are-triggers-and-why-are-they-important)
- [Q7: Manual skill loading](#q7-can-i-manually-request-a-skill-without-relying-on-auto-routing)
- [Q8: Multiple skill matches](#q8-what-happens-if-the-router-matches-multiple-skills-to-my-task)

**Section 3: Skill Management**
- [Q9: Adding new skills](#q9-how-do-i-add-a-new-skill-to-the-repository)
- [Q10: Domains, roles, and triggers](#q10-what-is-the-relationship-between-skill-domains-roles-and-triggers)
- [Q11: Updating existing skills](#q11-how-do-i-update-an-existing-skill-without-recreating-it)
- [Q12: generate_readme.py](#q12-what-happens-when-i-run-generate_readmepy)

**Section 4: Skill Quality**
- [Q13: Quality standards](#q13-what-quality-standards-do-skills-need-to-meet)
- [Q14: Testing skills](#q14-how-are-skills-tested-before-being-added-to-the-repository)
- [Q15: Good vs bad triggers](#q15-what-makes-a-good-trigger-vs-a-bad-trigger)
- [Q16: Related skills](#q16-how-are-related-skills-determined-and-linked)

**Section 5: OpenCode Integration**
- [Q17: Integration architecture](#q17-how-does-the-skill-router-integrate-with-opencode)
- [Q18: OpenCode restarts](#q18-do-i-need-to-restart-opencode-when-skills-are-updated)
- [Q19: Offline mode](#q19-can-the-skill-router-run-offline)

**Section 6: Comparison & Context**
- [Q20: Troubleshooting routing](#q20-how-do-i-troubleshoot-when-a-skill-isnt-being-auto-routed)

**Section 7: Best Practices**
- [Q21: Workflow for creating skills](#q21-whats-the-recommended-workflow-for-creating-skills)
- [Q22: Specific vs general skills](#q22-should-i-create-many-specific-skills-or-fewer-general-skills)

**Section 8: Advanced Topics**
- [Q23: Custom matching logic](#q23-can-i-extend-the-skill-router-with-custom-matching-logic)

**Section 9: Troubleshooting**
- [Q24: Refreshing README](#q24-the-readme-is-showing-old-skill-information-how-do-i-refresh-it)
- [Q25: Skills not in index](#q25-a-skill-appears-in-the-directory-but-not-in-skills-indexjson)
- [Q26: Triggers not matching](#q26-skill-triggers-arent-matching-my-natural-language-query)

**Section 10: Community**
- [Q27: Where to ask questions](#q27-where-can-i-ask-questions-about-the-skill-router)

---

**Last Updated:** 2026-04-24  
**Total Skills:** 387  
**Document Version:** 1.0.0
