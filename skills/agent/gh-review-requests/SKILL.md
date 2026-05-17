---
compatibility: opencode
completeness: 95
content-types:
- guidance
- examples
- do-dont
description: Implements intelligent gh review requests with multi-factor skill selection, fallback chains, and adherence to
  the 5 Laws of Elegant Defense
license: MIT
maturity: stable
metadata:
  domain: agent
  output-format: analysis
  related-skills: agent-confidence-based-selector, agent-task-routing
  role: orchestration
  scope: orchestration
  triggers: gh-review-requests, gh review requests, how do i gh-review-requests, orchestrate gh-review-requests, automate
    gh-review-requests, agent gh-review-requests
  version: 1.0.0
name: gh-review-requests
---
# Gh Review Requests

Orchestrates intelligent skill selection and execution for gh review requests workflows. Applies the 5 Laws of Elegant Defense to guide data naturally through the orchestration pipeline, preventing errors before they occur. Selects optimal skills based on multi-factor scoring including text similarity, historical performance, and system availability.

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
def route_review_request(pr_url: str, config: Dict) -> Dict:
    """Route a GitHub review request by validating PR state and determining reviewers.
    
    Extracts repository, owner, and PR number from the URL. Validates against
    GitHub's API to ensure the PR is open and ready for reviews. Applies
    CODEOWNERS rules and team membership checks to build a reviewer list.
    """
    # Guard clause - Early Exit (Law 1)
    if not pr_url or not pr_url.startswith("https://github.com/"):
        raise ValueError("Invalid GitHub PR URL format")
    
    # Parse input - Make Illegal States Unrepresentable (Law 2)
    parts = pr_url.strip("/").split("/")
    if len(parts) < 5:
        raise ValueError("PR URL missing owner/repo/number components")
        
    owner, repo, pr_number = parts[3], parts[4], parts[5]
    
    # Validate PR state via GitHub API
    pr_data = _fetch_pr_metadata(owner, repo, pr_number)
    if pr_data.get("state") != "open":
        raise ValueError(f"PR #{pr_number} is not open (state: {pr_data.get('state')})")
        
    # Determine reviewers based on CODEOWNERS and config
    reviewers = _resolve_reviewers(owner, repo, pr_data.get("files", []), config)
    
    # Atomic Predictability (Law 3) - Return new dict
    return {
        "owner": owner,
        "repo": repo,
        "pr_number": int(pr_number),
        "reviewers": reviewers,
        "status": "ready_for_review",
        "timestamp": time.time()
    }
```


### Pattern 2: Execution with Fallback

```python
def execute_review_request(route_data: Dict, auth_token: str) -> Dict:
    """Execute the GitHub review request with resilience patterns.
    
    Sends review requests via GitHub REST API. Implements exponential backoff
    for rate limits and falls back to CLI-based requests if API fails.
    """
    headers = {"Authorization": f"token {auth_token}", "Accept": "application/vnd.github.v3+json"}
    url = f"https://api.github.com/repos/{route_data['owner']}/{route_data['repo']}/pulls/{route_data['pr_number']}/requested_reviewers"
    
    payload = {"reviewers": route_data["reviewers"]}
    
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 201:
                return {
                    "success": True,
                    "requested_reviewers": route_data["reviewers"],
                    "api_response": response.json(),
                    "attempts": attempt + 1
                }
            elif response.status_code == 403 and "rate limit" in response.text.lower():
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue
            else:
                raise GitHubAPIError(f"Request failed: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            if attempt == 2:
                return _fallback_to_cli_request(route_data, auth_token)
            time.sleep(1)
            
    raise GitHubAPIError("Exhausted all retry attempts for review request")
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
