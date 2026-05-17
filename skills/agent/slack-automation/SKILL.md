---
compatibility: opencode
completeness: 95
content-types:
- guidance
- examples
- do-dont
description: Implements intelligent slack automation with multi-factor skill selection, fallback chains, and adherence to
  the 5 Laws of Elegant Defense
license: MIT
maturity: stable
metadata:
  domain: agent
  output-format: analysis
  related-skills: agent-confidence-based-selector, agent-task-routing
  role: orchestration
  scope: orchestration
  triggers: slack-automation, slack automation, how do i slack-automation, orchestrate slack-automation, automate slack-automation,
    agent slack-automation
  version: 1.0.0
name: slack-automation
---
# Slack Automation

Orchestrates intelligent skill selection and execution for slack automation workflows. Applies the 5 Laws of Elegant Defense to guide data naturally through the orchestration pipeline, preventing errors before they occur. Selects optimal skills based on multi-factor scoring including text similarity, historical performance, and system availability.

## TL;DR Checklist

- [ ] Parse all inputs at boundary before processing (Law 2)
- [ ] Handle edge cases with early returns at function top (Law 1)
- [ ] Fail immediately with descriptive errors on invalid states (Law 4)
- [ ] Return new data structures, never mutate inputs (Law 3)
- [ ] Implement minimum 2-level fallback chain for all skill executions
- [ ] Log all skill selections with context for full audit trail
- [ ] Validate skill metadata and dependencies before selection
- [ ] Update confidence scores after each execution for learning


┌───────────────────────────────────────────────────────────────────────────────┐
│                              Orchestration Flow                                               │
└───────────────────────────────────────────────────────────────────────────────┘

  User Request
      ↓
┌─────────────────┐
│  Parse Request  │
│  & Extract      │
│  Features       │
└────────┬────────┘
         ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    Evaluate Available Skills                                │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Skill A      │  │ Skill B      │  │ Skill C      │              │
│  │ - Match Score│  │ - Match Score│  │ - Match Score│              │
│  │ - Confidence │  │ - Confidence │  │ - Confidence │              │
│  │ - History    │  │ - History    │  │ - History    │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                       │
│         └─────────────────┴─────────────────┘                       │
│                          ↓                                          │
│                   Select Best Skill                               │
└─────────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────┐
│  Execute Skill  │
└────────┬────────┘
         ↓
┌─────────────────┐
│  Handle Result  │
└────────┬────────┘
         ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    Error Handling & Fallback                                  │
│                                                                     │
│  Success? ────────► Return Result                                  │
│                                                                     │
│  Fail? ────────┐                                                    │
│                ↓                                                    │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │               Fallback Chain                                    │      │
│  │                                                             │      │
│  │  1. Retry with adjusted parameters                          │      │
│  │  2. Try Alternative Skill (if available)                    │      │
│  │  3. Defer to Human Operator (if critical)                   │      │
│  │  4. Log & Return Error                                      │      │
│  └──────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘

## When to Use

Use this skill when:

- Orchestrating multi-step workflows that require skill delegation
- Implementing adaptive skill routing based on confidence scores
- Building fallback mechanisms for failed skill executions
- Creating intelligent task decomposition and parallel execution
- Designing skill dependency graphs with automatic resolution
- Implementing skill selection with historical performance weighting
- Building agent systems that need to self-organize around tasks

## When NOT to Use

Avoid this skill for:

- Direct task execution without orchestration needs - use individual skills instead
- High-frequency trading scenarios where latency must be minimized - the selection overhead may be prohibitive
- Simple linear workflows without branching or fallback requirements
- Cases where skill metadata is unavailable or unreliable


## Core Workflow

1. **Parse and Analyze Request** - Extract intent, entities, and constraints from user input.
   **Checkpoint:** All required parameters must be present and in valid format before proceeding.

