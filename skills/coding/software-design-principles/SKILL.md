---
name: software-design-principles
description: Implements core software design principles (SOLID, KISS, YAGNI, composition over inheritance, DRY) to guide architecture decisions and prevent structural debt.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  triggers: software design, SOLID principles, KISS, YAGNI, DRY, composition over inheritance, clean code, modular design
  role: implementation
  scope: implementation
  output-format: code
  content-types: [code, guidance, do-dont, examples]
  related-skills: coding-code-review, coding-design-patterns, coding-refactoring
---

# Core Software Design Principles

Applies foundational software design principles to guide architecture decisions, enforce maintainable structure, and prevent technical debt. This skill makes the model evaluate existing code and design new systems against established engineering standards.

## TL;DR Checklist

- [ ] Verify Single Responsibility: does each class/module handle only one reason to change?
- [ ] Check Open/Closed: can new behavior be added without modifying existing source?
- [ ] Validate Interface Segregation: are clients forced to depend on unused methods?
- [ ] Apply Dependency Inversion: do high-level modules depend on abstractions, not concretions?
- [ ] Enforce KISS and YAGNI: is the solution simpler than necessary? Are we building unneeded features?
- [ ] Prefer composition over inheritance for reuse.

---

## When to Use

Use this skill when:

- Architecting a new module, service, or library from scratch
- Reviewing code that exhibits tight coupling, God classes, or fragile base class problems
- Refactoring legacy systems to improve testability and maintainability
- Conducting design discussions where trade-offs between flexibility and complexity need evaluation
- Onboarding developers who need to align with project architecture standards

---

## When NOT to Use

Avoid this skill for:

- One-off scripts or throwaway prototypes where elegance outweighs correctness
- Performance-critical inner loops where abstraction overhead is unacceptable
- Domain-Driven Design strategic pattern discussions (use domain modeling skills instead)
- UI/UX layout decisions — this focuses on structural design, not presentation layer

---

## Core Workflow

1. **Audit Current Structure** — Map dependencies between modules. Identify God classes (>300 lines, >8 responsibilities), tight coupling (circular imports, direct concrete instantiation across layers), and violation of SRP.
   **Checkpoint:** Every module should have exactly one reason to change. If two unrelated features cause changes in the same file, split it.

2. **Apply SOLID Evaluation** — Check each class/interface against the five principles:
   - **S**RP: Single responsibility boundary clearly defined
   - **O**CP: Extend via new implementations, not modified source code
   - **L**SP: Subtypes must honor base contract preconditions/postconditions
   - **I**SP: Split fat interfaces into focused client-specific contracts
   - **D**IP: Depend on abstractions (`Protocol`/`ABC`) or traits, not concrete classes
   **Checkpoint:** No high-level business logic should import low-level implementation details.

3. **Filter Through KISS & YAGNI** — Strip away abstractions that add cognitive load without delivering immediate value. Ask: "Will this pattern be needed in the next release?" If no, implement it plainly.
   **Checkpoint:** Every factory, strategy, or decorator must solve a concrete current problem, not a hypothetical future one.

4. **Enforce Composition Over Inheritance** — Replace deep inheritance trees with composable objects. Use dependency injection to assemble behavior at runtime rather than compile time.
   **Checkpoint:** Inheritance depth should not exceed 2 levels. If it does, refactor to composition.

5. **Validate and Document** — Generate architecture decision records (ADRs) for non-obvious design choices. Ensure interfaces are explicitly typed and documented.
   **Checkpoint:** Public APIs must have clear contracts, error handling paths, and usage examples.

---

## Implementation Patterns / Reference Guide

### Pattern 1: SOLID in Practice (SRP + OCP + DIP)

```python
# ❌ BAD — Violates SRP (handles both business logic AND persistence), OCP (modifies source to add payment types), DIP (depends on concrete Stripe class)
class PaymentProcessor:
    def __init__(self):
        self.db = SQLiteConnection("payments.db")
        self.gateway = StripeGateway(api_key="sk_live_...")

    def process(self, order_id: int, amount: float) -> bool:
        # Business logic mixed with persistence
        payment_record = {
            "order_id": order_id,
            "amount": amount,
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        }
        self.db.insert("payments", payment_record)

        # Tight coupling to specific provider
        response = self.gateway.charge(amount)
        if response.success:
            payment_record["status"] = "completed"
            self.db.update("payments", payment_record)
        return response.success

# ✅ GOOD — SRP (separate concerns), OCP (add strategies without modifying processor), DIP (depends on abstraction)
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

@dataclass
class PaymentResult:
    success: bool
    transaction_id: str | None = None

class PaymentGateway(Protocol):
    def charge(self, amount: float, currency: str) -> PaymentResult: ...

class PaymentRepository(Protocol):
    def save(self, record: dict) -> None: ...
    def update_status(self, order_id: int, status: str) -> None: ...

class PaymentProcessor:
    def __init__(self, gateway: PaymentGateway, repository: PaymentRepository):
        self.gateway = gateway
        self.repository = repository

    def process(self, order_id: int, amount: float, currency: str = "USD") -> PaymentResult:
        result = self.gateway.charge(amount, currency)
        
        if result.success:
            record = {
                "order_id": order_id,
                "amount": amount,
                "currency": currency,
                "status": "completed",
                "transaction_id": result.transaction_id
            }
            self.repository.save(record)
        
        return result
```

