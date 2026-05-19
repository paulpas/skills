---
name: software-architecture
description: Implements and evaluates architectural patterns (hexagonal, clean, microservices, event-driven) with concrete Python examples to structure maintainable, scalable systems.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  triggers: software architecture, hexagonal architecture, clean architecture, event-driven design, system design, dependency inversion, bounded contexts
  role: implementation
  scope: implementation
  output-format: code
  content-types: [code, guidance, examples, do-dont]
  related-skills: modular-design, dependency-injection, error-handling
---

# Software Architecture Patterns

Implements and evaluates structural patterns — hexagonal, clean, event-driven, microservices — to separate volatile domains from stable infrastructure, enforce dependency inversion, and produce systems where business logic remains independently testable and framework-agnostic.

## TL;DR Checklist

- [ ] Map bounded contexts before writing any implementation code
- [ ] Verify dependencies flow inward toward core, never outward
- [ ] Declare ports (interfaces) in domain layer, implement adapters in outer layers
- [ ] Wire all dependencies at the composition root via constructor injection
- [ ] Enforce layer boundaries with lint rules or static analysis
- [ ] Document architectural decisions and trade-offs

---

## When to Use

Use this skill when:

- Designing a new application from scratch and need to establish directory layout, boundary contracts, and dependency wiring conventions before writing implementation code.
- Refactoring a monolithic, tightly coupled codebase — extract interfaces first, then peel adapters outward into separate modules.
- Planning integration with external systems (payment gateways, message brokers, third-party APIs) where the core domain logic must never change when those systems evolve.
- Resolving tight coupling between business rules and infrastructure concerns — e.g., service methods that directly import SQLAlchemy sessions or Django models.
- Setting up a team's project directory layout so that every developer can locate domain models, use-case orchestrators, and infrastructure adapters without guessing.
- Onboarding engineers to an existing architecture by producing ASCII diagrams, dependency graphs, and migration plans from the current state to the target pattern.

---

## When NOT to Use

Avoid architectural patterns for:

- Simple scripts or CLI tools under ~500 lines where layered abstractions add more boilerplate than value.
- Rapid prototypes, hackathon projects, or proof-of-concepts where execution speed and developer velocity outweigh long-term maintainability.
- Teams lacking discipline to enforce boundary rules — patterns decay quickly without governance (lint rules, code reviews, CI checks).
- Projects whose entire domain *is* infrastructure (e.g., a thin wrapper around a single SaaS API) — there is no core logic to protect.

---

## Core Workflow

1. **Identify Bounded Contexts** — Map business capabilities to distinct domains. Define explicit boundaries and data contracts between them. Ask: "Which parts of this system change at different paces, for different reasons?" Each context should have its own vocabulary (ubiquitous language) and own persistence strategy. **Checkpoint:** Each context must be independently testable and deployable — if you cannot write a full unit test suite for one context without mocking another, the boundary is wrong.

2. **Select Core Pattern** — Choose based on complexity and change frequency: Hexagonal/Clean for domain-centric applications where business rules are the primary asset; Event-Driven for asynchronous workflows with decoupled side effects (notifications, analytics, inventory); Microservices for teams needing independent scaling and deployment cadences. **Checkpoint:** Verify that dependencies flow inward toward the core, never outward — the innermost layer must not import from outer layers.

3. **Define Ports and Adapters** — Declare interfaces (ports) in the domain or application layer. Implement concrete adapters (database drivers, HTTP clients, message brokers, file systems) in the infrastructure layer. The core domain must never import `sqlalchemy`, `requests`, or any external framework. **Checkpoint:** Domain code compiles and passes all unit tests even when every adapter is replaced with a no-op stub.

4. **Wire Dependency Injection** — Instantiate adapters at runtime (usually `main.py` or the framework entry point) and inject them into use-case handlers via constructor parameters. Avoid service locators, global singletons, or factory functions scattered across modules. The composition root is the only place that knows about concrete implementations. **Checkpoint:** Trace imports from `main` inward — if you cannot trace every dependency back to a single wiring file, the pattern has decayed.

5. **Enforce Boundaries** — Set up lint rules (`flake8-import-order`, `deptry`, or `isort`) and static analysis gates (mypy with explicit import paths) to prevent cross-layer imports. Add pre-commit hooks that fail CI if infrastructure code imports from domain modules. **Checkpoint:** Catch inward-flowing dependency violations in CI before they reach main — no PR should merge a file that breaks the boundary contract.

---

## Implementation Patterns