2. **Score Available Skills** - Calculate match scores using multi-factor algorithm:
   - Text similarity between request and skill triggers
   - Historical success rate for similar tasks
   - Skill availability and health status
   - Required dependencies and their availability
   
   **Checkpoint:** Skip to fallback if no skill scores above threshold.

3. **Select Optimal Skill** - Choose skill with highest score that meets minimum confidence.
   **Checkpoint:** Verify skill has not been disabled or deprecated.

4. **Execute with Fallback** - Run skill execution wrapped in retry and fallback logic.
   **Checkpoint:** Log all execution attempts for audit trail.

5. **Return or Fallback** - Either return successful result or apply fallback chain:
   - Retry with adjusted parameters
   - Try alternative skill from `related-skills`
   - Defer to human operator for critical tasks
   
   **Checkpoint:** Record outcome with timing and confidence metadata.

## Implementation Patterns

### Pattern 1: Skill Selection Logic

```python
from slack_sdk import WebClient
from typing import Dict, List, Optional
import time

def select_slack_action(
    user_intent: str,
    channel_context: Dict,
    available_actions: List[Dict]
) -> Optional[Dict]:
    """Select optimal Slack API action based on intent and channel state.
    
    Applies multi-factor scoring: intent match, channel type compatibility,
    historical success rate, and current rate limit headroom.
    """
    # Guard clause - Early Exit (Law 1)
    if not user_intent or not channel_context.get("channel_id"):
        raise ValueError("Missing intent or channel context")
        
    best_action = None
    best_score = 0.0
    current_ts = time.time()
    
    for action in available_actions:
        # Calculate match score based on intent keywords and channel type
        intent_match = sum(1 for kw in action.get("triggers", []) if kw in user_intent.lower())
        channel_compat = 1.0 if action.get("channel_type") in channel_context.get("types", []) else 0.0
        rate_limit_headroom = 1.0 if channel_context.get("rate_limit_remaining", 0) > action.get("cost", 1) else 0.0
        
        score = (intent_match * 0.5) + (channel_compat * 0.3) + (rate_limit_headroom * 0.2)
        
        if score > best_score and score >= 0.6:
            best_score = score
            best_action = action
            
    if best_action is None:
        return None
    
    # Atomic Predictability (Law 3) - Return new dict, don't mutate
    return {
        "action": best_action["name"],
        "confidence": best_score,
        "selected_at": current_ts,
        "params": dict(best_action.get("default_params", {}))
    }
```


### Pattern 2: Execution with Fallback

```python
from slack_sdk.errors import SlackApiError

def execute_slack_operation(
    action: Dict,
    client: WebClient,
    context: Dict,
    max_retries: int = 2
) -> Dict:
    """Execute Slack API operation with resilience and fallback chain.
    
    Implements Fail Fast/Loud: validates channel state, handles rate limits,
    and falls back to alternative actions or human escalation.
    """
    channel_id = context.get("channel_id")
    if not channel_id:
        raise ValueError("Execution requires valid channel_id")
        
    for attempt in range(max_retries + 1):
        try:
            # Execute specific Slack API call based on selected action
            if action["action"] == "post_message":
                result = client.chat_postMessage(
                    channel=channel_id,
                    text=context.get("message", ""),
                    thread_ts=context.get("thread_ts"),
                    blocks=context.get("blocks")
                )
            elif action["action"] == "schedule_reminder":
                result = client.reminders_add(
                    text=context.get("reminder_text"),
                    time=context.get("reminder_time"),
                    user_id=context.get("user_id")
                )
            else:
                raise ValueError(f"Unsupported action: {action['action']}")
                
            # Success - Atomic Predictability (Law 3)
            return {
                "success": True,
                "action_executed": action["action"],
                "result": result,
                "attempts": attempt + 1,
                "latency_ms": time.time() - context.get("start_ts", time.time())
            }
            
        except SlackApiError as e:
            if e.response.status_code == 429:
                # Rate limited - wait and retry
                retry_after = int(e.response.headers.get("retry-after", 1))
                time.sleep(retry_after)
                continue
            elif e.response.status_code in (404, 403):
                # Channel archived or permission denied - Fail Fast (Law 4)
                raise SlackApiError(f"Channel access denied or archived: {e.response.status_code}", e.response)
            elif attempt == max_retries:
                # Exhausted retries - apply fallback
                return _apply_slack_fallback(action, context, e)
                
    raise SlackApiError("Max retries exceeded for Slack operation", None)

def _apply_slack_fallback(action: Dict, context: Dict, error: Exception) -> Dict:
    """Fallback chain for Slack operations: alternative action -> human notification"""
    if action.get("fallback_action"):
        return execute_slack_operation(action["fallback_action"], WebClient(token=context["token"]), context, max_retries=0)
    else:
        return {
            "success": False,
            "error": str(error),
            "fallback_triggered": True,
            "requires_human": True
        }
```

