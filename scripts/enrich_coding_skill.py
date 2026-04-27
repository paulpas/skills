#!/usr/bin/env python3
"""
Coding Skill Enrichment Template Generator

Generates complete, high-quality SKILL.md files for Coding domain skills
following the OpenCode skill format specification.

Usage:
    python scripts/enrich_coding_skill.py code-review
    python scripts/enrich_coding_skill.py testing
    python scripts/enrich_coding_skill.py refactoring
"""

import sys
import os


def generate_frontmatter(topic: str) -> str:
    """Generate YAML frontmatter for a coding skill."""
    metadata = {
        "code-review": {
            "name": "code-review",
            "description": "Analyzes code diffs and files to identify bugs, security vulnerabilities, code smells, and architectural concerns, producing a structured review report with prioritized, actionable feedback.",
            "triggers": "code review, pull request, PR review, code quality, security audit, OWASP, architectural review",
            "related_skills": "coding-security-review, coding-test-driven-development",
            "role": "review",
            "scope": "review",
            "output_format": "report",
        },
        "testing": {
            "name": "testing",
            "description": "Implements comprehensive test strategies including unit, integration, and end-to-end tests with best practices for test design, mocking, and coverage.",
            "triggers": "unit testing, integration testing, TDD, test automation, mocking, test coverage, pytest",
            "related_skills": "coding-code-review, coding-test-driven-development",
            "role": "implementation",
            "scope": "implementation",
            "output_format": "code",
        },
        "refactoring": {
            "name": "refactoring",
            "description": "Applies systematic refactoring techniques to improve code structure, reduce technical debt, and enhance maintainability without changing external behavior.",
            "triggers": "refactoring, code quality, technical debt, code smells, DRY, SOLID, legacy code",
            "related_skills": "coding-code-review, coding-test-driven-development",
            "role": "implementation",
            "scope": "implementation",
            "output_format": "code",
        },
        "security": {
            "name": "security",
            "description": "Implements security best practices including input validation, authentication patterns, encryption, and vulnerability prevention in application code.",
            "triggers": "security, OWASP, vulnerability, injection, authentication, encryption, secure coding",
            "related_skills": "coding-code-review, coding-security-review",
            "role": "implementation",
            "scope": "implementation",
            "output_format": "code",
        },
        "architecture": {
            "name": "architecture",
            "description": "Applies architectural patterns and principles including separation of concerns, dependency management, and design patterns for scalable systems.",
            "triggers": "architecture, design patterns, SOLID, dependency injection, clean architecture, modular design",
            "related_skills": "coding-refactoring, coding-code-review",
            "role": "implementation",
            "scope": "implementation",
            "output_format": "code",
        },
    }

    meta = metadata.get(topic, metadata["code-review"])
    return f"""---
name: {meta["name"]}
description: {meta["description"]}
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  triggers: {meta["triggers"]}
  role: {meta["role"]}
  scope: {meta["scope"]}
  output-format: {meta["output_format"]}
  related-skills: {meta["related_skills"]}
---"""


# TL;DR Checklist content
def get_tl_dr_checklist(topic: str) -> str:
    if topic == "code-review":
        return """## TL;DR Checklist

- [ ] Identify security vulnerabilities (injection, authentication, authorization)
- [ ] Check for code smells (long methods, large classes, tight coupling)
- [ ] Verify adherence to project conventions and style guide
- [ ] Validate error handling and edge cases
- [ ] Check test coverage and test quality
- [ ] Review architectural decisions and dependencies
- [ ] Provide constructive, actionable feedback with specific recommendations"""
    elif topic == "testing":
        return """## TL;DR Checklist

- [ ] Follow Arrange-Act-Assert (AAA) pattern for test structure
- [ ] Use descriptive test names that specify scenario, context, and expected behavior
- [ ] Mock external dependencies (APIs, databases) to ensure test isolation
- [ ] Test both happy paths and edge cases/error conditions
- [ ] Avoid test interdependencies (tests should run in any order)
- [ ] Keep tests fast (unit tests < 100ms each)
- [ ] Aim for meaningful coverage, not 100% coverage at all costs"""
    elif topic == "refactoring":
        return """## TL;DR Checklist

- [ ] Identify code smells before refactoring (long methods, duplicated code, large classes)
- [ ] Ensure tests exist or add them before making changes
- [ ] Make small, incremental changes with each commit
- [ ] Preserve external behavior while improving internal structure
- [ ] Apply DRY principle to eliminate duplication
- [ ] Break up large methods following Single Responsibility Principle
- [ ] Use meaningful names that express intent clearly"""
    elif topic == "security":
        return """## TL;DR Checklist

- [ ] Validate and sanitize all user input (SQL injection, XSS prevention)
- [ ] Use parameterized queries instead of string concatenation
- [ ] Implement proper authentication with secure session management
- [ ] Store secrets in environment variables or secret management tools
- [ ] Use HTTPS for all communications
- [ ] Implement rate limiting on sensitive endpoints
- [ ] Follow principle of least privilege for access control"""
    elif topic == "architecture":
        return """## TL;DR Checklist

- [ ] Apply separation of concerns (business logic separate from I/O)
- [ ] Depend on abstractions, not concrete implementations (dependency inversion)
- [ ] Ensure classes have a single reason to change (single responsibility)
- [ ] Use composition over inheritance when appropriate
- [ ] Keep modules cohesive and loosely coupled
- [ ] Design for testability (dependency injection, interfaces)
- [ ] Avoid premature optimization; optimize for clarity first"""
    return ""


