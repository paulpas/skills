---
name: testing
description: Implements comprehensive test strategies including unit, integration, and end-to-end tests with best practices for test design, mocking, and coverage.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  triggers: unit testing, integration testing, TDD, test automation, mocking, test coverage, pytest
  role: implementation
  scope: implementation
  output-format: code
  related-skills: coding-code-review, coding-test-driven-development
---

# Code Quality Specialist

Implements comprehensive code quality practices including review, testing, refactoring, security, and architectural patterns.

## TL;DR Checklist

- [ ] Follow Arrange-Act-Assert (AAA) pattern for test structure
- [ ] Use descriptive test names that specify scenario, context, and expected behavior
- [ ] Mock external dependencies (APIs, databases) to ensure test isolation
- [ ] Test both happy paths and edge cases/error conditions
- [ ] Avoid test interdependencies (tests should run in any order)
- [ ] Keep tests fast (unit tests < 100ms each)
- [ ] Aim for meaningful coverage, not 100% coverage at all costs

---

## When to Use

Use this skill when:

- Implementing new features with comprehensive test coverage
- Refactoring existing code to ensure no behavior changes
- Setting up a new project's test infrastructure
- Improving test coverage in legacy codebases
- Debugging complex issues with systematic test cases
- Implementing continuous integration pipelines
- Validating edge cases and error conditions

---

## When NOT to Use

Avoid this skill for:

- Writing tests for code that will be discarded immediately (prototypes, spikes)
- Testing code with no reliable behavior to verify (random generation without constraints)
- When test infrastructure doesn't exist and setup cost outweighs benefit
- As a replacement for manual QA for complex user workflows
- For code that is purely infrastructure with no logical behavior to test

---

## Core Workflow

1. **Understand Requirements** — Review feature specifications, user stories, or bug reports.
   **Checkpoint:** Clear understanding of expected behavior before writing tests.

2. **Design Test Strategy** — Determine test types (unit, integration, e2e) and scope of coverage needed.
   **Checkpoint:** Test plan covers all requirements and edge cases.

3. **Write Test Skeleton** — Create test file structure with descriptive names and basic test cases.
   **Checkpoint:** Test file follows project conventions and naming patterns.

4. **Implement Test Cases** — Write tests using Arrange-Act-Assert pattern and appropriate mocks.
   **Checkpoint:** Each test verifies a specific behavior and fails when behavior changes.

5. **Run Tests and Verify** — Execute tests and ensure they pass with correct expectations.
   **Checkpoint:** All tests pass and coverage meets minimum thresholds.

6. **Refactor Tests** — Improve test structure and readability while preserving intent.
   **Checkpoint:** Tests remain simple, fast, and maintainable.

7. **Document Test Coverage** — Note what is tested, what isn't, and any limitations.
   **Checkpoint:** Test documentation is updated alongside code changes.

---

## Implementation Patterns

### Pattern 1: Arrange-Act-Assert (AAA) Test Structure

**Use Case:** Writing clear, maintainable unit tests.

```python
import pytest
from typing import List


def get_even_numbers(numbers: List[int]) -> List[int]:
    '''Return only even numbers from a list.'''
    return [n for n in numbers if n % 2 == 0]


# GOOD: Clear Arrange-Act-Assert structure
class GoodTestCase:
    # ✅ GOOD: Arrange-Act-Assert structure is clear
    def test_even_numbers_returns_only_even_values(self):
        # Arrange
        input_numbers = [1, 2, 3, 4, 5, 6]
        expected_result = [2, 4, 6]
        
        # Act
        actual_result = get_even_numbers(input_numbers)
        
        # Assert
        assert actual_result == expected_result


# GOOD: Parameterized tests for multiple cases
class ParameterizedTestCase:
    @pytest.mark.parametrize(
        "input_nums,expected",
        [
            ([], []),
            ([1, 3, 5], []),
            ([2, 4, 6], [2, 4, 6]),
            ([1, 2, 3, 4, 5, 6], [2, 4, 6]),
        ],
    )
    def test_with_multiple_inputs(self, input_nums, expected):
        # Arrange, Act, Assert in compact form for parameterized tests
        assert get_even_numbers(input_nums) == expected
```

**Checkpoint:** All tests follow AAA pattern and have descriptive names.

---

### Pattern 2: Mocking External Dependencies

**Use Case:** Testing code with external dependencies (databases, APIs).

```python
from unittest.mock import Mock, patch
import pytest


def fetch_user_data(user_id: int) -> dict:
    '''Fetch user data from external API.'''
    response = requests.get(f"https://api.example.com/users/{user_id}")
    response.raise_for_status()
    return response.json()


# GOOD: Mock external dependency for reliable tests
class GoodUnitTest:
    @patch("requests.get")
    def test_fetch_user_data_success(self, mock_get):
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {"id": 123, "name": "John Doe"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Act
        result = fetch_user_data(123)
        
        # Assert
        assert result == {"id": 123, "name": "John Doe"}
        mock_get.assert_called_once_with("https://api.example.com/users/123")
    
    @patch("requests.get")
    def test_fetch_user_data_not_found(self, mock_get):
        # Arrange
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(requests.HTTPError):
            fetch_user_data(999)
```

**Checkpoint:** External dependencies are mocked; tests are reliable and fast.

---

### Pattern 3: Test Fixtures for Shared Setup

**Use Case:** Sharing test data and setup across multiple tests.

```python
import pytest
from dataclasses import dataclass
from typing import List


@dataclass
class Order:
    id: int
    items: List[str]
    total: float


@pytest.fixture
def sample_order():
    '''Create a sample order for testing.'''
    return Order(id=1, items=["Widget", "Gadget"], total=99.99)


@pytest.fixture
def empty_order():
    '''Create an empty order for edge case testing.'''
    return Order(id=2, items=[], total=0.0)


# Use fixtures in tests
class TestOrderCalculations:
    def test_order_total_calculation(self, sample_order):
        # Fixture provides pre-configured data
        assert sample_order.total == 99.99
    
    def test_order_item_count(self, sample_order):
        # Fixture provides consistent test data
        assert len(sample_order.items) == 2
    
    def test_empty_order_total(self, empty_order):
        # Edge case fixture
        assert empty_order.total == 0.0
        assert len(empty_order.items) == 0
```

**Checkpoint:** Fixtures reduce duplication and make tests easier to maintain.

---

## Constraints

### MUST DO
- Use parameterized tests for data-driven test cases
- Mock external dependencies to ensure test isolation
- Test both happy paths and error conditions
- Keep tests fast (unit tests should run in milliseconds)
- Clean up test data in teardown or use fixtures with limited scope
- Follow project's existing test conventions and patterns
- Fail tests on first assertion error for quick feedback

---

## Output Template

When applying this skill to code or reviewing work:

1. **Identified Issues** — List all issues found with severity (critical, high, medium, low)
2. **Root Cause** — Explain why each issue is problematic
3. **Recommended Fix** — Provide specific suggestions for improvement
4. **Code Examples** — Include BAD and GOOD code examples where applicable
5. **Related Standards** — Reference OWASP, SOLID, DRY, or other relevant standards

---

## Related Skills

| Skill | Purpose |
|---|---|
| `coding-code-review` | Review test code for quality and correctness |
| `coding-test-driven-development` | TDD methodology for writing tests first |
| `coding-continuous-integration` | CI pipeline for automated test execution |
| `coding-mocking` | Advanced mocking patterns for complex test scenarios |
| `coding-performance-testing` | Performance testing strategies and tools |