### MUST DO
- Always validate skill metadata before selection (Early Exit)
- Implement fallback chain with at least 2 levels (Fallback Skill + Human)
- Log all skill selections with full context for auditability
- Return new data structures instead of mutating inputs (Atomic Predictability)
- Fail immediately with descriptive errors on invalid states
- Update confidence scores after each execution for adaptive routing
- Reference `code-philosophy` (5 Laws of Elegant Defense) in all logic


### MUST NOT DO
- Select skills based on a single factor (e.g., only confidence score)
- Disable fallback mechanisms "temporarily" - this creates fragile systems
- Skip validation of skill dependencies before execution
- Return partial results - either complete success or clear failure
- Use magic numbers for confidence thresholds - make them configurable
- Cache skill selections without considering context changes


## TL;DR Checklist

- [ ] Parse all inputs at boundary before processing (Law 2)
- [ ] Handle edge cases with early returns at function top (Law 1)
- [ ] Fail immediately with descriptive errors on invalid states (Law 4)
- [ ] Return new data structures, never mutate inputs (Law 3)
- [ ] Implement minimum 2-level fallback chain for all skill executions
- [ ] Log all skill selections with context for full audit trail
- [ ] Validate skill metadata and dependencies before selection
- [ ] Update confidence scores after each execution for learning


## TL;DR for Code Generation

- Use guard clauses - return early on invalid input before doing work
- Return simple types (dict, str, int, bool, list) - avoid complex nested objects
- Cyclomatic complexity < 10 per function - split anything larger
- Handle null/empty cases explicitly at function top (Early Exit)
- Never mutate input parameters - return new dicts/objects
- Fail fast with descriptive errors - don't try to "patch" bad data
- Reference code-philosophy laws in comments for complex logic
- Include timing and confidence metadata in all return values


## Output Template

When applying this skill, produce:

1. **Selected Skills** - List of skill names with confidence scores
2. **Selection Rationale** - Why each skill was chosen (match score, history, availability)
3. **Execution Plan** - Order of execution with dependencies
4. **Fallback Strategy** - Which fallback skills will be tried and in what order
5. **Risk Assessment** - Any potential failure points and their impact
6. **Timing Estimates** - Expected latency including fallback scenarios


## Related Skills

| Skill | Purpose |
|---|---|
| `agent-dynamic-replanner` | Replans execution when conditions change |
| `agent-parallel-skill-runner` | Executes independent skills in parallel |
| `agent-dependency-graph-builder` | Builds and resolves skill dependency graphs |
| `agent-task-decomposer` | Breaks complex tasks into delegable subtasks |
| `agent-confidence-based-selector` | Alternative confidence-based routing approach

---

## Constraints

### MUST DO
- Ensure each agent handles a single responsibility
- Include explicit fallback/error routing for every branching point
- Reference code-philosophy (5 Laws of Elegant Defense)

### MUST NOT DO
- Use fixed thresholds without adaptive tuning
- Ignore low-confidence fallback scenarios
- Skip execution history tracking
