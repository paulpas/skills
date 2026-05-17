---
compatibility: opencode
completeness: 95
content-types:
- guidance
- examples
- do-dont
description: Implements intelligent fal audio with multi-factor skill selection, fallback chains, and adherence to the 5 Laws
  of Elegant Defense
license: MIT
maturity: stable
metadata:
  domain: agent
  output-format: analysis
  related-skills: agent-confidence-based-selector, agent-task-routing
  role: orchestration
  scope: orchestration
  triggers: fal-audio, fal audio, how do i fal-audio, orchestrate fal-audio, automate fal-audio, agent fal-audio
  version: 1.0.0
name: fal-audio
---
# Fal Audio

Orchestrates intelligent skill selection and execution for fal audio workflows. Applies the 5 Laws of Elegant Defense to guide data naturally through the orchestration pipeline, preventing errors before they occur. Selects optimal skills based on multi-factor scoring including text similarity, historical performance, and system availability.

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
def configure_audio_generation_task(
    user_prompt: str,
    available_models: List[Dict],
    min_confidence: float = 0.7
) -> Optional[Dict]:
    """Configure optimal audio generation parameters based on prompt analysis.
    
    Analyzes prompt semantics to select the best audio model and parameters:
    - Detects intent (music, voiceover, sfx, ambient)
    - Matches model capabilities to prompt requirements
    - Validates duration and format constraints
    
    Args:
        user_prompt: Natural language audio generation request
        available_models: List of supported audio generation models
        min_confidence: Minimum confidence threshold for model selection
        
    Returns:
        Configured task dictionary with model, parameters, and confidence
    """
    if not user_prompt or not user_prompt.strip():
        raise ValueError("Audio generation prompt cannot be empty")
        
    if not available_models:
        raise ValueError("No audio models available for generation")
    
    # Parse intent and extract constraints (Law 2)
    intent = _detect_audio_intent(user_prompt)
    duration_req = _extract_duration_constraint(user_prompt)
    
    best_config = None
    best_score = 0.0
    
    for model in available_models:
        # Score based on intent match, duration support, and historical success
        intent_match = _calculate_intent_similarity(intent, model["supported_intents"])
        duration_support = 1.0 if model["max_duration"] >= duration_req else 0.5
        history_score = model.get("success_rate", 0.0)
        
        score = (intent_match * 0.5) + (duration_support * 0.3) + (history_score * 0.2)
        
        if score > best_score and score >= min_confidence:
            best_score = score
            best_config = {
                "model_id": model["id"],
                "model_name": model["name"],
                "parameters": {
                    "prompt": user_prompt,
                    "duration": duration_req,
                    "format": model["default_format"],
                    "guidance_scale": model.get("default_guidance", 7.5)
                },
                "selected_confidence": best_score,
                "intent_detected": intent
            }
    
    if best_config is None:
        return None
        
    return best_config
```


### Pattern 2: Execution with Fallback

```python
def execute_audio_generation(
    task_config: Dict,
    api_client: Any,
    max_retries: int = 2
) -> Dict:
    """Execute audio generation with resilient fallback chain.
    
    Implements Fail Fast, Fail Loud (Law 4) for audio pipeline:
    - Validates prompt length and content policy immediately
    - Retries on transient API errors with exponential backoff
    - Falls back to alternative models if primary fails
    - Returns structured result with generation metadata
    
    Args:
        task_config: Configured audio generation task from Pattern 1
        api_client: Initialized Fal.ai or compatible audio API client
        max_retries: Maximum retry attempts before fallback
        
    Returns:
        Execution result with audio URL, duration, and confidence
    """
    if not task_config or "model_id" not in task_config:
        raise ValueError("Invalid task configuration provided")
        
    params = task_config["parameters"]
    
    for attempt in range(max_retries + 1):
        try:
            # Execute generation call
            generation_job = api_client.generate_audio(
                model_id=task_config["model_id"],
                prompt=params["prompt"],
                duration=params["duration"],
                guidance_scale=params["guidance_scale"]
            )
            
            # Wait for completion with timeout
            result = api_client.wait_for_completion(
                job_id=generation_job["id"],
                timeout=120
            )
            
            return {
                "success": True,
                "model_used": task_config["model_id"],
                "audio_url": result["audio_url"],
                "duration_sec": result["duration"],
                "attempts": attempt + 1,
                "confidence": task_config["selected_confidence"],
                "intent": task_config["intent_detected"]
            }
            
        except ContentPolicyError as e:
            # Fail Fast - reject invalid prompts immediately (Law 4)
            raise ValueError(f"Prompt violates content policy: {str(e)}")
            
        except TransientAPIError as e:
            if attempt == max_retries:
                return _fallback_to_alternative_model(task_config, api_client)
                
    raise RuntimeError(f"Audio generation failed after {max_retries + 1} attempts")
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
