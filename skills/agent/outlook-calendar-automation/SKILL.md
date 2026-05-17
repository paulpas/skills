---
compatibility: opencode
completeness: 95
content-types:
- guidance
- examples
- do-dont
description: Implements intelligent outlook calendar automation with multi-factor skill selection, fallback chains, and adherence
  to the 5 Laws of Elegant Defense
license: MIT
maturity: stable
metadata:
  domain: agent
  output-format: analysis
  related-skills: agent-confidence-based-selector, agent-task-routing
  role: orchestration
  scope: orchestration
  triggers: outlook-calendar-automation, outlook calendar automation, how do i outlook-calendar-automation, orchestrate outlook-calendar-automation,
    automate outlook-calendar-automation, agent outlook-calendar-automation
  version: 1.0.0
name: outlook-calendar-automation
---
# Outlook Calendar Automation

Orchestrates intelligent skill selection and execution for outlook calendar automation workflows. Applies the 5 Laws of Elegant Defense to guide data naturally through the orchestration pipeline, preventing errors before they occur. Selects optimal skills based on multi-factor scoring including text similarity, historical performance, and system availability.

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
def prepare_calendar_event(
    user_email: str,
    request_params: Dict[str, Any],
    available_slots: List[Dict]
) -> Dict[str, Any]:
    """Prepare and validate an Outlook calendar event before execution.
    
    Handles timezone normalization, conflict detection, and attendee validation
    using Microsoft Graph API patterns. Implements early validation and
    immutable data structures per Elegant Defense principles.
    
    Args:
        user_email: Primary organizer email
        request_params: Parsed request with subject, start, end, attendees
        available_slots: Pre-fetched free/busy slots from Graph API
        
    Returns:
        Validated event payload ready for Graph API submission
    """
    # Guard clause - Early Exit (Law 1)
    if not user_email or not request_params.get("subject"):
        raise ValueError("Missing required organizer email or event subject")
        
    # Parse & normalize inputs - Make Illegal States Unrepresentable (Law 2)
    start_dt = _parse_iso_datetime(request_params["start"])
    end_dt = _parse_iso_datetime(request_params["end"])
    if end_dt <= start_dt:
        raise ValueError("Event end time must be after start time")
        
    # Validate against free/busy data (Domain Logic)
    conflicts = _check_graph_free_busy(user_email, start_dt, end_dt, available_slots)
    if conflicts:
        return {
            "status": "conflict_detected",
            "conflicting_events": conflicts,
            "suggested_alternatives": _find_alternative_slots(available_slots, start_dt, end_dt)
        }
        
    # Validate attendees via Graph API directory lookup
    validated_attendees = []
    for attendee in request_params.get("attendees", []):
        if not _validate_graph_user(attendee):
            raise ValueError(f"Invalid attendee email: {attendee}")
        validated_attendees.append({"email": attendee, "type": "required"})
        
    # Atomic Predictability (Law 3) - Return new dict, never mutate inputs
    event_payload = {
        "subject": request_params["subject"],
        "body": {"contentType": "HTML", "content": request_params.get("body", "")},
        "start": {"dateTime": start_dt.isoformat(), "timeZone": request_params.get("timezone", "UTC")},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": request_params.get("timezone", "UTC")},
        "attendees": validated_attendees,
        "allowNewTimeProposals": True,
        "responseRequested": True
    }
    return event_payload
```


### Pattern 2: Execution with Fallback

```python
def execute_calendar_operation(
    event_payload: Dict[str, Any],
    graph_client: Any,
    fallback_strategy: str = "suggest_alternatives"
) -> Dict[str, Any]:
    """Execute Outlook calendar event creation/update with domain-specific fallbacks.
    
    Implements resilient Graph API calls with automatic conflict resolution,
    retry logic for transient network errors, and graceful degradation.
    
    Args:
        event_payload: Validated event dictionary from prepare_calendar_event
        graph_client: Authenticated Microsoft Graph SDK client
        fallback_strategy: How to handle conflicts (suggest_alternatives, defer_human, etc.)
        
    Returns:
        Execution result with event ID, status, and fallback metadata
    """
    # Guard clause - validate client state (Early Exit)
    if not graph_client or not graph_client.api_version:
        raise RuntimeError("Graph client not initialized or invalid")
        
    max_retries = 3
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Domain-specific Graph API call
            response = graph_client.me.events.post(event_payload)
            
            # Atomic Predictability (Law 3) - Return immutable result structure
            return {
                "success": True,
                "event_id": response.id,
                "status": "created",
                "attendee_responses": [],
                "attempts": attempt + 1,
                "latency_ms": _measure_execution_time()
            }
            
        except GraphAPIError as e:
            last_error = e
            # Fail Fast - Don't retry on invalid state (Law 4)
            if e.status_code in (400, 403, 404):
                raise CalendarOperationError(f"Permanent Graph API error: {e.message}") from e
                
            # Transient error - exponential backoff retry
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
                
    # All retries exhausted - Apply domain fallback (Law 4)
    if fallback_strategy == "suggest_alternatives":
        return {
            "success": False,
            "fallback_applied": True,
            "reason": "graph_api_unavailable",
            "next_steps": "trigger_alternative_time_slot_search",
            "original_payload": event_payload
        }
    elif fallback_strategy == "defer_human":
        return {
            "success": False,
            "fallback_applied": True,
            "reason": "requires_manual_review",
            "next_steps": "escalate_to_human_organizer",
            "original_payload": event_payload
        }
        
    raise CalendarOperationError(f"Calendar operation failed after {max_retries} attempts: {last_error}")
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
