---
name: architecture-design
description: Applies GoF design patterns, SOLID, DRY, and YAGNI principles to design clean, maintainable, and extensible software architectures.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  triggers: architecture, design patterns, SOLID, GoF, DRY, YAGNI, refactoring, modular design
  role: implementation
  scope: implementation
  output-format: code
  content-types: [code, guidance, do-dont, examples]
  related-skills: coding/design-patterns,coding/error-handling,coding/modular-design
---

# Architecture & Design Patterns

I apply established software architecture principles — GoF design patterns, SOLID, DRY, and YAGNI — to produce clean, maintainable, and extensible code. I help you choose the right pattern for a problem, refactor messy code into well-structured modules, and enforce design constraints that prevent architectural decay.

## TL;DR Checklist

- [ ] Identify the core responsibility of each class/module (Single Responsibility)
- [ ] Choose a GoF pattern only when the problem matches its intent (Factory for object creation, Strategy for interchangeable algorithms, Observer for event distribution, Decorator for dynamic behavior, Adapter for interface mismatch)
- [ ] Apply DRY: extract repeated logic into a single source of truth
- [ ] Apply YAGNI: do not build abstractions for requirements that do not exist
- [ ] Ensure open/closed design — extend via new classes, not modified ones
- [ ] Program to interfaces/abstract types, never to concrete implementations
- [ ] Validate every design decision against the 5 Laws of Elegant Defense (code-philosophy skill)

## When to Use

- Starting a new module or service with unclear boundaries
- Refactoring a class that has grown too large (>300 lines) or has multiple responsibilities
- Introducing a new algorithm or strategy that will have multiple variants
- Building systems that need to be extended with new types without modifying existing code (e.g., plugin architectures, payment processors, notification channels)
- Decoupling components that need to communicate without tight coupling (event-driven systems, pub/sub)
- Wrapping third-party libraries or legacy code with incompatible interfaces
- Adding cross-cutting concerns (logging, caching, authentication) to existing classes

## When NOT to Use

- Simple scripts or one-off utilities with no expected evolution
- Problems with no anticipated variation — do not over-engineer with patterns
- When the overhead of indirection exceeds the benefit (small teams, short-lived projects)
- As a replacement for understanding the domain — patterns are tools, not answers
- When you can solve the problem with composition instead of inheritance

## Core Workflow

1. **Analyze the Problem Space**
   - Identify responsibilities that are changing at different rates
   - List the concrete types and behaviors that may vary
   - Determine coupling points and dependency direction

   **Checkpoint**: You can draw a box-and-arrow diagram of the current structure and point to each coupling problem.

2. **Select the Pattern**
   - Object creation needed with variation? → Factory Method or Abstract Factory
   - Algorithm or strategy needs to swap at runtime? → Strategy
   - One shared instance is the correct model? → Singleton (use cautiously)
   - Components must react to state changes? → Observer
   - Behavior must be added dynamically? → Decorator
   - Incompatible interface must appear compatible? → Adapter
   - Class hierarchy is too deep or rigid? → Prefer composition over inheritance

   **Checkpoint**: You can state the pattern's intent and why it fits in one sentence.

3. **Apply SOLID Constraints**
   - **SRP**: Each class has exactly one reason to change
   - **OCP**: New behavior comes from new classes, not edits to existing ones
   - **LSP**: Subtypes must be substitutable without breaking caller expectations
   - **ISP**: No interface forces a client to depend on methods it does not use
   - **DIP**: High-level modules depend on abstractions, not concrete details

   **Checkpoint**: Walk through each principle and confirm the design satisfies it.

4. **Enforce DRY and YAGNI**
   - Extract duplicated logic into shared functions/classes
   - Remove any abstraction that has only one consumer or no imminent need for a second variant
   - Ask: "If this code never changes again, would I still need this indirection?"

   **Checkpoint**: Every piece of logic exists in exactly one place. No "future-proof" abstractions.

5. **Implement and Validate**
   - Write tests for the public interfaces, not internal implementations
   - Verify that adding a new variant requires zero changes to existing client code
   - Ensure dependency direction flows inward toward abstractions

## Implementation Patterns

### Factory Pattern

Use when object creation is complex, when the exact type depends on runtime data, or when you want to hide construction logic.

