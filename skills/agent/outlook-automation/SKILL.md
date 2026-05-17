---
compatibility: opencode
completeness: 95
content-types:
- guidance
- examples
- do-dont
description: Implements intelligent outlook automation with multi-factor skill selection, fallback chains, and adherence to
  the 5 Laws of Elegant Defense
license: MIT
maturity: stable
metadata:
  domain: agent
  output-format: analysis
  related-skills: agent-confidence-based-selector, agent-task-routing
  role: orchestration
  scope: orchestration
  triggers: outlook-automation, outlook automation, how do i outlook-automation, orchestrate outlook-automation, automate
    outlook-automation, agent outlook-automation
  version: 1.0.0
name: outlook-automation
---
# Outlook Automation

Orchestrates intelligent skill selection and execution for outlook automation workflows. Applies the 5 Laws of Elegant Defense to guide data naturally through the orchestration pipeline, preventing errors before they occur. Selects optimal skills based on multi-factor scoring including text similarity, historical performance, and system availability.

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
def route_outlook_intent(
    user_request: str,
    available_outlook_modules: List[Dict],
    graph_token: str
) -> Dict:
    """Route Outlook automation requests to specific Microsoft Graph API endpoints.
    
    Analyzes natural language requests to determine if the user wants to:
    - Search/Read emails (/me/messages)
    - Create/Update calendar events (/me/events)
    - Manage inbox rules (/me/mailFolders/inbox/messageRules)
    - Send emails (/me/sendMail)
    
    Args:
        user_request: Natural language instruction for Outlook
        available_outlook_modules: List of configured Outlook skill modules
        graph_token: Valid Microsoft Graph OAuth2 access token
        
    Returns:
        Routing decision with target endpoint, required scopes, and confidence
    """
    import re
    from datetime import datetime

    # Normalize request for intent matching
    normalized = user_request.lower().strip()
    
    # Intent detection patterns for Outlook automation
    intent_map = {
        "email_search": r"(search|find|look up|query).*email|message|inbox",
        "calendar_create": r"(create|schedule|book|add).*event|meeting|calendar",
        "rule_management": r"(create|delete|modify|manage).*rule|filter|auto|forward",
        "send_email": r"(send|reply|forward|draft).*email|message"
    }
    
    matched_intent = None
    for intent, pattern in intent_map.items():
        if re.search(pattern, normalized):
            matched_intent = intent
            break
            
    if not matched_intent:
        return {"status": "unrecognized", "confidence": 0.0, "fallback": "human_review"}
        
    # Match to available module
    target_module = None
    for module in available_outlook_modules:
        if module["intent"] == matched_intent:
            target_module = module
            break
            
    if not target_module:
        return {"status": "module_missing", "confidence": 0.0, "fallback": "module_install"}
        
    # Validate Graph API permissions
    required_scopes = target_module.get("required_scopes", [])
    valid_scopes = _validate_graph_scopes(graph_token, required_scopes)
    
    return {
        "status": "routed",
        "intent": matched_intent,
        "target_module": target_module["name"],
        "graph_endpoint": target_module["endpoint"],
        "confidence": 0.92,
        "timestamp": datetime.utcnow().isoformat()
    }
```


### Pattern 2: Execution with Fallback

```python
def execute_outlook_task(
    target_module: Dict,
    task_params: Dict,
    graph_token: str,
    max_retries: int = 2
) -> Dict:
    """Execute Outlook automation via Microsoft Graph API with resilience patterns.
    
    Handles rate limiting (429), token expiration (401), and transient network errors.
    Implements fallback chain: retry -> switch endpoint region -> queue for manual review.
    
    Args:
        target_module: Routed module configuration with endpoint and scopes
        task_params: Parsed parameters for the Graph API call
        graph_token: Active Microsoft Graph OAuth2 token
        max_retries: Maximum retry attempts for transient failures
        
    Returns:
        Execution result with Graph API response, timing, and status
    """
    import time
    import requests
    from datetime import datetime

    headers = {
        "Authorization": f"Bearer {graph_token}",
        "Content-Type": "application/json",
        "Prefer": "outlook.timezone=\"UTC\""
    }
    
    endpoint = target_module["endpoint"]
    payload = task_params.get("payload", {})
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(
                f"https://graph.microsoft.com/v1.0/{endpoint}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Handle Graph API rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                time.sleep(retry_after)
                continue
                
            # Handle token expiration
            if response.status_code == 401:
                return {"status": "token_expired", "fallback": "refresh_token"}
                
            response.raise_for_status()
            
            return {
                "status": "success",
                "graph_response": response.json(),
                "endpoint_used": endpoint,
                "latency_ms": response.elapsed.total_seconds() * 1000,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except requests.exceptions.Timeout:
            if attempt == max_retries:
                return {"status": "timeout", "fallback": "queue_manual_review"}
            time.sleep(2 ** attempt)
        except requests.exceptions.RequestException as e:
            return {"status": "network_error", "error": str(e), "fallback": "retry"}
            
    return {"status": "exhausted", "fallback": "human_operator"}
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