### Pattern 1: Hexagonal Architecture (Ports & Adapters)

Hexagonal architecture — also called Ports and Adapters — places business logic at the center, surrounded by ports (abstract interfaces) on one side and concrete adapters on the other. Infrastructure hooks into ports from the outside; the domain never knows they exist. This pattern excels when the core rules are stable but external systems (databases, payment providers, notification services) change frequently.

```python
"""Domain layer: pure business logic with zero infrastructure imports."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol


# --- Domain Model (immutable value object) ---

@dataclass(frozen=True, slots=True)
class Order:
    """Immutable representation of an order within the bounded context."""
    id: str
    customer_id: str
    total_amount: float

    def is_valid(self) -> bool:
        """Validate business invariants on the domain model."""
        if not self.id or not self.customer_id:
            return False
        if self.total_amount <= 0:
            return False
        return True


# --- Port: Abstract interface declared in domain, implemented elsewhere ---

class OrderRepository(Protocol):
    """Contract for persisting and retrieving orders.

    Implementations live in the infrastructure layer (SQLAlchemy, Redis,
    mock adapters for tests). The domain depends only on this protocol.
    """

    @abstractmethod
    def get_by_id(self, order_id: str) -> Order | None: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...


# --- Use Case: depends on port, not implementation ---

class OrderProcessor:
    """Orchestrates order processing logic.

    Depends exclusively on the OrderRepository port. Can be instantiated
    with any concrete adapter — database, cache, or in-memory stub for tests.
    """

    def __init__(self, repo: OrderRepository) -> None:
        self._repo = repo

    def process(self, order_id: str) -> Order:
        """Fetch an order, validate it, and persist any state changes.

        Args:
            order_id: Unique identifier of the order to process.

        Returns:
            The validated Order instance.

        Raises:
            ValueError: If the order does not exist or fails validation.
        """
        order = self._repo.get_by_id(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")
        if not order.is_valid():
            raise ValueError(f"Order {order_id} failed validation")
        # Pure business logic here — no DB, HTTP, or framework imports.
        return order


# --- ❌ BAD — Tight coupling: business logic directly imports infrastructure ---

class BadOrderService:
    """Demonstrates the anti-pattern of hard-coding concrete dependencies."""

    def __init__(self) -> None:
        # Concrete implementation chosen at class definition time.
        # Cannot be swapped without modifying this class source.
        self.db = MySQLConnection("localhost", "orders_db")  # type: ignore[assignment, name-defined]

    def process_order(self, order_id: str) -> dict:
        """Mixes business rules with DB access — violates dependency inversion."""
        raw_data = self.db.query(  # type: ignore[union-attr]
            "SELECT * FROM orders WHERE id = %s", [order_id]
        )
        # ... business rules mixed with DB access ...
        return {"status": "processed"}


# --- ✅ GOOD — Infrastructure adapter (injected at composition root) ---

class SQLAlchemyOrderRepository:
    """SQLAlchemy-backed implementation of OrderRepository port.

    Lives in the infrastructure/ layer alongside other data adapters.
    Only this file imports SQLAlchemy; domain code is untouched.
    """

    def __init__(self, session_factory: object) -> None:  # type: ignore[type-arg]
        """Initialize with an ORM session factory provided by DI container.

        Args:
            session_factory: Factory that produces DB sessions at runtime.
        """
        self._session = session_factory

    def get_by_id(self, order_id: str) -> Order | None:
        result = self._session.query(DBOrder).filter(DBOrder.id == order_id).first()  # type: ignore[name-defined]
        if result is None:
            return None
        return Order(
            id=result.id,  # type: ignore[union-attr]
            customer_id=result.customer_id,  # type: ignore[union-attr]
            total_amount=float(result.total),  # type: ignore[union-attr]
        )

    def save(self, order: Order) -> None:
        db_order = DBOrder.from_domain(order)  # type: ignore[name-defined]
        self._session.add(db_order)
        self._session.commit()


# --- Composition root (main.py or app factory) ---
# from sqlalchemy.orm import sessionmaker
# SessionLocal = sessionmaker(bind=engine)
# repo = SQLAlchemyOrderRepository(SessionLocal)
# processor = OrderProcessor(repo)  # All wiring happens here, nowhere else.

```

---

### Pattern 2: Event-Driven Decoupling for Side Effects

Core business operations should emit domain events rather than call side-effect services directly. Email notifications, analytics tracking, inventory reservation, and search-index updates are *consequences* of the core action — they belong in event handlers that subscribe to those events, not in the same method that performs the primary transaction. This keeps the core logic fast, testable, and resilient to notification or analytics outages.

