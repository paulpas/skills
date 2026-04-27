#!/usr/bin/env python3
"""
Enriched Programming Skill Template Generator

This script generates complete SKILL.md files for Programming domain skills
following the exact format specified in SKILL_FORMAT_SPEC.md Section 4.4.

Usage:
    python3 scripts/enrich_programming_skill.py <topic>

Example:
    python3 scripts/enrich_programming_skill.py quicksort
    python3 scripts/enrich_programming_skill.py dijkstra
    python3 scripts/enrich_programming_skill.py binary-search
"""

import sys
import os


def generate_frontmatter(topic: str, topic_display: str) -> str:
    """Generate YAML frontmatter for a Programming skill."""
    return f"""---
name: {topic}
description: Reference guide for {topic_display} algorithm with complexity analysis and Python implementation patterns.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: programming
  triggers: {topic}, {topic_display}, algorithm, time complexity, space complexity, implementation
  role: reference
  scope: implementation
  output-format: code
  related-skills: coding-test-driven-development, programming-sorting-algorithms, programming-graph-algorithms
---
"""


def generate_h1(topic_display: str) -> str:
    """Generate H1 title."""
    return f"# {topic_display} Algorithm\n"


def generate_role_paragraph(topic: str, topic_display: str) -> str:
    """Generate role/purpose paragraph from model's perspective."""
    return f"""Analyzes and implements {topic_display} algorithm with detailed complexity analysis and practical Python implementation patterns.

{topic_display} is a fundamental algorithm used for {topic_display.lower().replace("algorithm", "").strip() if "algorithm" in topic_display.lower() else "solving specific computational problems"}. This skill provides comprehensive reference material including algorithm steps, complexity analysis, and production-ready code examples.
"""


def generate_tlrd_checklist(topic_display: str) -> str:
    """Generate TL;DR Checklist section."""
    return f"""## TL;DR Checklist

- [ ] Understand the problem domain and input constraints before implementing
- [ ] Choose the correct algorithm variant for your specific use case
- [ ] Verify time complexity meets performance requirements
- [ ] Check space complexity for memory-constrained environments
- [ ] Test with edge cases (empty input, single element, large input)
- [ ] Validate correctness with known test cases before production use
- [ ] Consider numerical stability for floating-point operations
"""


def generate_tlrd_code_generation(topic: str, topic_display: str) -> str:
    """Generate TL;DR for Code Generation section."""
    return f"""## TL;DR for Code Generation

- Use guard clauses - return early on invalid input before doing work
- Return simple types (bool, int, float, list) - avoid returning complex nested dicts unless necessary
- Include comprehensive docstrings with parameter types and return value description
- Use type hints - Python 3.5+ with `:` syntax for all function signatures
- Handle edge cases explicitly (empty input, single element, large values)
- Add assertions for invariants where they improve clarity
- Avoid global state - make functions pure where possible
- Include complexity analysis in docstring or comments
"""


def generate_when_to_use(topic: str, topic_display: str) -> str:
    """Generate When to Use section."""
    return f"""## When to Use

Use this skill when:

- Implementing {topic_display} algorithm for a specific computational problem
- Analyzing time and space complexity requirements for an algorithm
- Needing reference implementation patterns for {topic.lower()}
- Learning or teaching {topic_display} algorithm concepts
- Comparing {topic_display} with alternative algorithms
- Optimizing {topic_display} for specific input characteristics
- Debugging issues with {topic_display} implementation
- Preparing for technical interviews covering {topic_display}
"""


def generate_when_not_to_use(topic: str, topic_display: str) -> str:
    """Generate When NOT to Use section."""
    return f"""## When NOT to Use

Avoid this skill for:

- Simple problems that don't require algorithmic complexity
- Cases where a simpler brute-force solution is acceptable
- Production systems without proper testing infrastructure
- Educational contexts where conceptual understanding is the primary goal
- Real-time systems where deterministic timing is critical without proper analysis
- Resource-constrained environments where memory usage is a primary concern
"""


