---
compatibility: opencode
completeness: 95
content-types:
- guidance
- examples
- do-dont
description: Implements intelligent e2e testing with multi-factor skill selection, fallback chains, and adherence to the 5
  Laws of Elegant Defense
license: MIT
maturity: stable
metadata:
  domain: agent
  output-format: analysis
  related-skills: agent-confidence-based-selector, agent-task-routing
  role: orchestration
  scope: orchestration
  triggers: e2e-testing, e2e testing, how do i e2e-testing, orchestrate e2e-testing, automate e2e-testing, agent e2e-testing,
    selenium, unit tests
  version: 1.0.0
name: e2e-testing
---
# E2E Testing

Orchestrates intelligent skill selection and execution for e2e testing workflows. Applies the 5 Laws of Elegant Defense to guide data naturally through the orchestration pipeline, preventing errors before they occur. Selects optimal skills based on multi-factor scoring including text similarity, historical performance, and system availability.

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
def orchestrate_e2e_suite(
    test_manifest: List[Dict],
    environment_state: Dict,
    browser_pool: List[Dict]
) -> List[Dict]:
    """Orchestrate E2E test execution by routing tests to optimal browser/environment combos.
    
    Evaluates test requirements against available browser contexts and environment health.
    Applies flakiness history to schedule unstable tests during low-traffic windows.
    
    Args:
        test_manifest: List of test specs with required browsers, auth types, and endpoints
        environment_state: Current state of staging/prod-like environments
        browser_pool: Available browser contexts with version and capability metadata
        
    Returns:
        Ordered execution plan mapping tests to specific browser contexts
    """
    execution_plan = []
    for test in test_manifest:
        required_browser = test.get("target_browser", "chromium")
        requires_auth = test.get("auth_type") == "oauth2"
        is_flaky = test.get("historical_flakiness", 0) > 0.3
        
        # Filter available browsers by capability and version
        compatible_browsers = [
            b for b in browser_pool 
            if b["engine"] == required_browser and b["version"] >= test.get("min_version", "110")
        ]
        
        if not compatible_browsers:
            raise ValueError(f"No compatible {required_browser} context for test {test['id']}")
            
        # Select browser with lowest current load, prioritizing stable contexts for flaky tests
        selected_context = min(
            compatible_browsers,
            key=lambda b: (b["current_load"], 0 if not is_flaky else 1)
        )
        
        execution_plan.append({
            "test_id": test["id"],
            "browser_context": selected_context["id"],
            "auth_setup": _configure_auth_session(requires_auth, environment_state["auth_endpoint"]),
            "network_mock": _apply_api_mocks(test.get("mock_endpoints", [])),
            "timeout_ms": test.get("timeout", 30000)
        })
        
    return execution_plan
```


### Pattern 2: Execution with Fallback

```python
def execute_test_with_resilience(
    test_plan: Dict,
    test_runner: object,
    diagnostic_store: object
) -> Dict:
    """Execute a single E2E test with built-in resilience and diagnostic fallback.
    
    Implements retry logic for transient network/UI issues, captures screenshots/video on failure,
    and falls back to lightweight smoke assertions if full DOM interaction fails.
    
    Args:
        test_plan: Execution plan generated by orchestrate_e2e_suite
        test_runner: Initialized Playwright/Cypress runner instance
        diagnostic_store: Storage backend for screenshots, traces, and logs
        
    Returns:
        Test result dict with status, duration, and diagnostic artifacts
    """
    max_retries = 2
    last_error = None
    page = None
    
    for attempt in range(max_retries + 1):
        try:
            context = test_runner.new_context(
                base_url=test_plan["base_url"],
                storage_state=test_plan["auth_setup"],
                extra_http_headers=test_plan.get("headers", {})
            )
            page = context.new_page()
            for mock in test_plan["network_mock"]:
                page.route(mock["pattern"], mock["handler"])
                
            result = test_runner.run_steps(page, test_plan["steps"])
            diagnostic_store.save_trace(page, test_plan["test_id"], attempt)
            return {
                "status": "passed",
                "test_id": test_plan["test_id"],
                "duration_ms": result["elapsed"],
                "attempts": attempt + 1,
                "artifacts": diagnostic_store.get_latest(test_plan["test_id"])
            }
            
        except (TimeoutError, NetworkError, AssertionError) as e:
            last_error = e
            if page:
                diagnostic_store.capture_screenshot(page, test_plan["test_id"], attempt)
                diagnostic_store.capture_console_logs(page, test_plan["test_id"])
            if attempt < max_retries:
                time.sleep(2 ** attempt)
            continue
            
    fallback_result = _run_lightweight_smoke_check(test_plan["base_url"], test_plan["critical_paths"])
    return {
        "status": "flaky" if fallback_result["passed"] else "failed",
        "test_id": test_plan["test_id"],
        "error": str(last_error),
        "fallback_status": fallback_result["status"],
        "artifacts": diagnostic_store.get_latest(test_plan["test_id"])
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