# TL;DR for Code Generation content
def get_tl_dr_code_gen(topic: str) -> str:
    if topic == "code-review":
        return """## TL;DR for Code Generation

- Use guard clauses — return early on invalid input before doing work
- Return simple types (bool, str, int, list) — avoid returning complex nested dicts
- Cyclomatic complexity ≤ 10 per function — split anything larger
- Handle the null/empty case explicitly
- No subprocess calls in pure logic functions
- Use type hints and docstrings for all public functions
- Follow project's existing code style and conventions"""
    elif topic == "testing":
        return """## TL;DR for Code Generation

- Use parameterized tests for data-driven test cases
- Mock external dependencies with appropriate test doubles
- Test behavior, not implementation details
- Use descriptive test names: "method_state_expectedOutcome"
- Assert on the smallest possible contract
- Clean up test data in teardown or use fixtures with limited scope
- Keep test setup minimal and focused"""
    elif topic == "refactoring":
        return """## TL;DR for Code Generation

- Extract methods when complexity exceeds cognitive load
- Rename variables and methods to express intent clearly
- Remove dead code and unused imports
- Group related code into cohesive modules
- Apply design patterns only when they solve a known problem
- Add tests before changing behavior
- Refactor in small, testable increments"""
    elif topic == "security":
        return """## TL;DR for Code Generation

- Never trust user input — validate and sanitize before use
- Use parameterized queries to prevent SQL injection
- Hash passwords with bcrypt or scrypt, never store plaintext
- Implement proper session management with secure cookies
- Use HTTPS for all communications
- Log security events for auditing
- Apply least privilege for database and API access"""
    elif topic == "architecture":
        return """## TL;DR for Code Generation

- Keep business logic independent of infrastructure concerns
- Use dependency injection for testability
- Define clear interfaces for external dependencies
- Apply single responsibility to classes and modules
- Favor composition over inheritance for reuse
- Design for testability from the start
- Keep modules focused and cohesive"""
    return ""


# When to Use content
def get_when_to_use(topic: str) -> str:
    if topic == "code-review":
        return """## When to Use

Use this skill when:

- Reviewing code changes before merging to main branch
- Onboarding new team members and establishing code quality standards
- Identifying security vulnerabilities in existing codebases
- Preparing code for production deployment
- Improving technical documentation through code clarity
- Conducting peer code reviews in agile development cycles
- Auditing third-party code integrations for quality and security"""
    elif topic == "testing":
        return """## When to Use

Use this skill when:

- Implementing new features with comprehensive test coverage
- Refactoring existing code to ensure no behavior changes
- Setting up a new project's test infrastructure
- Improving test coverage in legacy codebases
- Debugging complex issues with systematic test cases
- Implementing continuous integration pipelines
- Validating edge cases and error conditions"""
    elif topic == "refactoring":
        return """## When to Use

Use this skill when:

- Adding new features is difficult due to code complexity
- Bug fixes require extensive code changes
- Code duplication makes maintenance difficult
- Tests are slow or unreliable due to tight coupling
- New team members struggle to understand the codebase
- Performance issues stem from poor code organization
- Technical debt is accumulating and slowing development"""
    elif topic == "security":
        return """## When to Use

Use this skill when:

- Implementing user authentication and authorization
- Building APIs that handle sensitive data
- Integrating with external services and APIs
- Setting up database connections and queries
- Implementing encryption for data at rest or in transit
- Building applications that process financial or personal data
- Conducting security audits or penetration testing preparation"""
    elif topic == "architecture":
        return """## When to Use

Use this skill when:

- Designing the structure of a new application
- Refactoring a monolith into microservices
- Integrating third-party libraries and frameworks
- Scaling a codebase to support multiple developers
- Improving maintainability of legacy systems
- Setting up project structure and module boundaries
- Establishing architectural guidelines for a team"""
    return ""