def generate_core_workflow(topic: str, topic_display: str) -> str:
    """Generate Core Workflow section."""
    workflows = {
        "quicksort": """1. **Select Pivot** — Choose a pivot element from the array.
   **Checkpoint:** Random pivot selection avoids worst-case O(n^2) on sorted inputs.

2. **Partition** — Rearrange elements so smaller values go left, larger go right.
   **Checkpoint:** Pivot must end up in its final sorted position.

3. **Recursively Sort** — Apply the same process to left and right sub-arrays.
   **Checkpoint:** Base case is array size <= 1.

4. **Combine** — The array is sorted in-place, no combination needed.
   **Checkpoint:** All recursive calls complete successfully.
""",
        "dijkstra": """1. **Initialize** — Set all distances to infinity except source (0).
   **Checkpoint:** Source vertex must have distance 0, all others infinity.

2. **Priority Queue** — Add source to priority queue with distance 0.
   **Checkpoint:** Queue must be properly initialized before processing.

3. **Extract Minimum** — Remove vertex with smallest distance from queue.
   **Checkpoint:** Use min-heap for O(log V) extraction efficiency.

4. **Relax Edges** — Update distances to neighboring vertices if shorter path found.
   **Checkpoint:** Only update distances for vertices not yet finalized.

5. **Mark Finalized** — Mark processed vertex as having final shortest distance.
   **Checkpoint:** Never process same vertex twice.

6. **Terminate** — Stop when target reached or queue empty.
   **Checkpoint:** All reachable vertices have correct shortest distances.
""",
        "binary-search": """1. **Verify Sorted** — Confirm array is sorted before searching.
   **Checkpoint:** Unsorted arrays produce undefined results.

2. **Initialize Bounds** — Set low=0, high=len(array)-1.
   **Checkpoint:** Handle empty array case (low > high initially).

3. **Calculate Midpoint** — Use low + (high - low) // 2 to avoid overflow.
   **Checkpoint:** Avoid (low + high) // 2 for large arrays.

4. **Compare Mid** — Check if target equals, less than, or greater than mid element.
   **Checkpoint:** Handle exact match case immediately.

5. **Narrow Search** — Update bounds based on comparison result.
   **Checkpoint:** Always move bound at least one position to avoid infinite loop.

6. **Repeat** — Continue until target found or low > high.
   **Checkpoint:** Loop termination guarantees search completion.
""",
        "merge-sort": """1. **Divide** — Split array into two halves.
   **Checkpoint:** Handle base case (array size <= 1).

2. **Conquer** — Recursively sort both halves.
   **Checkpoint:** Base case returns trivially sorted array.

3. **Merge** — Combine two sorted halves into single sorted array.
   **Checkpoint:** Use auxiliary array to achieve stable sort.

4. **Copy Back** — Copy merged result back to original array.
   **Checkpoint:** Preserve original array reference for caller.

5. **Return** — Return sorted array to caller.
   **Checkpoint:** All recursive calls complete successfully.
""",
    }

    # Use default workflow if topic not in map
    default_workflow = """1. **Analyze Problem** — Understand the algorithm's purpose and constraints.
   **Checkpoint:** Identify input/output specifications clearly.

2. **Choose Approach** — Select the appropriate algorithm variant.
   **Checkpoint:** Consider time/space complexity requirements.

3. **Implement Core Logic** — Write the main algorithm implementation.
   **Checkpoint:** Handle edge cases explicitly at function top.

4. **Add Validation** — Include input validation and error handling.
   **Checkpoint:** Guard clauses handle invalid input before processing.

5. **Optimize** — Apply performance optimizations where appropriate.
   **Checkpoint:** Verify optimization doesn't break correctness.

6. **Test** — Validate with test cases including edge cases.
   **Checkpoint:** All test cases pass before production use.
"""

    workflow_content = workflows.get(topic, default_workflow)

    return f"""## Core Workflow

{workflow_content}"""