```python
# BAD: Concrete types are created directly throughout the codebase — every caller must know the exact class
class PaymentProcessor:
    def process(self, amount: float) -> dict:
        if self.method == "stripe":
            gateway = StripeGateway()
        elif self.method == "paypal":
            gateway = PayPalGateway()
        elif self.method == "square":
            gateway = SquareGateway()
        else:
            raise ValueError(f"Unknown payment method: {self.method}")
        return gateway.charge(amount)
```

```python
# GOOD: Factory isolates creation logic behind a single entry point; adding a new method requires zero changes to PaymentProcessor
from abc import ABC, abstractmethod
from typing import Protocol


class PaymentGateway(Protocol):
    def charge(self, amount: float) -> dict: ...


class StripeGateway:
    def charge(self, amount: float) -> dict:
        return {"provider": "stripe", "status": "charged", "amount": amount}


class PayPalGateway:
    def charge(self, amount: float) -> dict:
        return {"provider": "paypal", "status": "charged", "amount": amount}


class SquareGateway:
    def charge(self, amount: float) -> dict:
        return {"provider": "square", "status": "charged", "amount": amount}


class PaymentFactory:
    _gateways: dict[str, type[PaymentGateway]] = {
        "stripe": StripeGateway,
        "paypal": PayPalGateway,
        "square": SquareGateway,
    }

    @classmethod
    def create_gateway(cls, method: str) -> PaymentGateway:
        gateway_cls = cls._gateways.get(method)
        if gateway_cls is None:
            raise ValueError(f"Unsupported payment method: {method}")
        return gateway_cls()


# Usage — PaymentProcessor knows nothing about concrete gateways
class PaymentProcessor:
    def __init__(self, factory: PaymentFactory) -> None:
        self._factory = factory

    def process(self, method: str, amount: float) -> dict:
        gateway = self._factory.create_gateway(method)
        return gateway.charge(amount)
```

### Strategy Pattern

Use when you have multiple algorithms that are interchangeable and may change independently.

```python
# BAD: Algorithm variants are scattered in conditional branches — adding a new sorting strategy requires editing every caller
class DataAnalyzer:
    def analyze(self, data: list[float], strategy: str) -> float:
        if strategy == "mean":
            return sum(data) / len(data)
        elif strategy == "median":
            sorted_data = sorted(data)
            n = len(sorted_data)
            return sorted_data[n // 2] if n % 2 else (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
        elif strategy == "weighted":
            weights = [1.5 if v > 100 else 1.0 for v in data]
            total_w = sum(weights)
            return sum(v * w for v, w in zip(data, weights)) / total_w
        raise ValueError(f"Unknown strategy: {strategy}")
```

```python
# GOOD: Each strategy is a self-contained class; adding a new strategy adds a new file, not new branches
from abc import ABC, abstractmethod
from typing import Protocol


class AggregationStrategy(Protocol):
    def compute(self, data: list[float]) -> float: ...


class MeanStrategy:
    def compute(self, data: list[float]) -> float:
        return sum(data) / len(data)


class MedianStrategy:
    def compute(self, data: list[float]) -> float:
        sorted_data = sorted(data)
        n = len(sorted_data)
        return sorted_data[n // 2] if n % 2 else (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2


class WeightedStrategy:
    def compute(self, data: list[float]) -> float:
        weights = [1.5 if v > 100 else 1.0 for v in data]
        total_w = sum(weights)
        return sum(v * w for v, w in zip(data, weights)) / total_w


class DataAnalyzer:
    def __init__(self, strategy: AggregationStrategy) -> None:
        self._strategy = strategy

    def analyze(self, data: list[float]) -> float:
        return self._strategy.compute(data)


# Usage — swap strategies at runtime without modifying DataAnalyzer
analyzer = DataAnalyzer(MeanStrategy())
result = analyzer.analyze([10, 20, 30])
```

### Observer Pattern

Use when one change must propagate to multiple dependents, and you want to keep them loosely coupled.