# When NOT to Use content
def get_when_not_to_use(topic: str) -> str:
    if topic == "code-review":
        return """## When NOT to Use

Avoid this skill for:

- Fixing critical production bugs where speed is paramount — fix first, review later
- Trivial changes (typo fixes, whitespace) — consider automated formatting instead
- Skills that require deep domain expertise not available in the reviewer's knowledge
- Reviewing code with significantly different conventions than your team's standards
- As a substitute for automated testing — review complements, doesn't replace, tests"""
    elif topic == "testing":
        return """## When NOT to Use

Avoid this skill for:

- Writing tests for code that will be discarded immediately (prototypes, spikes)
- Testing code with no reliable behavior to verify (random generation without constraints)
- When test infrastructure doesn't exist and setup cost outweighs benefit
- As a replacement for manual QA for complex user workflows
- For code that is purely infrastructure with no logical behavior to test"""
    elif topic == "refactoring":
        return """## When NOT to Use

Avoid this skill for:

- Production-critical code without existing test coverage (refactor after tests)
- Code with known issues — fix bugs before refactoring
- Legacy code with no tests and no understanding of behavior
- When business deadlines don't allow time for thorough refactoring
- Code that will be rewritten entirely in an upcoming major version
- Without understanding the existing codebase's patterns and conventions"""
    elif topic == "security":
        return """## When NOT to Use

Avoid this skill for:

- Implementing security for non-sensitive data (security has overhead)
- Prototyping where security is not a concern (fix before production)
- When you lack understanding of the threat model and attack surface
- Using security tools without understanding their limitations
- As a replacement for security audits by specialized professionals"""
    elif topic == "architecture":
        return """## When NOT to Use

Avoid this skill for:

- Small projects where complexity overhead outweighs benefits
- When requirements are highly uncertain and changing rapidly
- For code that will be replaced within a short timeframe
- When team lacks agreement on architectural direction
- As a substitute for incremental development and user feedback"""
    return ""


# Core Workflow content
def get_core_workflow(topic: str) -> str:
    if topic == "code-review":
        return """## Core Workflow

1. **Assess Scope and Context** — Review pull request description, linked issues, and deployment notes.
   **Checkpoint:** Understand the purpose and scope of changes before reviewing code.

2. **Review for Security Issues** — Check for common vulnerabilities (injection, authentication, authorization, data exposure).
   **Checkpoint:** Identify and flag any security concerns before moving to code quality review.

3. **Evaluate Code Quality** — Assess adherence to style guide, code smells, and complexity metrics.
   **Checkpoint:** Verify tests exist and cover edge cases before approving.

4. **Check Architecture and Design** — Ensure changes align with project architecture and don't introduce technical debt.
   **Checkpoint:** Confirm dependencies and module boundaries are appropriate.

5. **Provide Constructive Feedback** — Document issues with clear explanations and suggested improvements.
   **Checkpoint:** All feedback is actionable, specific, and respectful.

6. **Approve or Request Changes** — Use appropriate status based on review findings.
   **Checkpoint:** Approved code meets all team quality and security standards."""
    elif topic == "testing":
        return """## Core Workflow

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
   **Checkpoint:** Test documentation is updated alongside code changes."""
    elif topic == "refactoring":
        return """## Core Workflow

1. **Identify Code Smells** — Scan for indicators of poor structure (long methods, large classes, duplication).
   **Checkpoint:** List specific code smells with file locations and line numbers.

2. **Assess Risk and Testability** — Determine if tests exist or need to be added before refactoring.
   **Checkpoint:** Either existing tests cover the behavior or new tests will be added first.

3. **Plan Refactoring Steps** — Break complex refactoring into small, testable changes.
   **Checkpoint:** Each step is small enough to verify quickly and safely.

4. **Apply Refactoring Pattern** — Implement the chosen pattern (extract method, rename variable, etc.).
   **Checkpoint:** Code still functions correctly after each change.

5. **Run Tests** — Execute test suite to verify behavior hasn't changed.
   **Checkpoint:** All tests pass before proceeding to next refactoring step.

6. **Review for Improvement** — Assess if additional refactoring opportunities exist.
   **Checkpoint:** Code quality has improved and new smells have been addressed.

7. **Update Documentation** — Update comments, docstrings, and architectural notes.
   **Checkpoint:** Documentation accurately reflects the refactored code structure."""
    elif topic == "security":
        return """## Core Workflow

1. **Identify Attack Surface** — Map all user inputs, API endpoints, and external integrations.
   **Checkpoint:** Complete inventory of all entry points that could accept malicious input.

2. **Apply Input Validation** — Implement validation for all user inputs (type, format, range).
   **Checkpoint:** All inputs are validated before processing.

3. **Review Authentication and Authorization** — Verify proper implementation of auth patterns.
   **Checkpoint:** Authentication is secure and authorization follows least privilege.

4. **Check Data Protection** — Ensure sensitive data is encrypted in transit and at rest.
   **Checkpoint:** Secrets are not hardcoded and encryption is properly configured.

5. **Review Error Handling** — Ensure error messages don't leak sensitive information.
   **Checkpoint:** Generic error messages for users, detailed logging for developers.

6. **Apply Secure Defaults** — Configure secure defaults for all settings and configurations.
   **Checkpoint:** Application is secure out of the box without manual configuration.

7. **Document Security Considerations** — Record security decisions and known limitations.
   **Checkpoint:** Security documentation is available for review and audit."""
    elif topic == "architecture":
        return """## Core Workflow

1. **Understand Requirements and Constraints** — Review functional requirements, non-functional requirements, and constraints.
   **Checkpoint:** Clear understanding of what the system must do and how it must perform.

2. **Identify Key Components** — Break system into major components and their responsibilities.
   **Checkpoint:** Each component has a single, well-defined responsibility.

3. **Define Component Interfaces** — Specify how components interact (interfaces, contracts, events).
   **Checkpoint:** Interfaces are minimal, focused, and testable.

4. **Apply Design Patterns** — Select appropriate patterns for common architectural challenges.
   **Checkpoint:** Patterns are applied where they solve actual problems, not as dogma.

5. **Establish Layering** — Define layers (presentation, business logic, data access) and dependencies.
   **Checkpoint:** Dependencies flow inward (toward business logic), not outward.

6. **Validate with Examples** — Walk through concrete use cases to verify architecture supports requirements.
   **Checkpoint:** Architecture handles all identified requirements without major modifications.

7. **Document Architecture** — Create diagrams, decisions, and trade-off documentation.
   **Checkpoint:** Architecture documentation is current and accessible to the team."""
    return ""