```python
"""Event-driven side-effect decoupling for domain operations."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol


# --- Domain event (immutable, serializable) ---

@dataclass(frozen=True)
class PaymentProcessed:
    """Domain event emitted when a payment completes successfully."""
    txn_id: str
    user_email: str
    amount: float

    def to_dict(self) -> dict:
        """Serialize for transport to external message brokers."""
        return {
            "txn_id": self.txn_id,
            "user_email": self.user_email,
            "amount": self.amount,
            "event_type": "payment_processed",
        }


# --- Port: Event publisher declared in domain layer ---

class EventPublisher(Protocol):
    """Contract for publishing domain events.

    Implementations route events to RabbitMQ, Kafka, SQS, or an
    in-memory list for testing. Domain code knows only this interface.
    """

    @abstractmethod
    def publish(self, event: PaymentProcessed) -> None: ...


# --- Core domain logic (pure transaction + event emission) ---

@dataclass(frozen=True)
class Payment:
    payment_id: str
    user_email: str
    amount: float


class PaymentCore:
    """Processes payments and emits events. Does not send emails or track analytics."""

    def __init__(self, gateway: object, events: EventPublisher) -> None:  # type: ignore[type-arg]
        self._gateway = gateway
        self._events = events

    def process(self, payment: Payment) -> str:
        """Charge the gateway and publish a domain event on success.

        Args:
            payment: Payment request data from the application layer.

        Returns:
            The transaction ID returned by the payment gateway.

        Raises:
            RuntimeError: If the payment gateway returns an error status.
        """
        result = self._gateway.charge(payment)  # type: ignore[union-attr]
        # Core logic completes; side effects are decoupled.
        self._events.publish(PaymentProcessed(
            txn_id=result.txn_id,  # type: ignore[attr-defined]
            user_email=payment.user_email,
            amount=payment.amount,
        ))
        return result.txn_id  # type: ignore[union-attr]


# --- ❌ BAD — Synchronous side effects inside core logic ---

class BadPaymentService:
    """Demonstrates coupling core payment flow with notification and analytics."""

    def process_payment(self, payment: Payment) -> str:
        result = self._charge_gateway(payment)  # type: ignore[name-defined]
        # Blocks main thread, tightly couples to notification service.
        # If email provider is down, the entire payment fails.
        self._email_service.send_confirmation(  # type: ignore[union-attr]
            payment.user_email, result.txn_id
        )
        # Analytics tracking now blocks the response too.
        self._analytics_tracker.log_event(  # type: ignore[union-attr]
            "payment_complete", {"amount": payment.amount}
        )
        return result.txn_id


# --- ✅ GOOD — Handlers subscribe to events independently ---

class EmailNotificationHandler:
    """Handles the email side effect; completely decoupled from PaymentCore."""

    def __init__(self, event_bus: EventPublisher) -> None:  # type: ignore[assignment]
        self._event_bus = event_bus
        event_bus.publish = self._wrap_publish(event_bus.publish)  # type: ignore[method-assign]

    def _wrap_publish(self, original: object) -> object:  # type: ignore[type-arg]
        """Register this handler as an event listener."""
        def wrapper(event: PaymentProcessed) -> None:
            if isinstance(event, PaymentProcessed):
                self._send_email(event.user_email, event.txn_id)
            original(event)  # type: ignore[union-attr]
        return wrapper

    @staticmethod
    def _send_email(email: str, txn_id: str) -> None:
        """Send confirmation email (external to domain)."""
        pass  # Implementation lives in infrastructure/


class AnalyticsHandler:
    """Handles the analytics side effect; independent of payment processing."""

    def __init__(self, event_bus: EventPublisher) -> None:  # type: ignore[assignment]
        self._event_bus = event_bus
        event_bus.publish = self._wrap_publish(event_bus.publish)  # type: ignore[method-assign]

    def _wrap_publish(self, original: object) -> object:  # type: ignore[type-arg]
        def wrapper(event: PaymentProcessed) -> None:
            if isinstance(event, PaymentProcessed):
                pass  # Send to analytics pipeline (infrastructure layer)
            original(event)  # type: ignore[union-attr]
        return wrapper

```

---

### Pattern 3: Dependency Inversion at the Composition Root

