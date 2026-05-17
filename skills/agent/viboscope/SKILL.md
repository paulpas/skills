---
compatibility: opencode
completeness: 95
content-types:
- guidance
- examples
- do-dont
description: Implements intelligent viboscope with multi-factor skill selection, fallback chains, and adherence to the 5 Laws
  of Elegant Defense
license: MIT
maturity: stable
metadata:
  domain: agent
  output-format: analysis
  related-skills: agent-confidence-based-selector, agent-task-routing
  role: orchestration
  scope: orchestration
  triggers: viboscope, viboscope, how do i viboscope, orchestrate viboscope, automate viboscope, agent viboscope
  version: 1.0.0
name: viboscope
---
# Viboscope

Orchestrates intelligent skill selection and execution for viboscope workflows. Applies the 5 Laws of Elegant Defense to guide data naturally through the orchestration pipeline, preventing errors before they occur. Selects optimal skills based on multi-factor scoring including text similarity, historical performance, and system availability.

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
def viboscope_select_module(
    signal_metadata: Dict[str, Any],
    available_modules: List[Dict],
    calibration_threshold: float = 0.85
) -> Optional[Dict]:
    """Select optimal viboscope processing module based on signal characteristics.
    
    Evaluates modules against raw signal features: frequency range, amplitude variance,
    and sensor calibration status. Applies multi-factor scoring to route signals
    through the most accurate processing pipeline.
    
    Args:
        signal_metadata: Parsed signal features (freq_range_hz, amplitude_std, sensor_id)
        available_modules: List of viboscope module configs with capabilities
        calibration_threshold: Minimum calibration match required for selection
        
    Returns:
        Selected module dict with routing metadata or None
    """
    # Guard clause - Early Exit (Law 1)
    if not signal_metadata or not available_modules:
        raise ValueError("Signal metadata and module registry required")
        
    best_module = None
    best_score = 0.0
    
    for module in available_modules:
        freq_match = _calculate_frequency_alignment(signal_metadata["freq_range_hz"], module["supported_hz"])
        amp_match = _calculate_amplitude_compatibility(signal_metadata["amplitude_std"], module["dynamic_range"])
        cal_score = _verify_sensor_calibration(signal_metadata["sensor_id"], module["calibrated_sensors"])
        
        composite_score = (freq_match * 0.5) + (amp_match * 0.3) + (cal_score * 0.2)
        
        if composite_score > best_score and cal_score >= calibration_threshold:
            best_score = composite_score
            best_module = module
            
    if best_module is None:
        return None
    
    # Atomic Predictability (Law 3) - Return new dict, don't mutate
    return {
        "module_id": best_module["id"],
        "routing_score": best_score,
        "signal_hash": hashlib.md5(json.dumps(signal_metadata, sort_keys=True).encode()).hexdigest(),
        "timestamp": time.time()
    }
```


### Pattern 2: Execution with Fallback

```python
def viboscope_execute_pipeline(
    selected_module: Dict,
    raw_signal_data: bytes,
    fallback_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute viboscope signal processing pipeline with domain-specific fallbacks.
    
    Runs the selected module against raw vibration data. Implements graceful degradation
    when signal quality drops or hardware latency exceeds thresholds.
    
    Args:
        selected_module: Output from viboscope_select_module
        raw_signal_data: Raw byte stream from vibroscope sensor
        fallback_config: Fallback routing rules and degradation parameters
        
    Returns:
        Processed signal dict with quality metrics and routing history
    """
    pipeline_state = {"attempts": 0, "degradation_level": 0, "module_id": selected_module["module_id"]}
    
    for attempt in range(fallback_config.get("max_retries", 3)):
        pipeline_state["attempts"] += 1
        try:
            # Apply module-specific signal transformation
            processed = _apply_viboscope_transform(raw_signal_data, selected_module["module_id"])
            
            # Validate output integrity
            quality_score = _calculate_signal_to_noise_ratio(processed)
            
            if quality_score >= fallback_config.get("min_quality_threshold", 0.7):
                return {
                    "status": "success",
                    "processed_signal": processed,
                    "quality_score": quality_score,
                    "routing_path": [selected_module["module_id"]],
                    "pipeline_state": pipeline_state
                }
                
            # Signal degraded - trigger adaptive fallback
            raw_signal_data = _apply_noise_filtering(raw_signal_data)
            selected_module = fallback_config["adaptive_modules"][pipeline_state["degradation_level"]]
            pipeline_state["degradation_level"] += 1
            
        except SensorDriftError as e:
            # Hardware drift detected - switch to reference calibration
            raw_signal_data = _apply_reference_calibration(raw_signal_data, fallback_config["reference_sensor"])
            continue
            
        except HardwareTimeoutError:
            if attempt == fallback_config.get("max_retries", 3) - 1:
                raise PipelineExecutionError("Viboscope pipeline exhausted all hardware retries")
            time.sleep(fallback_config.get("backoff_seconds", 0.5))
            
    return {
        "status": "degraded",
        "processed_signal": processed,
        "quality_score": quality_score,
        "routing_path": pipeline_state.get("fallback_chain", []),
        "pipeline_state": pipeline_state
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