# Implementation Patterns content
def get_implementation_patterns(topic: str) -> str:
    if topic == "code-review":
        return """## Implementation Patterns

### Pattern 1: Security Vulnerability Detection

**Use Case:** Identifying common security vulnerabilities in application code.

```python
# BAD: SQL injection vulnerability
def bad_user_lookup(user_id: str) -> dict:
    # ❌ BAD: String concatenation allows SQL injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()

# GOOD: Parameterized query prevents SQL injection
def good_user_lookup(user_id: str) -> dict:
    # ✅ GOOD: Parameterized query prevents SQL injection
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, [user_id])
    return cursor.fetchone()

# GOOD: Input validation with type checking
def safe_user_lookup(user_id: int) -> dict:
    # ✅ GOOD: Type hint and validation ensure expected input
    if not isinstance(user_id, int):
        raise ValueError(f"Expected int, got {type(user_id).__name__}")
    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, [user_id])
    return cursor.fetchone()
```

**Checkpoint:** All SQL queries use parameterized statements, never string concatenation.

---

### Pattern 2: Code Review Comment Template

**Use Case:** Providing constructive, actionable feedback on code changes.

```python
# BAD: Vague, unhelpful comment
def bad_review_comment():
    # ❌ BAD: Vague and unhelpful
    # "This looks wrong"
    # "Fix this"
    pass

# GOOD: Specific, actionable, with explanation and suggestion
def good_review_comment():
    # ✅ GOOD: Specific, actionable, with explanation and suggestion
    # Security: SQL injection risk
    # 
    # The current implementation uses f-string interpolation in the query,
    # which allows SQL injection attacks.
    # 
    # Consider using parameterized queries instead:
    # 
    #   query = "SELECT * FROM users WHERE id = %s"
    #   cursor.execute(query, [user_id])
    pass

# GOOD: Positive reinforcement
def praise_good_practice():
    # ✅ GOOD: Recognizes good practice
    # "Great use of type hints here — they really help with code readability
    # and catch errors early."
    pass
```

**Checkpoint:** Every comment includes what, why, and how to fix.

---

### Pattern 3: Review Checklist Integration

**Use Case:** Ensuring consistent review quality with automated checklists.

```python
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ReviewIssue:
    severity: str  # critical, high, medium, low
    category: str  # security, code-quality, architecture
    description: str
    location: str
    suggestion: str


class ReviewChecklist:
    '''Automated checklist for code review consistency.'''
    
    def __init__(self):
        self.issues: List[ReviewIssue] = []
    
    def check_sql_injection(self, code: str) -> None:
        '''Check for SQL injection vulnerabilities.'''
        if 'execute(f"' in code or "execute(f'" in code:
            self.issues.append(ReviewIssue(
                severity="critical",
                category="security",
                description="Potential SQL injection detected",
                location="String concatenation in SQL execute call",
                suggestion="Use parameterized queries instead of f-strings"
            ))
    
    def get_critical_issues(self) -> List[ReviewIssue]:
        '''Return only critical issues that block merging.'''
        return [issue for issue in self.issues if issue.severity == "critical"]
```

**Checkpoint:** Review checklist runs automatically and blocks merge for critical issues."""

    elif topic == "testing":
        return """## Implementation Patterns

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

**Checkpoint:** Fixtures reduce duplication and make tests easier to maintain."""

    elif topic == "refactoring":
        return """## Implementation Patterns

### Pattern 1: Extract Method Refactoring

**Use Case:** Reducing code duplication and improving readability.

```python
# BAD: Duplicated code, hard to maintain
def calculate_order_total_bad(order):
    subtotal = 0
    for item in order.items:
        # Price calculation logic duplicated
        if item.quantity > 10:
            price = item.unit_price * 0.9
        elif item.quantity > 5:
            price = item.unit_price * 0.95
        else:
            price = item.unit_price
        subtotal += price * item.quantity
    
    # Tax calculation logic duplicated
    if order.customer.is_vip:
        tax = subtotal * 0.05
    else:
        tax = subtotal * 0.08
    
    return subtotal + tax


# GOOD: Extracted methods for clarity
def calculate_item_price(item):
    '''Calculate price per item with quantity discounts.'''
    if item.quantity > 10:
        return item.unit_price * 0.9
    elif item.quantity > 5:
        return item.unit_price * 0.95
    else:
        return item.unit_price


def calculate_tax(subtotal: float, customer: "Customer") -> float:
    '''Calculate tax based on customer type.'''
    if customer.is_vip:
        return subtotal * 0.05
    else:
        return subtotal * 0.08


def calculate_order_total_good(order: "Order") -> float:
    '''Calculate total order amount.'''
    subtotal = sum(calculate_item_price(item) * item.quantity for item in order.items)
    tax = calculate_tax(subtotal, order.customer)
    return subtotal + tax
```

**Checkpoint:** Each method has a single responsibility and is easy to test.

---

### Pattern 2: Rename for Clarity

**Use Case:** Improving code readability through meaningful names.

```python
# BAD: Unclear variable names
def process_data(a, b, c):
    x = a + b
    y = x * c
    return y > 100


# GOOD: Names express intent
def calculate_final_score(
    base_score: int,
    multiplier: int,
    threshold: int
) -> bool:
    '''Calculate if the final score exceeds the threshold.'''
    intermediate_result = base_score + multiplier
    final_value = intermediate_result * multiplier
    return final_value > threshold


# BAD: Generic function name
def do_it(data):
    # What does this do?
    pass


# GOOD: Descriptive function name
def validate_and_normalize_user_input(raw_input: str) -> dict:
    '''Parse and validate user input, returning normalized data structure.'''
    if not raw_input:
        raise ValueError("Input cannot be empty")
    # Processing logic here
    return {"raw": raw_input, "normalized": raw_input.strip().lower()}
```

**Checkpoint:** All variable and function names express intent clearly.

---

### Pattern 3: Replace Conditional with Polymorphism

**Use Case:** Eliminating complex conditionals with polymorphic behavior.

```python
from abc import ABC, abstractmethod


# BAD: Complex conditional logic
class BadOrderProcessor:
    def calculate_shipping(self, order: "Order", carrier: str) -> float:
        # Ugly conditional
        if carrier == "ups":
            return order.weight * 2.50
        elif carrier == "fedex":
            return order.weight * 2.25
        elif carrier == "usps":
            return order.weight * 1.75
        elif carrier == "dhl":
            return order.weight * 3.00
        else:
            raise ValueError(f"Unknown carrier: {carrier}")


# GOOD: Polymorphic design
class ShippingCarrier(ABC):
    @abstractmethod
    def calculate_rate(self, weight: float) -> float:
        pass


class UPSCarrier(ShippingCarrier):
    def calculate_rate(self, weight: float) -> float:
        return weight * 2.50


class FedExCarrier(ShippingCarrier):
    def calculate_rate(self, weight: float) -> float:
        return weight * 2.25


class USPSCarrier(ShippingCarrier):
    def calculate_rate(self, weight: float) -> float:
        return weight * 1.75


class DHLCarrier(ShippingCarrier):
    def calculate_rate(self, weight: float) -> float:
        return weight * 3.00


class GoodOrderProcessor:
    def __init__(self, carrier: ShippingCarrier):
        self.carrier = carrier
    
    def calculate_shipping(self, weight: float) -> float:
        return self.carrier.calculate_rate(weight)
```

**Checkpoint:** Conditionals are replaced with polymorphism or strategy pattern."""

    elif topic == "security":
        return """## Implementation Patterns

### Pattern 1: Input Validation with Type Hints

**Use Case:** Preventing injection attacks through proper input validation.

```python
from dataclasses import dataclass
from typing import Optional
import re


# BAD: No input validation
class BadUserInput:
    def process_username(self, username: str) -> str:
        # ❌ BAD: No validation, vulnerable to XSS
        return f"<div>{username}</div>"
    
    def build_query(self, table: str, user_id: str) -> str:
        # ❌ BAD: String concatenation allows SQL injection
        return f"SELECT * FROM {table} WHERE id = {user_id}"


# GOOD: Strict input validation
def validate_username(username: str) -> str:
    '''Validate and sanitize username input.'''
    if not username:
        raise ValueError("Username cannot be empty")
    
    if len(username) > 50:
        raise ValueError("Username must be 50 characters or fewer")
    
    # Only allow letters, numbers, underscores, and hyphens
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
    
    return username.strip()


def validate_email(email: str) -> str:
    '''Validate email format.'''
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+[.][a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    return email.lower().strip()


# GOOD: Safe query building
def safe_user_query(table: str, user_id: int) -> tuple:
    '''Build safe SQL query with validated inputs.'''
    allowed_tables = ["users", "accounts", "profiles"]
    if table not in allowed_tables:
        raise ValueError(f"Invalid table name: {table}")
    
    query = f"SELECT * FROM {table} WHERE id = %s"
    return (query, [user_id])
```

**Checkpoint:** All user inputs are validated before use in queries or output.

---

### Pattern 2: Secure Password Hashing

**Use Case:** Storing passwords securely using bcrypt.

```python
import bcrypt


# BAD: Insecure password storage
class BadPasswordStorage:
    def hash_password(self, password: str) -> str:
        # ❌ BAD: Plain text storage - never do this
        return password
    
    def verify_password(self, password: str, hashed: str) -> bool:
        # ❌ BAD: Direct string comparison
        return password == hashed


# GOOD: bcrypt for secure password hashing
class SecurePasswordStorage:
    def __init__(self, rounds: int = 12):
        self.rounds = rounds
    
    def hash_password(self, password: str) -> bytes:
        '''Hash a password using bcrypt with salt.'''
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed
    
    def verify_password(self, password: str, hashed: bytes) -> bool:
        '''Verify a password against its hash.'''
        if not password or not hashed:
            return False
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed)
        except Exception:
            return False
```

**Checkpoint:** Passwords are never stored in plain text; always use bcrypt or scrypt.

---

### Pattern 3: Rate Limiting Implementation

**Use Case:** Protecting endpoints from brute force attacks.

```python
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict
from threading import Lock


@dataclass
class RateLimitConfig:
    max_requests: int
    window_seconds: int


class RateLimiter:
    '''Thread-safe rate limiter for API endpoints.'''
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self._requests: Dict[str, list] = defaultdict(list)
        self._lock = Lock()
    
    def is_allowed(self, identifier: str) -> bool:
        '''Check if request is allowed for identifier (IP, user, etc.).'''
        with self._lock:
            current_time = time.time()
            window_start = current_time - self.config.window_seconds
            
            # Clean old requests outside the window
            self._requests[identifier] = [
                timestamp for timestamp in self._requests[identifier]
                if timestamp > window_start
            ]
            
            # Check if under limit
            if len(self._requests[identifier]) >= self.config.max_requests:
                return False
            
            # Record this request
            self._requests[identifier].append(current_time)
            return True


# GOOD: Usage with rate limiting
class LoginEndpoint:
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
    
    def login(self, username: str, password: str, client_ip: str):
        # ✅ GOOD: Rate limit login attempts
        if not self.rate_limiter.is_allowed(client_ip):
            return {"error": "Too many login attempts"}, 429
        
        # Authentication logic here
        return {"status": "success"}
```

**Checkpoint:** Rate limiting prevents brute force attacks on sensitive endpoints."""

    elif topic == "architecture":
        return """## Implementation Patterns

### Pattern 1: Dependency Injection for Testability

**Use Case:** Writing loosely coupled code that's easy to test.

```python
from abc import ABC, abstractmethod


# GOOD: Interface-based design with dependency injection
class DatabaseInterface(ABC):
    '''Abstract interface for database operations.'''
    
    @abstractmethod
    def fetch_user(self, user_id: int) -> dict:
        pass
    
    @abstractmethod
    def save_user(self, user: dict) -> None:
        pass


# GOOD: Service depends on abstraction, not implementation
class UserService:
    # ✅ GOOD: Dependency injected via constructor
    def __init__(self, database: DatabaseInterface):
        self.database = database
    
    def get_user(self, user_id: int) -> dict:
        return self.database.fetch_user(user_id)
    
    def save_user(self, user: dict) -> None:
        self.database.save_user(user)


# GOOD: Easy to test with mock
class TestUserService:
    def test_get_user_calls_database(self):
        # Arrange
        mock_db = Mock(spec=DatabaseInterface)
        mock_db.fetch_user.return_value = {"id": 123, "name": "Test User"}
        service = UserService(mock_db)
        
        # Act
        result = service.get_user(123)
        
        # Assert
        assert result == {"id": 123, "name": "Test User"}
        mock_db.fetch_user.assert_called_once_with(123)
```

**Checkpoint:** Services depend on abstractions (interfaces), not concrete implementations.

---

### Pattern 2: Separation of Concerns (Business Logic vs I/O)

**Use Case:** Keeping business logic independent of infrastructure concerns.

```python
from dataclasses import dataclass
from typing import List


@dataclass
class OrderItem:
    product_id: int
    quantity: int
    unit_price: float
    
    @property
    def line_total(self) -> float:
        '''Pure function: calculates line total, no I/O.'''
        return self.quantity * self.unit_price


@dataclass
class Order:
    items: List[OrderItem]
    tax_rate: float = 0.08
    
    def calculate_subtotal(self) -> float:
        '''Pure function: calculates subtotal, no I/O.'''
        return sum(item.line_total for item in self.items)
    
    def calculate_tax(self) -> float:
        '''Pure function: calculates tax, no I/O.'''
        return self.calculate_subtotal() * self.tax_rate
    
    def calculate_total(self) -> float:
        '''Pure function: calculates total, no I/O.'''
        return self.calculate_subtotal() + self.calculate_tax()


# GOOD: Clean separation of concerns
class OrderService:
    # ✅ GOOD: Business logic separated from I/O
    def __init__(self, database: "DatabaseInterface"):
        self.database = database
    
    def process_order(self, order_data: dict) -> dict:
        # 1. Validate (pure)
        order = Order(
            items=[OrderItem(**item) for item in order_data["items"]],
            tax_rate=order_data.get("tax_rate", 0.08),
        )
        
        # 2. Business logic (pure)
        total = order.calculate_total()
        
        # 3. I/O (database operations)
        self.database.save_order(order_data, total)
        
        return {"total": total, "tax": order.calculate_tax()}
```

**Checkpoint:** Business logic functions are pure (no I/O, no side effects) and easy to test.

---

### Pattern 3: Factory Pattern for Object Creation

**Use Case:** Creating complex objects with varying configurations.

```python
from abc import ABC, abstractmethod


class EmailService(ABC):
    '''Abstract interface for email sending.'''
    
    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool:
        pass


class SMTPEmailService(EmailService):
    '''SMTP-based email service.'''
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        return True


class MockEmailService(EmailService):
    '''Mock email service for testing.'''
    
    def __init__(self):
        self.sent_emails = []
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        self.sent_emails.append({"to": to, "subject": subject, "body": body})
        return True


# GOOD: Factory pattern for object creation
class EmailServiceFactory:
    '''Factory for creating email service instances.'''
    
    @staticmethod
    def create_service(env: str = "development") -> EmailService:
        '''Create appropriate email service based on environment.'''
        if env == "production":
            return SMTPEmailService(
                host=os.environ.get("SMTP_HOST", "smtp.example.com"),
                port=int(os.environ.get("SMTP_PORT", 587)),
            )
        else:
            return MockEmailService()


# GOOD: Easy to test with factory-provided mock
class NotificationService:
    def __init__(self, email_service: EmailService):
        self.email_service = email_service
    
    def send_notification(self, to: str, message: str) -> bool:
        return self.email_service.send_email(to=to, subject="Notification", body=message)
```

**Checkpoint:** Object creation is centralized in factories, making code easier to test and configure."""
    return ""