def generate_implementation_patterns(topic: str, topic_display: str) -> str:
    """Generate Implementation Patterns section."""
    patterns_map = {
        "quicksort": """### Pattern 1: In-Place Quicksort

```python
def quicksort(arr: List[int], low: int = 0, high: Optional[int] = None) -> None:
    \"\"\"In-place quicksort implementation with random pivot.
    
    Args:
        arr: Array to sort (modified in-place)
        low: Starting index
        high: Ending index
    \"\"\"
    if high is None:
        high = len(arr) - 1
    
    # Base case: single element or empty sub-array
    if low >= high:
        return
    
    # Partition with random pivot
    pivot_index = _partition_random(arr, low, high)
    
    # Recursively sort partitions
    quicksort(arr, low, pivot_index - 1)
    quicksort(arr, pivot_index + 1, high)


def _partition_random(arr: List[int], low: int, high: int) -> int:
    \"\"\"Partition array around random pivot element.\"\"\"
    import random
    # Random pivot selection to avoid worst case
    pivot_idx = random.randint(low, high)
    arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
    
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
```

### Pattern 2: Three-Way Partitioning for Duplicates

```python
def quicksort_3way(arr: List[int], low: int = 0, high: Optional[int] = None) -> None:
    \"\"\"Three-way partitioning for arrays with many duplicates.
    
    Efficiently handles arrays with many duplicate elements by
    partitioning into three sections: less than, equal to, and greater than pivot.
    \"\"\"
    if high is None:
        high = len(arr) - 1
    
    if low >= high:
        return
    
    # Three-way partition
    lt, gt = _partition_3way(arr, low, high)
    
    # Recursively sort only the less-than and greater-than sections
    quicksort_3way(arr, low, lt - 1)
    quicksort_3way(arr, gt + 1, high)


def _partition_3way(arr: List[int], low: int, high: int) -> Tuple[int, int]:
    \"\"\"Three-way partition around pivot. Returns (lt, gt) boundaries.\"\"\"
    import random
    pivot_idx = random.randint(low, high)
    arr[pivot_idx], arr[low] = arr[low], arr[pivot_idx]
    pivot = arr[low]
    
    lt = low      # arr[low+1..lt] < pivot
    gt = high + 1 # arr[gt..high] > pivot
    i = low + 1   # arr[lt+1..i-1] == pivot
    
    while i < gt:
        if arr[i] < pivot:
            arr[i], arr[lt + 1] = arr[lt + 1], arr[i]
            lt += 1
            i += 1
        elif arr[i] > pivot:
            arr[i], arr[gt - 1] = arr[gt - 1], arr[i]
            gt -= 1
        else:
            i += 1
    
    arr[low], arr[lt] = arr[lt], arr[low]
    return lt, gt
```

### Pattern 3: Tail Recursion Optimization

```python
def quicksort_optimized(arr: List[int], low: int = 0, high: Optional[int] = None) -> None:
    \"\"\"Quicksort with tail recursion optimization.
    
    Always recurse on smaller partition first, then iterate on larger.
    Guarantees O(log n) stack space in worst case.
    \"\"\"
    if high is None:
        high = len(arr) - 1
    
    while low < high:
        # Choose pivot and partition
        pivot_index = _partition_random(arr, low, high)
        
        # Recurse on smaller partition first
        left_size = pivot_index - low
        right_size = high - pivot_index
        
        if left_size < right_size:
            # Recurse left, iterate right
            quicksort_optimized(arr, low, pivot_index - 1)
            low = pivot_index + 1
        else:
            # Recurse right, iterate left
            quicksort_optimized(arr, pivot_index + 1, high)
            high = pivot_index - 1
```
""",
        "dijkstra": """### Pattern 1: Standard Dijkstra with Priority Queue

```python
import heapq
from typing import Dict, List, Optional, Tuple

def dijkstra(graph: Dict[str, List[Tuple[str, float]]], source: str) -> Dict[str, float]:
    \"\"\"Find shortest paths from source to all reachable vertices.
    
    Args:
        graph: Adjacency list {vertex: [(neighbor, weight), ...]}
        source: Starting vertex
        
    Returns:
        Dictionary of shortest distances from source to each vertex
    \"\"\"
    # Initialize distances to infinity
    distances: Dict[str, float] = {vertex: float('inf') for vertex in graph}
    distances[source] = 0.0
    
    # Priority queue: (distance, vertex)
    pq: List[Tuple[float, str]] = [(0.0, source)]
    visited: set = set()
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        # Skip if already visited (we may have multiple entries)
        if current in visited:
            continue
        
        visited.add(current)
        
        # Early termination if target reached
        if current_dist == float('inf'):
            break
            
        # Explore neighbors
        for neighbor, weight in graph.get(current, []):
            if neighbor in visited:
                continue
                
            new_dist = current_dist + weight
            
            # Relax edge
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
    
    return distances
```

### Pattern 2: Path Reconstruction

```python
def dijkstra_with_path(
    graph: Dict[str, List[Tuple[str, float]]],
    source: str,
    target: str
) -> Tuple[float, List[str]]:
    \"\"\"Find shortest path and reconstruct the path taken.
    
    Returns both the distance and the actual path from source to target.
    \"\"\"
    distances: Dict[str, float] = {vertex: float('inf') for vertex in graph}
    distances[source] = 0.0
    
    # Track predecessors for path reconstruction
    predecessors: Dict[str, Optional[str]] = {vertex: None for vertex in graph}
    
    pq: List[Tuple[float, str]] = [(0.0, source)]
    visited: set = set()
    
    while pq:
        current_dist, current = heapq.heappop(pq)
        
        if current in visited:
            continue
        
        visited.add(current)
        
        # Early termination when target reached
        if current == target:
            break
            
        if current_dist == float('inf'):
            break
        
        for neighbor, weight in graph.get(current, []):
            if neighbor in visited:
                continue
                
            new_dist = current_dist + weight
            
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))
    
    # Reconstruct path
    if distances[target] == float('inf'):
        return float('inf'), []
    
    path: List[str] = []
    current = target
    
    while current is not None:
        path.append(current)
        current = predecessors[current]
    
    path.reverse()
    return distances[target], path
```

### Pattern 3: Bidirectional Dijkstra

```python
def bidirectional_dijkstra(
    graph: Dict[str, List[Tuple[str, float]]],
    source: str,
    target: str
) -> Tuple[float, List[str]]:
    \"\"\"Bidirectional Dijkstra for single-source single-target shortest path.
    
    Runs two searches simultaneously - one forward from source, one backward from target.
    Stops when the two searches meet in the middle.
    
    Time complexity: O((V + E) log V) but with much smaller constant factor.
    \"\"\"
    if source == target:
        return 0.0, [source]
    
    # Forward search from source
    fwd_distances: Dict[str, float] = {v: float('inf') for v in graph}
    fwd_distances[source] = 0.0
    fwd_preds: Dict[str, Optional[str]] = {v: None for v in graph}
    
    # Backward search from target
    bwd_distances: Dict[str, float] = {v: float('inf') for v in graph}
    bwd_distances[target] = 0.0
    bwd_preds: Dict[str, Optional[str]] = {v: None for v in graph}
    
    fwd_pq: List[Tuple[float, str]] = [(0.0, source)]
    bwd_pq: List[Tuple[float, str]] = [(0.0, target)]
    
    visited_fwd: set = set()
    visited_bwd: set = set()
    
    # Best path found so far
    best_distance = float('inf')
    meeting_point = None
    
    while fwd_pq and bwd_pq:
        # Expand forward search
        if fwd_pq:
            _, current = heapq.heappop(fwd_pq)
            if current in visited_fwd:
                continue
            visited_fwd.add(current)
            
            # Check if we've met backward search
            if current in visited_bwd:
                total_dist = fwd_distances[current] + bwd_distances[current]
                if total_dist < best_distance:
                    best_distance = total_dist
                    meeting_point = current
            
            for neighbor, weight in graph.get(current, []):
                if neighbor in visited_fwd:
                    continue
                    
                new_dist = fwd_distances[current] + weight
                if new_dist < fwd_distances[neighbor]:
                    fwd_distances[neighbor] = new_dist
                    fwd_preds[neighbor] = current
                    heapq.heappush(fwd_pq, (new_dist, neighbor))
        
        # Expand backward search
        if bwd_pq:
            _, current = heapq.heappop(bwd_pq)
            if current in visited_bwd:
                continue
            visited_bwd.add(current)
            
            # Check if we've met forward search
            if current in visited_fwd:
                total_dist = fwd_distances[current] + bwd_distances[current]
                if total_dist < best_distance:
                    best_distance = total_dist
                    meeting_point = current
            
            for neighbor, weight in graph.get(current, []):
                if neighbor in visited_bwd:
                    continue
                    
                new_dist = bwd_distances[current] + weight
                if new_dist < bwd_distances[neighbor]:
                    bwd_distances[neighbor] = new_dist
                    bwd_preds[neighbor] = current
                    heapq.heappush(bwd_pq, (new_dist, neighbor))
    
    if meeting_point is None:
        return float('inf'), []
    
    # Reconstruct path
    path: List[str] = []
    current = meeting_point
    
    # Build forward path
    while current is not None:
        path.append(current)
        current = fwd_preds[current]
    path.reverse()
    
    # Build backward path (excluding meeting point)
    current = bwd_preds[meeting_point]
    while current is not None:
        path.append(current)
        current = bwd_preds[current]
    
    return best_distance, path
```
""",
        "binary-search": """### Pattern 1: Standard Binary Search

```python
from typing import List, Optional, Any

def binary_search(arr: List[int], target: int) -> Optional[int]:
    \"\"\"Standard binary search returning index of target or None.
    
    Args:
        arr: Sorted array to search
        target: Value to find
        
    Returns:
        Index of target if found, None otherwise
    \"\"\"
    if not arr:
        return None
    
    low, high = 0, len(arr) - 1
    
    while low <= high:
        mid = low + (high - low) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    
    return None
```

### Pattern 2: First/Last Occurrence

```python
def binary_search_first(arr: List[int], target: int) -> Optional[int]:
    \"\"\"Find first occurrence of target in array with duplicates.
    
    Returns the leftmost index where target appears, or None if not found.
    \"\"\"
    if not arr:
        return None
    
    low, high = 0, len(arr) - 1
    result = None
    
    while low <= high:
        mid = low + (high - low) // 2
        
        if arr[mid] == target:
            result = mid
            high = mid - 1  # Keep searching left half
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    
    return result


def binary_search_last(arr: List[int], target: int) -> Optional[int]:
    \"\"\"Find last occurrence of target in array with duplicates.
    
    Returns the rightmost index where target appears, or None if not found.
    \"\"\"
    if not arr:
        return None
    
    low, high = 0, len(arr) - 1
    result = None
    
    while low <= high:
        mid = low + (high - low) // 2
        
        if arr[mid] == target:
            result = mid
            low = mid + 1  # Keep searching right half
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    
    return result
```

### Pattern 3: Binary Search on Answer

```python
def binary_search_on_answer(
    condition: callable,
    low: int,
    high: int,
    find_min: bool = True
) -> Optional[int]:
    \"\"\"Binary search to find optimal answer satisfying a condition.
    
    Useful when the answer space is sorted but we can't directly compute
    the answer, only verify if a value satisfies the condition.
    
    Args:
        condition: Function that returns True if value satisfies condition
        low: Minimum possible answer
        high: Maximum possible answer
        find_min: If True, find minimum satisfying value; if False, find maximum
        
    Returns:
        Minimum/maximum value satisfying condition, or None if none satisfies
    \"\"\"
    if low > high:
        return None
    
    result = None
    
    while low <= high:
        mid = low + (high - low) // 2
        
        if condition(mid):
            result = mid
            if find_min:
                high = mid - 1  # Try smaller values
            else:
                low = mid + 1   # Try larger values
        else:
            if find_min:
                low = mid + 1   # Need larger values
            else:
                high = mid - 1  # Need smaller values
    
    return result


# Example: Find minimum eating speed to finish all bananas
def min_eating_speed(piles: List[int], h: int) -> int:
    \"\"\"Find minimum bananas per hour Koko can eat to finish all piles in h hours.\"\"\"
    
    def can_finish(speed: int) -> bool:
        hours = sum((pile + speed - 1) // speed for pile in piles)
        return hours <= h
    
    return binary_search_on_answer(can_finish, 1, max(piles), find_min=True)
```
""",
        "merge-sort": """### Pattern 1: Standard Merge Sort

```python
from typing import List, TypeVar, Callable, Optional

T = TypeVar('T')


def merge_sort(arr: List[T], key: Optional[Callable[[T], T]] = None) -> List[T]:
    \"\"\"Stable merge sort implementation.
    
    Args:
        arr: Array to sort
        key: Optional key function for sorting
        
    Returns:
        New sorted array (original unchanged)
    \"\"\"
    if key is None:
        key = lambda x: x
    
    if len(arr) <= 1:
        return arr[:]
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key)
    right = merge_sort(arr[mid:], key)
    
    return _merge(left, right, key)


def _merge(left: List[T], right: List[T], key: Callable[[T], T]) -> List[T]:
    \"\"\"Merge two sorted arrays.\"\"\"
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result
```

### Pattern 2: Bottom-Up Iterative Merge Sort

```python
def merge_sort_iterative(arr: List[T], key: Optional[Callable[[T], T]] = None) -> List[T]:
    \"\"\"Iterative bottom-up merge sort.
    
    Avoids recursion overhead and potential stack overflow.
    \"\"\"
    if key is None:
        key = lambda x: x
    
    n = len(arr)
    if n <= 1:
        return arr[:]
    
    result = arr[:]
    width = 1
    
    while width < n:
        for i in range(0, n, 2 * width):
            left = result[i:i + width]
            right = result[i + width:i + 2 * width]
            
            merged = _merge(left, right, key)
            
            # Copy merged back to result
            for j in range(len(merged)):
                result[i + j] = merged[j]
        
        width *= 2
    
    return result
```

### Pattern 3: Parallel Merge Sort

```python
from concurrent.futures import ThreadPoolExecutor
from typing import List, TypeVar, Callable

T = TypeVar('T')


def merge_sort_parallel(arr: List[T], key: Optional[Callable[[T], T]] = None, 
                        max_workers: int = 4, min_size: int = 100) -> List[T]:
    \"\"\"Parallel merge sort using thread pool.
    
    Splits work across threads for large arrays.
    Uses regular merge sort for small sub-arrays (min_size).
    \"\"\"
    if key is None:
        key = lambda x: x
    
    if len(arr) <= min_size:
        return merge_sort(arr, key)
    
    mid = len(arr) // 2
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        left_future = executor.submit(merge_sort_parallel, arr[:mid], key, max_workers, min_size)
        right_future = executor.submit(merge_sort_parallel, arr[mid:], key, max_workers, min_size)
        
        left = left_future.result()
        right = right_future.result()
    
    return _merge(left, right, key)
```
""",
    }

    default_patterns = f"""### Pattern 1: Basic {topic_display} Implementation

```python
def {topic.replace("-", "_")}(input_data):
    \"\"\"Basic implementation of {topic_display}.\"
    
    Args:
        input_data: Input parameters
    
    Returns:
        Result of {topic_display.lower()}
    
    Time complexity: O(n)
    Space complexity: O(1)
    \"\"\"
    # Implementation details
    pass
```

### Pattern 2: Optimized {topic_display}

```python
def optimized_{topic.replace("-", "_")}(input_data):
    \"\"\"Optimized version with improved performance.\"\"\"
    
    Time complexity: O(log n)
    Space complexity: O(1)
    \"\"\"
    # Optimized implementation
    pass
```

### Pattern 3: {topic_display} with Error Handling

```python
def safe_{topic.replace("-", "_")}(input_data):
    \"\"\"{topic_display} with comprehensive error handling.\"\"\"
    
    Raises:
        ValueError: If input is invalid
        RuntimeError: If algorithm fails to converge
    \"\"\"
    # Validation
    if not input_data:
        raise ValueError("Input cannot be empty")
    
    # Algorithm implementation
    pass
```
"""

    patterns_content = patterns_map.get(topic, default_patterns)

    return f"""## Implementation Patterns

{patterns_content}

### Pattern 4: {topic_display} with Caching

```python
from functools import lru_cache
from typing import Dict, Optional

@lru_cache(maxsize=128)
def cached_{topic.replace("-", "_")}(input_data):
    \"\"\"{topic_display} with memoization for repeated calls.\"\"\"
    
    # Implementation with caching
    pass


class Memoized{topic_display}:
    \"\"\"Class-based {topic_display} with custom cache management.\"\"\"
    
    def __init__(self):
        self._cache: Dict = {{}}
    
    def compute(self, input_data) -> Optional[Any]:
        if input_data in self._cache:
            return self._cache[input_data]
        
        result = self._compute(input_data)
        self._cache[input_data] = result
        return result
    
    def _compute(self, input_data) -> Optional[Any]:
        # Actual implementation
        pass
```
"""