```python
# BAD: Tight coupling — the subject must know every subscriber type and method name
class StockPrice:
    def __init__(self) -> None:
        self._price: float = 0.0

    def set_price(self, price: float) -> None:
        self._price = price
        # Hard-coded subscribers — adding a new notification type requires modifying StockPrice
        self._notify_email(price)
        self._notify_dashboard(price)
        self._notify_alert_system(price)

    def _notify_email(self, price: float) -> None:
        print(f"EMAIL: Price is ${price:.2f}")

    def _notify_dashboard(self, price: float) -> None:
        print(f"DASHBOARD: Price updated to ${price:.2f}")

    def _notify_alert_system(self, price: float) -> None:
        print(f"ALERT: Threshold check for ${price:.2f}")
```

```python
# GOOD: Loose coupling — the subject knows nothing about observers; new subscribers are added by registration
from abc import ABC, abstractmethod
from typing import Any


class Observer(ABC):
    @abstractmethod
    def update(self, subject: Any, event: str, data: Any) -> None: ...


class StockSubject:
    def __init__(self) -> None:
        self._observers: list[Observer] = []
        self._price: float = 0.0

    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def set_price(self, price: float) -> None:
        if self._price == price:
            return
        self._price = price
        self._notify_all(price)

    def _notify_all(self, price: float) -> None:
        for observer in self._observers:
            observer.update(self, "price_change", price)


class EmailNotifier(Observer):
    def update(self, subject: Any, event: str, data: Any) -> None:
        print(f"EMAIL: Price is ${data:.2f}")


class DashboardUpdater(Observer):
    def update(self, subject: Any, event: str, data: Any) -> None:
        print(f"DASHBOARD: Price updated to ${data:.2f}")


# Usage — add new observers without touching StockSubject
stock = StockSubject()
stock.attach(EmailNotifier())
stock.attach(DashboardUpdater())
stock.set_price(150.00)
```

### Decorator Pattern

Use when you need to add responsibilities to individual objects dynamically, without affecting other instances.

```python
# BAD: Subclassing for every combination of behavior explodes the class hierarchy
class Coffee:
    def cost(self) -> float:
        return 5.0

    def description(self) -> str:
        return "Coffee"


class MilkCoffee(Coffee):
    def cost(self) -> float:
        return super().cost() + 1.5

    def description(self) -> str:
        return super().description() + ", Milk"


class SugarMilkCoffee(MilkCoffee):
    def cost(self) -> float:
        return super().cost() + 0.5

    def description(self) -> str:
        return super().description() + ", Sugar"
    # Adding WhipCoffee, SugarMilkWhipCoffee, etc. creates exponential subclass growth
```

```python
# GOOD: Decorator wraps any beverage component; combinations are infinite with zero new classes
from abc import ABC, abstractmethod


class Beverage(ABC):
    @abstractmethod
    def cost(self) -> float: ...

    @abstractmethod
    def description(self) -> str: ...


class PlainCoffee(Beverage):
    def cost(self) -> float:
        return 5.0

    def description(self) -> str:
        return "Coffee"


class BeverageDecorator(Beverage):
    def __init__(self, wrapped: Beverage) -> None:
        self._wrapped = wrapped

    def cost(self) -> float:
        return self._wrapped.cost()

    def description(self) -> str:
        return self._wrapped.description()


class Milk(BeverageDecorator):
    def cost(self) -> float:
        return super().cost() + 1.5

    def description(self) -> str:
        return f"{super().description()}, Milk"


class Sugar(BeverageDecorator):
    def cost(self) -> float:
        return super().cost() + 0.5

    def description(self) -> str:
        return f"{super().description()}, Sugar"


# Usage — compose any combination at runtime with O(1) class count
coffee: Beverage = PlainCoffee()
coffee = Milk(coffee)
coffee = Sugar(coffee)
print(coffee.description())  # "Coffee, Milk, Sugar"
print(coffee.cost())         # 7.0
```

### Adapter Pattern

Use when you must integrate a component with an incompatible interface.

```python
# BAD: Caller code is littered with format conversions — every new data source adds more ad-hoc conversion
class ReportGenerator:
    def generate(self, data_source: dict) -> str:
        # Tightly coupled to a specific CSV format
        if "records" in data_source:
            rows = data_source["records"]
        elif "results" in data_source:
            rows = data_source["results"]
        elif isinstance(data_source, str):
            rows = [line.split(",") for line in data_source.strip().split("\n")]
        else:
            raise ValueError("Unsupported data format")
        return "\n".join(str(row) for row in rows)
```

