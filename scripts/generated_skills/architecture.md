---
name: architecture
description: Applies architectural patterns and principles including separation of concerns, dependency management, and design patterns for scalable systems.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  triggers: architecture, design patterns, SOLID, dependency injection, clean architecture, modular design
  role: implementation
  scope: implementation
  output-format: code
  related-skills: coding-refactoring, coding-code-review
---

# Code Quality Specialist

Implements comprehensive code quality practices including review, testing, refactoring, security, and architectural patterns.

## TL;DR Checklist

- [ ] Apply separation of concerns (business logic separate from I/O)
- [ ] Depend on abstractions, not concrete implementations (dependency inversion)
- [ ] Ensure classes have a single reason to change (single responsibility)
- [ ] Use composition over inheritance when appropriate
- [ ] Keep modules cohesive and loosely coupled
- [ ] Design for testability (dependency injection, interfaces)
- [ ] Avoid premature optimization; optimize for clarity first

---

## When to Use

Use this skill when:

- Designing the structure of a new application
- Refactoring a monolith into microservices
- Integrating third-party libraries and frameworks
- Scaling a codebase to support multiple developers
- Improving maintainability of legacy systems
- Setting up project structure and module boundaries
- Establishing architectural guidelines for a team

---

## When NOT to Use

Avoid this skill for:

- Small projects where complexity overhead outweighs benefits
- When requirements are highly uncertain and changing rapidly
- For code that will be replaced within a short timeframe
- When team lacks agreement on architectural direction
- As a substitute for incremental development and user feedback

---

## Core Workflow

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
   **Checkpoint:** Architecture documentation is current and accessible to the team.

---

## Implementation Patterns

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

**Checkpoint:** Object creation is centralized in factories, making code easier to test and configure.

---

## Constraints

### MUST DO
- Keep business logic independent of infrastructure concerns
- Use dependency injection for testability
- Define clear interfaces for external dependencies
- Apply single responsibility to classes and modules
- Favor composition over inheritance for reuse
- Design for testability from the start
- Keep modules focused and cohesive

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
| `coding-refactoring` | Apply refactoring techniques to improve architecture |
| `coding-code-review` | Architectural review during code review |
| `coding-microservices` | Microservices architecture patterns |
| `coding-configuration-management` | Managing application configuration effectively |
| `coding-testing-strategy` | Testing strategy that aligns with architecture |