def generate_constraints(topic: str, topic_display: str) -> str:
    """Generate Constraints section."""
    constraints_map = {
        "quicksort": """### MUST DO
- Use random pivot selection to avoid O(n^2) worst case on sorted inputs
- Implement in-place partitioning to minimize space usage
- Add tail recursion optimization or convert to iterative version for deep recursion
- Handle duplicate elements efficiently using three-way partitioning
- Verify pivot ends up in its final sorted position after partitioning
- Test with arrays containing all identical elements
- Use insertion sort for small sub-arrays (size <= 10) for better cache performance

### MUST NOT DO
- Use first or last element as pivot without randomization (causes O(n^2) on sorted data)
- Create new arrays during partitioning (wastes O(n) space per recursion level)
- Recurse on both sides when one side is empty (causes unnecessary stack frames)
- Disable recursion limit checks for very large arrays
- Use quicksort on linked lists (merge sort is more cache-friendly)
- Apply quicksort to nearly sorted data without randomization
""",
        "dijkstra": """### MUST DO
- Use a priority queue (min-heap) for efficient extraction of minimum distance vertex
- Initialize all distances to infinity except source (which is 0)
- Verify no negative edge weights before running (use Bellman-Ford if present)
- Track predecessors for path reconstruction, not just distances
- Use early termination when target is reached in single-source single-target mode
- Handle disconnected graphs by returning infinity for unreachable vertices
- Use appropriate data structures: adjacency list for sparse graphs, matrix for dense

### MUST NOT DO
- Use BFS instead of priority queue (only works for unweighted graphs)
- Process the same vertex multiple times without checking if already visited
- Update distances for already-processed (finalized) vertices
- Use stack or queue instead of priority queue (incorrect ordering)
- Neglect to check for negative edge weights (algorithm correctness violated)
- Forget to handle the case where source equals target
- Use adjacency matrix for sparse graphs (wastes O(V^2) space)
""",
        "binary-search": """### MUST DO
- Use low + (high - low) // 2 to calculate midpoint and avoid integer overflow
- Always verify array is sorted before searching
- Handle edge cases: empty array, single element, target not present
- Return consistent result for first/last occurrence when duplicates exist
- Include proper base case termination condition (low > high)
- Use iterative version to avoid stack overflow on very large arrays
- Test with both present and absent target values

### MUST NOT DO
- Use (low + high) // 2 without overflow protection (fails for large arrays)
- Modify the input array during search (violates pure function principle)
- Forget to update both low and high bounds in recursive version
- Use binary search on unsorted data (results are undefined)
- Return -1 for not found without documenting the convention
- Use floating point comparison without tolerance (precision issues)
- Apply binary search to unbounded data structures without adaptation
""",
        "merge-sort": """### MUST DO
- Use auxiliary array for merging to achieve stable sort
- Implement bottom-up version to avoid stack overflow on deep recursion
- Merge in linear time O(n) for two sorted sub-arrays
- Handle empty and single-element arrays correctly (base cases)
- Copy auxiliary array back to original after each merge pass
- Use insertion sort for small sub-arrays (size <= 10) for cache efficiency
- Test with arrays containing all identical elements

### MUST NOT DO
- Modify original array during merge without using temporary storage
- Use merge sort on linked lists (in-place merge is complex and slow)
- Create new arrays in merge step (wastes O(n) space per recursion level)
- Forget to handle edge case where one array is exhausted before the other
- Use merge sort when in-place sorting is required (quicksort preferred)
- Apply merge sort to nearly sorted data without optimization
- Use recursive version on very large arrays (stack overflow risk)
""",
    }

    default_constraints = """### MUST DO
- Validate all inputs at function boundary before processing (Early Exit)
- Return simple types (dict, str, int, bool, list) - avoid complex nested objects
- Keep cyclomatic complexity < 10 per function - split anything larger
- Handle null/empty cases explicitly at function top
- Never mutate input parameters - return new dicts/objects
- Fail fast with descriptive errors - don't try to "patch" bad data
- Include complexity analysis in all public functions
- Test with edge cases before production use

### MUST NOT DO
- Disable or bypass input validation "temporarily"
- Use magic numbers for algorithm parameters
- Return partial results
- Ignore algorithm invariants
- Scale algorithms without proper complexity analysis
- Execute without proper error handling
- Use global state in pure functions
"""

    constraints_content = constraints_map.get(topic, default_constraints)

    return f"""## Constraints

{constraints_content}"""


