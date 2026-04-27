---
name: refactoring
description: Applies systematic refactoring techniques to improve code structure, reduce technical debt, and enhance maintainability without changing external behavior.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  triggers: refactoring, code quality, technical debt, code smells, DRY, SOLID, legacy code
  role: implementation
  scope: implementation
  output-format: code
  related-skills: coding-code-review, coding-test-driven-development
---

# Code Quality Specialist

Implements comprehensive code quality practices including review, testing, refactoring, security, and architectural patterns.

## TL;DR Checklist

- [ ] Identify code smells before refactoring (long methods, duplicated code, large classes)
- [ ] Ensure tests exist or add them before making changes
- [ ] Make small, incremental changes with each commit
- [ ] Preserve external behavior while improving internal structure
- [ ] Apply DRY principle to eliminate duplication
- [ ] Break up large methods following Single Responsibility Principle
- [ ] Use meaningful names that express intent clearly

---

## When to Use

Use this skill when:

- Adding new features is difficult due to code complexity
- Bug fixes require extensive code changes
- Code duplication makes maintenance difficult
- Tests are slow or unreliable due to tight coupling
- New team members struggle to understand the codebase
- Performance issues stem from poor code organization
- Technical debt is accumulating and slowing development

---

## When NOT to Use

Avoid this skill for:

- Production-critical code without existing test coverage (refactor after tests)
- Code with known issues — fix bugs before refactoring
- Legacy code with no tests and no understanding of behavior
- When business deadlines don't allow time for thorough refactoring
- Code that will be rewritten entirely in an upcoming major version
- Without understanding the existing codebase's patterns and conventions

---

## Core Workflow

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
   **Checkpoint:** Documentation accurately reflects the refactored code structure.

---

## Implementation Patterns

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

**Checkpoint:** Conditionals are replaced with polymorphism or strategy pattern.

---

## Constraints

### MUST DO
- Ensure tests exist before refactoring, or add them first
- Make small, incremental changes with each commit
- Preserve external behavior while improving internal structure
- Apply DRY principle to eliminate duplication
- Use meaningful names that express intent clearly
- Document refactoring decisions and trade-offs
- Run tests after each refactoring step

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
| `coding-code-review` | Get peer review on refactoring changes |
| `coding-test-driven-development` | TDD ensures refactoring doesn't break behavior |
| `coding-architecture` | Apply architectural patterns during refactoring |
| `coding-performance-optimization` | Optimize code after structural improvements |
| `coding-legacy-code` | Strategies for refactoring untested legacy systems |
