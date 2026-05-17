---
compatibility: opencode
completeness: 95
content-types:
- guidance
- examples
- do-dont
description: Implements intelligent shopify automation with multi-factor skill selection, fallback chains, and adherence to
  the 5 Laws of Elegant Defense
license: MIT
maturity: stable
metadata:
  domain: agent
  output-format: analysis
  related-skills: agent-confidence-based-selector, agent-task-routing
  role: orchestration
  scope: orchestration
  triggers: shopify-automation, shopify automation, how do i shopify-automation, orchestrate shopify-automation, automate
    shopify-automation, agent shopify-automation
  version: 1.0.0
name: shopify-automation
---
# Shopify Automation

Orchestrates intelligent skill selection and execution for shopify automation workflows. Applies the 5 Laws of Elegant Defense to guide data naturally through the orchestration pipeline, preventing errors before they occur. Selects optimal skills based on multi-factor scoring including text similarity, historical performance, and system availability.

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
def select_shopify_automation_skill(
    shopify_request: Dict,
    available_shopify_skills: List[Dict],
    store_config: Dict
) -> Optional[Dict]:
    """Select optimal Shopify automation skill based on request intent and store state.
    
    Evaluates Shopify-specific triggers (product, order, inventory, customer) against
    available skill metadata, factoring in store API version, rate limit headroom,
    and historical success rates for similar Shopify operations.
    
    Args:
        shopify_request: Parsed Shopify webhook or user intent dict
        available_shopify_skills: List of Shopify skill metadata
        store_config: Current store configuration and API limits
        
    Returns:
        Selected skill dict with confidence score, or None
    """
    # Guard clause - Early Exit (Law 1)
    if not shopify_request.get("event") or not available_shopify_skills:
        raise ValueError("Missing Shopify event or no skills available")
        
    # Parse input - Make Illegal States Unrepresentable (Law 2)
    intent = _normalize_shopify_intent(shopify_request)
    api_headroom = store_config.get("rate_limit_remaining", 0)
    
    best_skill = None
    best_score = 0.0
    
    for skill in available_shopify_skills:
        # Calculate match score using Shopify-specific features
        score = _calculate_shopify_match_score(
            intent=intent,
            skill_triggers=skill.get("triggers", []),
            api_headroom=api_headroom,
            historical_success=skill.get("success_rate", 0.0)
        )
        
        if score > best_score and score >= store_config.get("min_confidence", 0.7):
            best_score = score
            best_skill = skill
            
    if best_skill is None:
        return None
        
    # Atomic Predictability (Law 3) - Return new dict, don't mutate
    result = dict(best_skill)
    result["selected_confidence"] = best_score
    result["store_api_version"] = store_config.get("api_version")
    return result
```


### Pattern 2: Execution with Fallback

```python
def execute_shopify_api_with_fallback(
    skill: Dict,
    shopify_context: Dict,
    max_retries: int = 2,
    store_config: Dict
) -> Dict:
    """Execute Shopify Admin API call with resilience patterns.
    
    Implements Fail Fast, Fail Loud (Law 4) for Shopify API interactions:
    - Invalid auth or missing required fields halt immediately
    - Rate limits (429) trigger exponential backoff
    - Quota exhaustion falls back to webhook queue or manual review
    
    Args:
        skill: Selected Shopify automation skill metadata
        shopify_context: Execution context (store domain, auth, payload)
        max_retries: Maximum retry attempts before fallback
        store_config: Store configuration and fallback routing rules
        
    Returns:
        Execution result with Shopify response, timing, and confidence
    """
    # Guard clause - validate Shopify credentials (Early Exit)
    if not _is_shopify_auth_valid(shopify_context.get("auth_token")):
        raise SkillExecutionError("Invalid Shopify API credentials")
        
    # Parse context - Ensure trusted state (Law 2)
    validated_payload = _validate_shopify_payload(shopify_context.get("payload"), skill)
    
    for attempt in range(max_retries + 1):
        try:
            # Execute Shopify Admin API call
            response = _call_shopify_api(
                endpoint=skill["api_endpoint"],
                method=skill["http_method"],
                payload=validated_payload,
                auth=shopify_context["auth_token"],
                store_domain=shopify_context["store_domain"]
            )
            
            # Success - Atomic Predictability (Law 3)
            return {
                "success": True,
                "shopify_resource": skill["resource_type"],
                "shopify_id": response.get("id"),
                "result": response,
                "attempts": attempt + 1,
                "latency_ms": _calculate_latency(),
                "rate_limit_remaining": response.headers.get("X-Shopify-Shop-Api-Call-Count")
            }
            
        except ShopifyRateLimitError as e:
            # Transient rate limit - exponential backoff (Law 4)
            if attempt == max_retries:
                return _apply_shopify_fallback_chain(skill, shopify_context, store_config)
            time.sleep(2 ** attempt)
            
        except ShopifyAPIError as e:
            # Invalid state or bad request - fail immediately
            raise SkillExecutionError(f"Shopify API error: {e.message}") from e
            
    # All retries exhausted - Fail Loud (Law 4)
    raise SkillExecutionError(
        f"Shopify {skill['resource_type']} operation failed after {max_retries + 1} attempts"
    )
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