```python
# GOOD: Adapter isolates format conversion; new sources are handled by new adapter classes
from abc import ABC, abstractmethod
from typing import Any


class DataAdapter(ABC):
    @abstractmethod
    def get_records(self) -> list[dict[str, Any]]: ...


class CSVAdapter(DataAdapter):
    def __init__(self, raw_data: str) -> None:
        self._rows = [line.split(",") for line in raw_data.strip().split("\n")]

    def get_records(self) -> list[dict[str, Any]]:
        return [dict(zip(["id", "name", "value"], row)) for row in self._rows]


class JSONAPIAdapter(DataAdapter):
    def __init__(self, api_response: dict) -> None:
        self._records = api_response.get("records", api_response.get("results", []))

    def get_records(self) -> list[dict[str, Any]]:
        return self._records


class ReportGenerator:
    def __init__(self, adapter: DataAdapter) -> None:
        self._adapter = adapter

    def generate(self) -> str:
        records = self._adapter.get_records()
        return "\n".join(str(record) for record in records)


# Usage — swap data sources without touching ReportGenerator
csv_adapter = CSVAdapter("1,Alice,100\n2,Bob,200")
json_adapter = JSONAPIAdapter({"records": [{"id": 1, "name": "Alice", "value": 100}]})
report = ReportGenerator(csv_adapter)
print(report.generate())
```

### Singleton Pattern

Use when exactly one instance must exist (e.g., configuration, connection pool). Prefer dependency injection over global state.

```python
# BAD: Global mutable state — impossible to test in isolation, invisible dependencies
class DatabaseConnection:
    _instance = None
    _connection_string = "postgres://localhost/mydb"

    def __new__(cls) -> "DatabaseConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connected = False
        return cls._instance

    def connect(self) -> None:
        self._connected = True
        print(f"Connected to {self._connection_string}")

    def query(self, sql: str) -> list[dict]:
        if not self._connected:
            raise RuntimeError("Not connected")
        # ...
        return []


# Any code can call DatabaseConnection() and get the shared instance — no visibility
conn = DatabaseConnection()
conn.connect()
result = conn.query("SELECT * FROM users")
```

```python
# GOOD: Singleton is explicit, testable via injection, and documented with its intent
import threading
from typing import ClassVar


class DatabaseConnection:
    """Thread-safe singleton for database connections.
    
    Use dependency injection to pass this instance to components that need it.
    In tests, inject a mock instead.
    """

    _instance: ClassVar["DatabaseConnection | None"] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(cls, connection_string: str = "postgres://localhost/mydb") -> "DatabaseConnection":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._connection_string = connection_string
                    instance._connected = False
                    cls._instance = instance
        return cls._instance

    @classmethod
    def reset_for_testing(cls) -> None:
        """Reset the singleton instance — for testing only."""
        with cls._lock:
            cls._instance = None

    @property
    def connection_string(self) -> str:
        return self._connection_string

    def connect(self) -> None:
        if not self._connected:
            self._connected = True
            print(f"Connected to {self._connection_string}")

    def query(self, sql: str) -> list[dict]:
        if not self._connected:
            raise RuntimeError("Not connected")
        return []


# Usage — explicit and testable
DatabaseConnection.reset_for_testing()
conn = DatabaseConnection()
conn.connect()
```

### SOLID Principles — Single Responsibility

```python
# BAD: Class handles data retrieval, validation, formatting, AND persistence
class UserService:
    def create_user(self, data: dict) -> dict:
        # 1. Validation
        if not data.get("email") or "@" not in data["email"]:
            raise ValueError("Invalid email")
        if not data.get("name") or len(data["name"]) < 2:
            raise ValueError("Name too short")

        # 2. Persistence
        import sqlite3
        conn = sqlite3.connect("app.db")
        conn.execute(
            "INSERT INTO users (email, name) VALUES (?, ?)",
            (data["email"], data["name"])
        )
        conn.commit()

        # 3. Notification
        import smtplib
        server = smtplib.SMTP("localhost")
        server.sendmail("admin@app.com", data["email"], f"Welcome {data['name']}")

        # 4. Formatting
        return {
            "id": conn.execute("SELECT last_insert_rowid()").fetchone()[0],
            "message": f"User {data['name']} created successfully."
        }
```