### Pattern 2: Composition Over Inheritance

```python
# ❌ BAD — Deep inheritance tree, fragile base class, violates LSP when adding specialized behavior
class NotificationService:
    def send(self, message: str): ...

class EmailNotification(NotificationService):
    def send(self, message: str): ...  # Overrides entire method for email-specific logic
	
class SMSNotification(NotificationService):
    def send(self, message: str): ...  # Duplicates validation logic from parent

# ✅ GOOD — Composition with strategy pattern, open/closed compliant
from abc import ABC, abstractmethod
import smtplib
import requests

class NotificationStrategy(ABC):
    @abstractmethod
    def deliver(self, recipient: str, message: str) -> bool: ...

class EmailNotifier(NotificationStrategy):
    def deliver(self, recipient: str, message: str) -> bool:
        # Email-specific implementation
        return True  # smtp send logic here

class SMSNotifier(NotificationStrategy):
    def deliver(self, recipient: str, message: str) -> bool:
        # SMS API call logic here
        return True  # requests post to twilio/etc

class NotificationService:
    """Composable service — behavior injected at initialization or runtime."""
    
    def __init__(self, strategy: NotificationStrategy):
        self.strategy = strategy

    def send(self, recipient: str, message: str) -> bool:
        return self.strategy.deliver(recipient, message)

# Usage: swap strategies without modifying class hierarchy
service = NotificationService(EmailNotifier())
service.send("user@example.com", "Hello")
```

### Pattern 3: KISS & YAGNI Applied to API Routing

```python
# ❌ BAD — Over-engineered factory pattern for a simple routing table (YAGNI + violates KISS)
class RouteHandlerFactory:
    @staticmethod
    def create(handler_type: str):
        if handler_type == "users":
            return UserHandler()
        elif handler_type == "orders":
            return OrderHandler()
        # ... 20 more branches
        raise ValueError(f"Unknown route: {handler_type}")

# ✅ GOOD — Direct mapping, simple, readable (KISS)
from typing import Dict, Type, Callable
import asyncio

RouteMap: Dict[str, Callable] = {
    "/users": handle_users,
    "/orders": handle_orders,
    "/products": handle_products,
}

def route_request(path: str, request_data: dict) -> dict:
    handler = RouteMap.get(path)
    if not handler:
        return {"status": 404, "error": "Not found"}
    return handler(request_data)
```

---

## Constraints

### MUST DO
- Enforce Single Responsibility: split modules when they handle more than one distinct business capability
- Depend on abstractions (Protocols, ABCs, traits, interfaces) not concrete classes
- Keep inheritance depth to 2 levels maximum; prefer composition for behavior reuse
- Apply YAGNI ruthlessly: do not abstract until a second concrete implementation exists
- Document public interfaces with clear preconditions, postconditions, and error contracts

### MUST NOT DO
- Create "manager" or "utility" classes that accumulate unrelated functions (God classes)
- Use inheritance to share code — use composition or extraction of shared logic into standalone modules
- Implement factory patterns for simple object creation when direct instantiation is clearer
- Add abstraction layers ("because it might be needed later") without a current concrete requirement
- Violate LSP by overriding methods in subclasses to throw `NotImplementedError` or add unexpected side effects

---

## Output Template

When auditing or designing software architecture, produce:

1. **Principle Violations Found** — Specific classes/modules violating SOLID/KISS/YAGNI with line references
2. **Refactoring Proposal** — Concrete steps to restore compliance (split modules, introduce abstractions, extract strategies)
3. **Dependency Map Summary** — Current coupling score and target architecture state
4. **Code Samples** — Before/after implementations demonstrating the corrected pattern
5. **Trade-off Analysis** — Flexibility gains vs. added complexity from proposed changes

---

## Related Skills

| Skill | Purpose |
|---|---|
| `coding-code-review` | Catches design violations during PR reviews before they reach production |
| `coding-design-patterns` | Provides specific reusable solutions (Observer, Factory, etc.) when composition alone isn't enough |
| `coding-refactoring` | Systematic technique for incrementally improving structure without changing external behavior |