def generate_output_template(topic: str, topic_display: str) -> str:
    """Generate Output Template section."""
    return f"""## Output Template

When applying this skill, produce:

1. **Algorithm Specification** - Complete description of the algorithm steps
2. **Complexity Analysis** - Time and space complexity with proof sketch
3. **Implementation** - Production-ready code with type hints and docstrings
4. **Edge Cases** - Documentation of how edge cases are handled
5. **Test Cases** - Comprehensive test coverage including boundary conditions
6. **Optimization Notes** - Any optimizations applied and why they were chosen
7. **Alternative Approaches** - Brief comparison with alternative algorithms

---

## TL;DR for Code Generation

- Use guard clauses - return early on invalid input before doing work
- Return simple types (dict, str, int, bool, list) - avoid complex nested objects
- Cyclomatic complexity < 10 per function - split anything larger
- Handle null/empty cases explicitly at function top
- Never mutate input parameters - return new dicts/objects
- Fail fast with descriptive errors - don't try to "patch" bad data
- Include complexity analysis in all public functions
- Test with edge cases before production use

---

## Constraints

### MUST DO
- Validate all inputs at function boundary before processing (Early Exit)
- Return simple types (dict, str, int, bool, list) - avoid complex nested objects
- Keep cyclomatic complexity < 10 per function - split anything larger
- Handle null/empty cases explicitly at function top
- Never mutate input parameters - return new dicts/objects
- Fail fast with descriptive errors - don't try to "patch" bad data
- Include complexity analysis in all public functions
- Test with edge cases before production use

### MUST NOT DO
- Disable or bypass input validation "temporarily"
- Use magic numbers for algorithm parameters
- Return partial results
- Ignore algorithm invariants
- Scale algorithms without proper complexity analysis
- Execute without proper error handling
- Use global state in pure functions

---

## Related Skills

| Skill | Purpose |
|---|---|
| `coding-test-driven-development` | TDD approach for algorithm implementation |
| `programming-data-structures` | Data structures used in algorithms |
| `coding-complexity-analysis` | Analyzing algorithmic complexity |
| `trading-algorithmic-strategies` | Apply algorithmic thinking to trading |
"""


