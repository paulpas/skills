#!/usr/bin/env python3
"""
Agent Skill Enrichment Template Generator

This script generates comprehensive SKILL.md files for Agent domain skills
following the agent-skill-router format specifications and best practices.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional


def generate_frontmatter(
    name: str,
    description: str,
    topic: str,
    triggers: str,
    related_skills: str = "",
) -> str:
    """Generate YAML frontmatter for an Agent skill."""
    return f"""---
name: {name}
description: {description}
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: agent
  triggers: {triggers}
  role: orchestration
  scope: orchestration
  output-format: analysis
  related-skills: {related_skills}
---"""


def generate_ascii_flow_diagram() -> str:
    """Generate a generic orchestration flow diagram."""
    return """
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
└─────────────────────────────────────────────────────────────────────┘"""


def generate_code_example_1(topic: str) -> str:
    """Generate a skill selection function."""
    code = """def select_skill(
    task_description: str,
    available_skills: List[Dict],
    min_confidence: float = 0.7
) -> Optional[Dict]:
    \"\"\"Select the most appropriate skill for a given task.
    
    Uses a multi-factor scoring algorithm that considers:
    - Text similarity between task and skill triggers
    - Historical success rate for similar tasks
    - Current system load and skill availability
    
    Args:
        task_description: Natural language description of the task
        available_skills: List of skill metadata dictionaries
        min_confidence: Minimum confidence threshold (0.0-1.0)
        
    Returns:
        Selected skill dictionary or None if no match meets threshold
        
    Raises:
        ValueError: If task_description is empty or available_skills is empty
    \"\"\"
    # Guard clause - Early Exit (Law 1)
    if not task_description or not task_description.strip():
        raise ValueError("Task description cannot be empty")
        
    if not available_skills:
        raise ValueError("No skills available for selection")
    
    # Parse input - Make Illegal States Unrepresentable (Law 2)
    task_features = _extract_task_features(task_description)
    
    best_skill = None
    best_score = 0.0
    
    for skill in available_skills:
        score = _calculate_skill_score(task_features, skill)
        
        if score > best_score and score >= min_confidence:
            best_score = score
            best_skill = skill
    
    if best_skill is None:
        return None
    
    # Atomic Predictability (Law 3) - Return new dict, don't mutate
    result = dict(best_skill)
    result["selected_confidence"] = best_score
    result["selection_timestamp"] = time.time()
    return result"""
    return code


def generate_code_example_2(topic: str) -> str:
    """Generate an execution wrapper with error handling."""
    code = """def execute_with_fallback(
    skill: Dict,
    task_context: Dict,
    max_retries: int = 2
) -> Dict:
    \"\"\"Execute a skill with fallback chain for resilience.
    
    Implements the Fail Fast, Fail Loud principle (Law 4):
    - Invalid states halt immediately with descriptive errors
    - No silent failures or partial results
    
    Fallback chain:
    1. Retry with original parameters
    2. Retry with adjusted parameters (if applicable)
    3. Try alternative skill from related skills list
    4. Defer to human operator (for critical tasks)
    
    Args:
        skill: Selected skill metadata
        task_context: Execution context including inputs
        max_retries: Maximum retry attempts before fallback
        
    Returns:
        Execution result with metadata (success, timing, confidence)
        
    Raises:
        SkillExecutionError: If all retries and fallbacks exhausted
    \"\"\"
    # Guard clause - validate skill (Early Exit)
    if not _is_skill_valid(skill):
        raise SkillExecutionError(f"Invalid skill: {skill.get('name', 'unknown')}")
    
    # Parse context - Ensure trusted state (Law 2)
    validated_context = _validate_and_parse_context(task_context, skill)
    
    for attempt in range(max_retries + 1):
        try:
            result = _execute_skill_direct(skill, validated_context)
            
            # Success - Atomic Predictability (Law 3)
            return {
                "success": True,
                "skill_executed": skill["name"],
                "result": result,
                "attempts": attempt + 1,
                "latency_ms": _calculate_latency()
            }
            
        except InvalidStateError as e:
            # Fail Fast - Don't try to patch bad data (Law 4)
            raise SkillExecutionError(
                f"Invalid state in {skill['name']}: {str(e)}"
            ) from e
            
        except TransientError as e:
            # Transient error - try fallback
            if attempt == max_retries:
                return _apply_fallback_chain(skill, validated_context)
    
    # All retries exhausted - Fail Loud (Law 4)
    raise SkillExecutionError(
        f"Failed to execute {skill['name']} after {max_retries + 1} attempts"
    )"""
    return code


def generate_core_workflow(topic: str) -> str:
    """Generate core workflow with specific steps."""
    return f"""## Core Workflow

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
   
   **Checkpoint:** Record outcome with timing and confidence metadata."""


def generate_when_to_use(topic: str) -> str:
    """Generate When to Use section."""
    return f"""## When to Use

Use this skill when:

- Orchestrating multi-step workflows that require skill delegation
- Implementing adaptive skill routing based on confidence scores
- Building fallback mechanisms for failed skill executions
- Creating intelligent task decomposition and parallel execution
- Designing skill dependency graphs with automatic resolution
- Implementing skill selection with historical performance weighting
- Building agent systems that need to self-organize around tasks"""


def generate_when_not_to_use(topic: str) -> str:
    """Generate When NOT to Use section."""
    return """## When NOT to Use

Avoid this skill for:

- Direct task execution without orchestration needs - use individual skills instead
- High-frequency trading scenarios where latency must be minimized - the selection overhead may be prohibitive
- Simple linear workflows without branching or fallback requirements
- Cases where skill metadata is unavailable or unreliable
"""


def generate_constraints(topic: str) -> str:
    """Generate Constraints section."""
    return """### MUST DO
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
| `agent-confidence-based-selector` | Alternative confidence-based routing approach"""  # noqa: E501


def generate_skill_content(
    topic: str,
    title: str,
    description: str,
    triggers: str,
    related_skills: str = "",
) -> str:
    """Generate complete SKILL.md content for an Agent skill."""
    name = topic  # Matches directory name

    # Build the complete content
    frontmatter = generate_frontmatter(
        name, description, topic, triggers, related_skills
    )

    role_paragraph = (
        f"Orchestrates intelligent skill selection and execution for {topic.replace('-', ' ')} workflows. "
        "Applies the 5 Laws of Elegant Defense to guide data naturally through the orchestration pipeline, preventing errors before they occur. "
        "Selects optimal skills based on multi-factor scoring including text similarity, historical performance, and system availability."
    )

    content = "\n\n".join(
        [
            frontmatter,
            f"# {title}",
            role_paragraph,
            "## TL;DR Checklist",
            "- [ ] Parse all inputs at boundary before processing (Law 2)\n"
            "- [ ] Handle edge cases with early returns at function top (Law 1)\n"
            "- [ ] Fail immediately with descriptive errors on invalid states (Law 4)\n"
            "- [ ] Return new data structures, never mutate inputs (Law 3)\n"
            "- [ ] Implement minimum 2-level fallback chain for all skill executions\n"
            "- [ ] Log all skill selections with context for full audit trail\n"
            "- [ ] Validate skill metadata and dependencies before selection\n"
            "- [ ] Update confidence scores after each execution for learning",
            generate_ascii_flow_diagram(),
            generate_when_to_use(topic),
            generate_when_not_to_use(topic),
            generate_core_workflow(topic),
            generate_implementation_patterns(topic),
            generate_constraints(topic),
        ]
    )

    return content


def generate_implementation_patterns(topic: str) -> str:
    """Generate Implementation Patterns section."""
    pattern1 = generate_code_example_1(topic)
    pattern2 = generate_code_example_2(topic)
    return f"""## Implementation Patterns

### Pattern 1: Skill Selection Logic

```python
{pattern1}
```


### Pattern 2: Execution with Fallback

```python
{pattern2}
```"""  # noqa: E501


def create_skill_directory(base_path: str, topic: str) -> Path:
    """Create the skill directory structure."""
    path = Path(base_path) / "skills" / "agent" / topic
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_skill_file(skill_path: Path, content: str) -> None:
    """Write the SKILL.md file."""
    file_path = skill_path / "SKILL.md"
    with open(file_path, "w") as f:
        f.write(content)
    print(f"Created: {file_path} ({len(content)} bytes)")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 enrich_agent_skill.py <topic>")
        print("Example: python3 enrich_agent_skill.py task-routing")
        sys.exit(1)

    topic = sys.argv[1]

    # Generate skill content
    title = topic.replace("-", " ").title()

    # Build description
    description_map = {
        "task-routing": "Selects and delegates tasks to the most appropriate skills based on confidence scoring and relevance metrics for intelligent orchestration",
        "confidence-selection": "Chooses optimal execution paths based on confidence scores, historical performance, and system availability for adaptive routing",
        "parallel-execution": "Coordinates concurrent skill execution with dependency management and conflict resolution for optimized workflow performance",
        "fallback-routing": "Implements multi-level fallback chains with retry logic and human intervention escalation for resilient skill execution",
    }

    base_description = description_map.get(
        topic,
        f"Orchestrates intelligent {topic.replace('-', ' ')} with confidence-based routing and resilience",
    )
    description = f"Implements {topic.replace('-', ' ')} with multi-factor skill selection, fallback chains, and adherence to the 5 Laws of Elegant Defense"

    # Build triggers
    trigger_map = {
        "task-routing": "task routing, skill routing, agent dispatch, orchestration, how do i automate this, workflow automation, task delegation",
        "confidence-selection": "confidence scoring, skill selection, adaptive selection, routing logic, task routing, agent dispatch, confidence-based",
        "parallel-execution": "parallel execution, concurrent tasks, workflow orchestration, how do i run tasks in parallel, agent coordination, async execution",
        "fallback-routing": "fallback routing, error handling, retry logic, graceful degradation, human intervention, escalation path, resilience",
    }

    triggers = trigger_map.get(
        topic,
        f"{topic}, orchestration, agent routing, how do i {topic.replace('-', ' ')}",
    )

    # Build related skills
    related_map = {
        "task-routing": "agent-confidence-based-selector, agent-dynamic-replanner, agent-parallel-skill-runner",
        "confidence-selection": "agent-task-routing, agent-dependency-graph-builder, agent-dynamic-replanner",
        "parallel-execution": "agent-task-decomposer, agent-dependency-graph-builder, agent-task-routing",
        "fallback-routing": "agent-confidence-based-selector, agent-parallel-skill-runner, agent-dynamic-replanner",
    }

    related_skills = related_map.get(
        topic,
        "agent-task-routing, agent-confidence-based-selector, agent-dynamic-replanner",
    )

    content = generate_skill_content(
        topic, title, description, triggers, related_skills
    )

    # Create directory and write file
    skill_path = create_skill_directory("/home/paulpas/git/agent-skill-router", topic)
    write_skill_file(skill_path, content)

    # Verify size
    file_size = len(content)
    if file_size < 3000:
        print(f"WARNING: File size is {file_size} bytes (should be >= 3000)")
    else:
        print(f"File size: {file_size} bytes (OK)")


if __name__ == "__main__":
    main()