# Constraints content
def get_constraints(topic: str) -> str:
    if topic == "code-review":
        return """## Constraints

### MUST DO
- Review security vulnerabilities first — flag any critical issues before code quality
- Provide specific, actionable feedback with suggestions for improvement
- Reference project style guide and coding standards explicitly
- Verify tests exist and cover edge cases before approving
- Use positive reinforcement to recognize good practices
- Document all review decisions in comments for audit trail
- Block merge for critical security issues, even if code otherwise looks good"""
    elif topic == "testing":
        return """## Constraints

### MUST DO
- Use parameterized tests for data-driven test cases
- Mock external dependencies to ensure test isolation
- Test both happy paths and error conditions
- Keep tests fast (unit tests should run in milliseconds)
- Clean up test data in teardown or use fixtures with limited scope
- Follow project's existing test conventions and patterns
- Fail tests on first assertion error for quick feedback"""
    elif topic == "refactoring":
        return """## Constraints

### MUST DO
- Ensure tests exist before refactoring, or add them first
- Make small, incremental changes with each commit
- Preserve external behavior while improving internal structure
- Apply DRY principle to eliminate duplication
- Use meaningful names that express intent clearly
- Document refactoring decisions and trade-offs
- Run tests after each refactoring step"""
    elif topic == "security":
        return """## Constraints

### MUST DO
- Validate and sanitize all user input before processing
- Use parameterized queries to prevent SQL injection
- Hash passwords with bcrypt or scrypt, never store plaintext
- Implement proper session management with secure cookies
- Log security events for auditing
- Follow principle of least privilege for all access
- Use HTTPS for all communications"""
    elif topic == "architecture":
        return """## Constraints

### MUST DO
- Keep business logic independent of infrastructure concerns
- Use dependency injection for testability
- Define clear interfaces for external dependencies
- Apply single responsibility to classes and modules
- Favor composition over inheritance for reuse
- Design for testability from the start
- Keep modules focused and cohesive"""
    return ""