```python
# GOOD: Each class has one responsibility — change email validation without touching persistence
from dataclasses import dataclass


@dataclass
class User:
    email: str
    name: str


class UserValidator:
    """Validates user data according to business rules."""

    def validate(self, data: dict) -> User:
        if not data.get("email") or "@" not in data["email"]:
            raise ValueError("Invalid email")
        if not data.get("name") or len(data["name"]) < 2:
            raise ValueError("Name must be at least 2 characters")
        return User(email=data["email"], name=data["name"])


class UserRepository:
    """Handles user persistence — technology-agnostic on the interface level."""

    def save(self, user: User) -> int:
        import sqlite3
        conn = sqlite3.connect("app.db")
        cursor = conn.execute(
            "INSERT INTO users (email, name) VALUES (?, ?)",
            (user.email, user.name)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id


class NotificationService:
    """Sends welcome notifications to new users."""

    def send_welcome(self, user: User) -> None:
        import smtplib
        server = smtplib.SMTP("localhost")
        server.sendmail("admin@app.com", user.email, f"Welcome {user.name}")


class UserService:
    """Coordinates the workflow — contains no business logic itself."""

    def __init__(
        self,
        validator: UserValidator,
        repository: UserRepository,
        notifier: NotificationService,
    ) -> None:
        self._validator = validator
        self._repository = repository
        self._notifier = notifier

    def create_user(self, data: dict) -> dict:
        user = self._validator.validate(data)
        user_id = self._repository.save(user)
        self._notifier.send_welcome(user)
        return {"id": user_id, "message": f"User {user.name} created successfully."}
```

### DRY — Don't Repeat Yourself

```python
# BAD: Validation logic duplicated across multiple endpoints
class UserEndpoint:
    def create(self, data: dict) -> dict:
        if not data.get("email"):
            return {"error": "Email required"}
        if not data.get("password"):
            return {"error": "Password required"}
        if len(data.get("password", "")) < 8:
            return {"error": "Password too short"}
        return self._save(data)

    def update(self, data: dict) -> dict:
        if not data.get("email"):
            return {"error": "Email required"}
        if not data.get("password"):
            return {"error": "Password required"}
        if len(data.get("password", "")) < 8:
            return {"error": "Password too short"}
        return self._save(data)

    def reset_password(self, data: dict) -> dict:
        if not data.get("email"):
            return {"error": "Email required"}
        if not data.get("password"):
            return {"error": "Password required"}
        if len(data.get("password", "")) < 8:
            return {"error": "Password too short"}
        return self._save(data)


# GOOD: Extracted into a reusable validator — all three endpoints share one source of truth
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    is_valid: bool = True
    errors: list[str] = field(default_factory=list)

    def add_error(self, error: str) -> None:
        self.is_valid = False
        self.errors.append(error)


class PasswordValidator:
    """Single source of truth for password and email validation rules."""

    def validate(self, data: dict[str, Any]) -> ValidationResult:
        result = ValidationResult()

        if not data.get("email"):
            result.add_error("Email required")
        elif "@" not in data.get("email", ""):
            result.add_error("Invalid email format")

        if not data.get("password"):
            result.add_error("Password required")
        elif len(data.get("password", "")) < 8:
            result.add_error("Password must be at least 8 characters")

        return result


class UserEndpoint:
    def __init__(self) -> None:
        self._validator = PasswordValidator()

    def create(self, data: dict) -> dict:
        result = self._validator.validate(data)
        if not result.is_valid:
            return {"error": "; ".join(result.errors)}
        return self._save(data)

    def update(self, data: dict) -> dict:
        result = self._validator.validate(data)
        if not result.is_valid:
            return {"error": "; ".join(result.errors)}
        return self._save(data)

    def reset_password(self, data: dict) -> dict:
        result = self._validator.validate(data)
        if not result.is_valid:
            return {"error": "; ".join(result.errors)}
        return self._save(data)

    def _save(self, data: dict) -> dict:
        return {"status": "saved"}
```

### YAGNI — You Ain't Gonna Need It