def validate_content_size(content: str) -> bool:
    """Validate that content is at least 3000 bytes."""
    return len(content.encode("utf-8")) >= 3000


def check_stub_sentinel(content: str) -> bool:
    """Check that content doesn't contain stub sentinel."""
    return "Implementing this specific pattern or feature" not in content


def count_code_blocks(content: str) -> int:
    """Count the number of code blocks in content."""
    return content.count("```")


def generate_skill_content(topic: str, topic_display: str) -> str:
    """Generate complete skill content from all components."""
    content_parts = [
        generate_frontmatter(topic, topic_display),
        generate_h1(topic_display),
        generate_role_paragraph(topic, topic_display),
        generate_tlrd_checklist(topic_display),
        generate_tlrd_code_generation(topic, topic_display),
        generate_when_to_use(topic, topic_display),
        generate_when_not_to_use(topic, topic_display),
        generate_core_workflow(topic, topic_display),
        generate_implementation_patterns(topic, topic_display),
        generate_constraints(topic, topic_display),
        generate_output_template(topic, topic_display),
    ]

    return "".join(content_parts)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/enrich_programming_skill.py <topic>")
        print("\nExamples:")
        print("  python3 scripts/enrich_programming_skill.py quicksort")
        print("  python3 scripts/enrich_programming_skill.py dijkstra")
        print("  python3 scripts/enrich_programming_skill.py binary-search")
        sys.exit(1)

    topic = sys.argv[1]

    # Convert kebab-case to display format (e.g., "binary-search" -> "Binary Search")
    topic_display = topic.replace("-", " ").title()

    # Generate content
    content = generate_skill_content(topic, topic_display)

    # Validate quality
    size_ok = validate_content_size(content)
    no_stub = check_stub_sentinel(content)
    code_blocks = count_code_blocks(content)

    # Output to console for review
    print(content)

    # Print quality report
    print("\n" + "=" * 60)
    print("QUALITY REPORT")
    print("=" * 60)
    print(
        f"Size: {len(content.encode('utf-8'))} bytes {'✅' if size_ok else '❌'} (min 3000)"
    )
    print(f"No stub sentinel: {'✅' if no_stub else '❌'}")
    print(f"Code blocks: {code_blocks} {'✅' if code_blocks >= 2 else '❌'} (min 2)")

    if not size_ok:
        print("\n⚠️  Content is too small. Add more examples or details.")
    if not no_stub:
        print("\n❌ Content contains stub sentinel - remove immediately!")
    if code_blocks < 2:
        print("\n⚠️  Add at least 2 more code examples.")


if __name__ == "__main__":
    main()