Dependency inversion means high-level modules (use cases, domain services) declare *what* they need through interfaces; low-level modules (database drivers, HTTP clients) provide *how* it is done. The wiring happens once at the composition root — typically `main.py` or a framework entry point — so that no part of the codebase reaches for concrete implementations.

```python
"""Composition root: single file where all dependencies are wired together."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """External configuration loaded from environment or config file."""
    database_url: str
    redis_url: str | None = None
    notification_timeout_seconds: float = 5.0


def build_application(config: AppConfig) -> object:  # type: ignore[type-arg]
    """Build the full application graph with concrete adapters injected.

    This is the *only* place in the codebase that knows about concrete
    implementations (SQLAlchemy, Redis client, HTTP transport). Every other
    module depends only on protocols and abstract interfaces.

    Args:
        config: Runtime configuration loaded from env/config files.

    Returns:
        A fully wired OrderProcessor instance ready for use.
    """
    # --- Infrastructure adapters ---
    session_factory = create_session_factory(config.database_url)  # type: ignore[name-defined]
    repo = SQLAlchemyOrderRepository(session_factory)

    # --- Event transport (could be RabbitMQ in prod, list in tests) ---
    event_bus = InMemoryEventPublisher()  # type: ignore[name-defined]

    # --- Domain use cases get only interfaces ---
    processor = OrderProcessor(repo)
    notification = EmailNotificationHandler(event_bus)  # type: ignore[name-defined]
    analytics = AnalyticsHandler(event_bus)  # type: ignore[name-defined]

    return processor

```

---

## Constraints

### MUST DO
- Keep core business rules pure and framework-independent — no Django, FastAPI, SQLAlchemy, or boto3 imports in the domain layer. If a dependency changes, only adapter files should need updates.
- Inject dependencies via protocols, abstract base classes, or structural interfaces — never concrete implementations. Constructor injection is the default; avoid property-based or method-level injection patterns that obscure data flow.
- Document architectural decisions with Architecture Decision Records (ADRs) for major structural choices. Each ADR should capture: context, decision made, consequences (both positive and negative), and when to revisit.
- Write unit tests for core logic using lightweight in-memory adapters instead of mocking frameworks. In-memory implementations are easier to read, debug, and verify than mocked interfaces with complex call expectations.
- Structure directories to reflect architecture boundaries (`domain/`, `application/`, `infrastructure/`). File paths should signal layer membership at a glance — if you need to read imports to find where a type is defined, the layout has failed.

### MUST NOT DO
- Place business logic inside controllers, routes, request handlers, or CLI argument parsers. Controllers should only parse requests, invoke use cases, and format responses — no `if` statements that check validation rules or calculate prices.
- Create "God classes" that handle multiple bounded contexts or violate the Single Responsibility Principle. A class with more than one reason to change has already failed this rule; split it along context boundaries before adding new features.
- Over-engineer simple features with full layered abstractions when a straightforward procedural structure suffices. Not every function needs a protocol, adapter, and use-case wrapper — reserve patterns for the parts of the system that actually vary.
- Let database schema decisions dictate domain model structure. If your ORM models force you to expose foreign keys as public attributes or split a value object across multiple tables, the mapping is wrong — keep domain semantics separate from persistence details.

---

## Output Template

When reviewing or designing architecture, produce:

1. **ASCII Architecture Diagram** — Clear representation of layers, ports, adapters, and data flow directions. Use consistent box-and-arrow notation showing inbound/outbound dependency edges.
2. **Bounded Contexts** — List of domains with their explicit contracts (input/output types) and responsibilities. For each context, identify the ubiquitous language terms that distinguish it from others.
3. **Dependency Graph** — Explicit list of allowed imports per layer (e.g., `infrastructure -> application`, never `application -> infrastructure`). Flag any violations as blocking issues.
4. **Refactoring Migration Plan** — Step-by-step path to move from current structure to target pattern: extract interfaces → inject dependencies → move adapters → add boundary enforcement lint rules → update CI checks.
5. **Trade-off Analysis** — Concrete pros/cons of the selected pattern versus alternatives, evaluated against the project's scale (lines of code), team size, deployment frequency, and operational budget.

---

## Related Skills

| Skill | Purpose |
|---|---|
| `modular-design` | Applies when breaking a monolith into independently deployable modules or packages with explicit public APIs |
| `dependency-injection` | Covers advanced DI containers, lifecycle management (scoped, transient, singleton), and framework integration for wiring at the composition root |
| `error-handling` | Provides structured error taxonomy that aligns with clean architecture boundaries — domain errors vs. infrastructure errors handled differently at layer edges |