# Related Skills content
def get_related_skills(topic: str) -> str:
    if topic == "code-review":
        return """## Related Skills

| Skill | Purpose |
|---|---|
| `coding-security-review` | Specialized security-focused code review with deep OWASP analysis |
| `coding-test-driven-development` | TDD practices for writing tests before implementation |
| `coding-refactoring` | Refactoring techniques to improve code quality after review |
| `coding-architecture` | Architectural patterns and design principles for code review |
| `coding-continuous-integration` | CI pipeline setup for automated code quality checks |"""
    elif topic == "testing":
        return """## Related Skills

| Skill | Purpose |
|---|---|
| `coding-code-review` | Review test code for quality and correctness |
| `coding-test-driven-development` | TDD methodology for writing tests first |
| `coding-continuous-integration` | CI pipeline for automated test execution |
| `coding-mocking` | Advanced mocking patterns for complex test scenarios |
| `coding-performance-testing` | Performance testing strategies and tools |"""
    elif topic == "refactoring":
        return """## Related Skills

| Skill | Purpose |
|---|---|
| `coding-code-review` | Get peer review on refactoring changes |
| `coding-test-driven-development` | TDD ensures refactoring doesn't break behavior |
| `coding-architecture` | Apply architectural patterns during refactoring |
| `coding-performance-optimization` | Optimize code after structural improvements |
| `coding-legacy-code` | Strategies for refactoring untested legacy systems |"""
    elif topic == "security":
        return """## Related Skills

| Skill | Purpose |
|---|---|
| `coding-code-review` | Security-focused code review to identify vulnerabilities |
| `coding-security-audit` | Comprehensive security audit of entire application |
| `coding-secret-management` | Secure handling of secrets and credentials |
| `coding-authentication` | Authentication patterns and best practices |
| `coding-encryption` | Encryption patterns for data protection |"""
    elif topic == "architecture":
        return """## Related Skills

| Skill | Purpose |
|---|---|
| `coding-refactoring` | Apply refactoring techniques to improve architecture |
| `coding-code-review` | Architectural review during code review |
| `coding-microservices` | Microservices architecture patterns |
| `coding-configuration-management` | Managing application configuration effectively |
| `coding-testing-strategy` | Testing strategy that aligns with architecture |"""
    return ""