```python
# BAD: Abstraction built for a future requirement that never materializes
class NotificationChannel(ABC):
    """Generic notification channel — designed so we could add more types later."""

    @abstractmethod
    def send(self, message: str, recipient: str) -> bool: ...

    @abstractmethod
    def get_delivery_status(self, message_id: str) -> str: ...

    @abstractmethod
    def get_bounce_rate(self) -> float: ...


class EmailChannel(NotificationChannel):
    def send(self, message: str, recipient: str) -> bool:
        # Only used for email — but forced to implement methods for channels we don't have
        print(f"Sending email to {recipient}: {message}")
        return True

    def get_delivery_status(self, message_id: str) -> str:
        return "delivered"

    def get_bounce_rate(self) -> float:
        return 0.02


# Three methods for a feature that doesn't exist yet, all for a single email use case
```

```python
# GOOD: Simple, focused implementation — when email and SMS both exist, then abstract
class EmailService:
    """Sends email notifications. When SMS or push notifications are needed, create those separately."""

    def send(self, message: str, recipient: str) -> bool:
        print(f"Sending email to {recipient}: {message}")
        return True


class NotificationService:
    """Coordinates notifications using the services that actually exist."""

    def __init__(self, email_service: EmailService) -> None:
        self._email_service = email_service

    def notify_user(self, user_email: str, message: str) -> None:
        self._email_service.send(message, user_email)


# No abstraction until there are two or more concrete implementations
```

## Constraints

### MUST DO

- Apply **Single Responsibility Principle**: each class has exactly one reason to change
- Apply **Dependency Inversion**: depend on abstractions (interfaces, abstract classes), never concrete implementations
- Apply **Open/Closed Principle**: extend behavior by adding new classes, never by modifying existing ones
- Use **composition over inheritance** when the relationship is "has-a" rather than "is-a"
- Keep classes under 300 lines — if they grow larger, extract responsibilities into new classes
- Use Protocol or ABC to define interfaces — never a bare dict or tuple as a contract
- Apply **DRY**: when logic repeats three or more times, extract it
- Write tests for public interfaces, not internal methods
- Document the intent of each class at the top with a one-line docstring
- Inject dependencies through constructors — never call `Database()` or `Config()` inside business logic
- When choosing between patterns, prefer the one with the fewest moving parts that still solves the problem

### MUST NOT DO

- Use Singleton as a global variable pattern — it hides dependencies and breaks testability
- Apply a pattern when a simple function or class would suffice — patterns are for managing complexity, not adding it
- Create interfaces that exist only to be implemented once — that is over-engineering (YAGNI)
- Inherit from concrete classes — inherit from abstractions only
- Violate LSP by making a subtype override a parent method to do nothing or raise NotImplemented
- Split a class into many tiny classes that are only called in a single chain — this is "micro-responsibility" anti-pattern
- Use the Strategy pattern for logic that will never have a second variant (use an if/elif instead)
- Use the Factory pattern when object construction is trivial (just call `ClassName()` directly)
- Create a class hierarchy deeper than three levels
- Modify an existing class to support a new variant — create a new class and update the factory or registry instead
- Apply Observer when the event flow is a simple synchronous call chain (use a direct method call instead)

## Output Template

When this skill is active, the model produces output in the following structure:

1. **Problem Analysis**: One-paragraph assessment of the architectural problem
2. **Pattern Selection**: Which pattern(s) to apply and why, with reference to the specific pattern definition
3. **SOLID Validation**: Brief check of how the design satisfies each applicable principle
4. **Code Output**: Clean, typed Python code with BAD/GOOD examples where applicable
5. **Trade-off Note**: One sentence on what was simplified or what to watch for in the future

Example output format:

```
Problem: [description]
Pattern: [name] — [one-sentence justification]
SOLID: [SRP/OCP/LSP/ISP/DIP satisfied]

[Typed, documented code output with clear section headers]

Trade-off: [one-line note on trade-offs or future considerations]
```

## Related Skills

| Skill | Relationship | Purpose |
|-------|-------------|---------|
| coding/design-patterns | Adjacent | Deeper coverage of individual GoF pattern implementations |
| coding/error-handling | Adjacent | How to handle errors within architectural patterns |
| coding/modular-design | Adjacent | Module boundaries, cohesion, and coupling strategies |
| code-philosophy | Foundational | 5 Laws of Elegant Defense — underlying design philosophy |
| m0-foundation | Adjacent | Configuration and error handling patterns in trading platforms |
| signals-module | Adjacent | AI-driven signal architecture with multi-source aggregation |