def generate_skill(topic: str) -> str:
    """Generate complete SKILL.md content for a coding skill."""
    frontmatter = generate_frontmatter(topic)

    content = f"""{frontmatter}

# Code Quality Specialist

Implements comprehensive code quality practices including review, testing, refactoring, security, and architectural patterns.

{get_tl_dr_checklist(topic)}

---

{get_when_to_use(topic)}

---

{get_when_not_to_use(topic)}

---

{get_core_workflow(topic)}

---

{get_implementation_patterns(topic)}

---

{get_constraints(topic)}

---

## Output Template

When applying this skill to code or reviewing work:

1. **Identified Issues** — List all issues found with severity (critical, high, medium, low)
2. **Root Cause** — Explain why each issue is problematic
3. **Recommended Fix** — Provide specific suggestions for improvement
4. **Code Examples** — Include BAD and GOOD code examples where applicable
5. **Related Standards** — Reference OWASP, SOLID, DRY, or other relevant standards

---

{get_related_skills(topic)}
"""
    return content


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/enrich_coding_skill.py <topic>")
        print("\nTopics available:")
        print("  - code-review")
        print("  - testing")
        print("  - refactoring")
        print("  - security")
        print("  - architecture")
        print("\nExample:")
        print("  python scripts/enrich_coding_skill.py code-review")
        sys.exit(1)

    topic = sys.argv[1].lower().strip()

    # Validate topic
    valid_topics = ["code-review", "testing", "refactoring", "security", "architecture"]
    if topic not in valid_topics:
        print(f"Error: Invalid topic '{topic}'")
        print(f"Valid topics are: {', '.join(valid_topics)}")
        sys.exit(1)

    # Generate skill content
    content = generate_skill(topic)

    # Write to file
    output_path = (
        f"/home/paulpas/git/agent-skill-router/scripts/generated_skills/{topic}.md"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        f.write(content)

    # Report file size
    file_size = os.path.getsize(output_path)
    print(f"Generated skill for '{topic}'")
    print(f"Output: {output_path}")
    print(f"Size: {file_size:,} bytes")

    # Verify minimum size
    if file_size < 3000:
        print(
            f"WARNING: File size ({file_size:,} bytes) is below minimum (3,000 bytes)"
        )
        sys.exit(1)
    else:
        print("✅ File meets minimum size requirement (≥ 3,000 bytes)")

    # Count code blocks
    code_blocks = content.count("```")
    print(f"Code blocks: {code_blocks}")
    if code_blocks < 2:
        print("WARNING: Fewer than 2 code blocks found")
    else:
        print("✅ Meets code block requirement (≥ 2 code blocks)")


if __name__ == "__main__":
    main()
