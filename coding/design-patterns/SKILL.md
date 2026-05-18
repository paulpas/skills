---
name: design-patterns
description: Applies GoF, SOLID, DRY, YAGNI, and KISS design principles to identify code smells, refactor toward proven patterns, and prevent architectural debt.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  triggers: design patterns, SOLID principles, GoF patterns, DRY code, YAGNI, KISS principle, code refactoring, architectural review
  role: implementation
  scope: implementation
  output-format: code
  content-types: [code, guidance, do-dont, examples]
  related-skills: code-philosophy,test-driven-development
---

# Design Patterns and SOLID Principles

Senior architect evaluating code against GoF, SOLID, DRY, YAGNI, and KISS principles. I identify architectural anti-patterns, recommend proven design patterns, and guide refactoring toward clean, maintainable code that resists future change.

## TL;DR Checklist

- [ ] Ask "What changes frequently?" before creating any abstraction
- [ ] Verify DRY/YAGNI/KISS compliance before applying any pattern
- [ ] Prefer composition over inheritance — every time
- [ ] Ensure every new class has a single, well-defined responsibility (SRP)
- [ ] Use the simplest pattern that solves the current problem
- [ ] Reference the applicable SOLID principle when explaining design decisions
- [ ] Confirm the abstraction solves a current problem, not a hypothetical one (YAGNI)

---

## When to Use

- Refactoring a class or module that does too many things (SRP violation)
- Tight coupling between modules that need independent testing or replacement
- Long if/else or switch chains that select behavior based on type or condition
- Object creation logic scattered across multiple places with duplicated factory logic
- Copy-pasted code blocks that share 80%+ similarity (DRY violation)
- Architecture reviews where structural debt is accumulating
- Onboarding new developers to a codebase with unclear abstractions
- Adding a new behavior or strategy to an existing system without modifying existing code (OCP)

---

## When NOT to Use

- Simple scripts or one-off utilities that will never change or be extended
- Code with only one concrete implementation and zero likelihood of variation
- Prototypes or proof-of-concepts where speed matters more than structure
- Trivial methods (under 10 lines) that clearly do one thing — KISS wins
- When a simple function call replaces what would become a 5-class pattern hierarchy
- Adding abstractions for hypothetical future needs — YAGNI violation

---

## Core Workflow

1. **Identify the problem domain** — Determine what changes frequently. Is it the behavior? The data format? The algorithm? The concrete type? **Checkpoint:** If nothing changes, no pattern is needed.

2. **Apply the right SOLID principle** — Map the change surface to the violating principle:
   - Single responsibility → class does too many things
   - Open/closed → adding features requires modifying existing code
   - Liskov substitution → subtypes break the contract of their base type
   - Interface segregation → interfaces force unused method dependencies
   - Dependency inversion → high-level modules depend on low-level concretions

3. **Match to a GoF pattern if applicable** — Use the pattern only when the structural problem it solves is present. If no GoF pattern fits cleanly, keep it simple (KISS).

4. **Verify DRY/YAGNI/KISS compliance** — The proposed abstraction must reduce complexity. If it adds more moving parts than it removes, the simplest solution is the correct one.

5. **Produce refactored code** — Return complete, working code with clear separation of concerns. Every new class or interface must have a single, well-defined responsibility.

---

## Implementation Patterns

### Pattern 1: Single Responsibility Principle (SRP)

A class should have only one reason to change. When a class handles multiple concerns, changes to one concern risk breaking another. Identify the distinct responsibilities and extract each into its own class.

```python
# ❌ BAD — Invoice class violates SRP: handles data, formatting, AND storage
class Invoice:
    def __init__(self, customer: str, items: list[dict[str, float]]) -> None:
        self.customer = customer
        self.items = items
        self.status = "draft"

    def calculate_total(self) -> float:
        return sum(item["price"] * item["quantity"] for item in self.items)

    def generate_pdf(self, filepath: str) -> None:
        # Formatting logic mixed into data model
        with open(filepath, "w") as f:
            f.write(f"Invoice for {self.customer}\n")
            f.write("=" * 40 + "\n")
            for item in self.items:
                subtotal = item["price"] * item["quantity"]
                f.write(f"{item['name']:20s} {item['quantity']:3d} x ${item['price']:.2f} = ${subtotal:.2f}\n")
            f.write("=" * 40 + "\n")
            f.write(f"TOTAL: ${self.calculate_total():.2f}\n")
            f.write(f"STATUS: {self.status}\n")

    def save_to_database(self, db_conn: object) -> None:
        # Database logic mixed into data model
        cursor = db_conn.cursor()
        cursor.execute(
            "INSERT INTO invoices (customer, total, status) VALUES (%s, %s, %s)",
            (self.customer, self.calculate_total(), self.status),
        )
        db_conn.commit()

    def send_email_notification(self, email: str) -> None:
        # Email logic mixed into data model
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(f"Invoice for {self.customer} total: ${self.calculate_total():.2f}")
        msg["Subject"] = "Your Invoice"
        msg["From"] = "billing@company.com"
        msg["To"] = email
        s = smtplib.SMTP("localhost")
        s.send_message(msg)
        s.quit()


# ✅ GOOD — Each class has a single, well-defined responsibility (SRP)
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class InvoiceItem:
    name: str
    price: float
    quantity: int

    def subtotal(self) -> float:
        return self.price * self.quantity


@dataclass
class Invoice:
    customer: str
    items: list[InvoiceItem] = field(default_factory=list)
    status: str = "draft"

    def add_item(self, name: str, price: float, quantity: int) -> None:
        self.items.append(InvoiceItem(name, price, quantity))

    def calculate_total(self) -> float:
        return sum(item.subtotal() for item in self.items)


class InvoicePdfFormatter:
    """Formats an invoice into a human-readable text file (PDF content source).

    Responsibility: Transform invoice data into formatted text output.
    This class changes only when the output format requirements change.
    """

    def format(self, invoice: Invoice) -> str:
        lines: list[str] = [f"Invoice for {invoice.customer}", "=" * 40]
        for item in invoice.items:
            line = f"{item.name:20s} {item.quantity:3d} x ${item.price:.2f} = ${item.subtotal():.2f}"
            lines.append(line)
        lines.extend(["=" * 40, f"TOTAL: ${invoice.calculate_total():.2f}", f"STATUS: {invoice.status}"])
        return "\n".join(lines)


class InvoiceRepository:
    """Persists invoice data to a database.

    Responsibility: Handle database CRUD operations for invoices.
    This class changes only when the storage mechanism or schema changes.
    """

    def __init__(self, db_conn: object) -> None:
        self._db_conn = db_conn

    def save(self, invoice: Invoice) -> None:
        cursor = self._db_conn.cursor()
        cursor.execute(
            "INSERT INTO invoices (customer, total, status) VALUES (%s, %s, %s)",
            (invoice.customer, invoice.calculate_total(), invoice.status),
        )
        self._db_conn.commit()

    def find_by_customer(self, customer: str) -> list[Invoice]:
        cursor = self._db_conn.cursor()
        cursor.execute("SELECT customer, total, status FROM invoices WHERE customer = %s", (customer,))
        rows = cursor.fetchall()
        return [Invoice(customer=row[0], status=row[2]) for row in rows]


class InvoiceNotifier:
    """Sends email notifications for invoices.

    Responsibility: Dispatch email messages when invoices are created.
    This class changes only when the notification channel or message content changes.
    """

    def __init__(self, smtp_host: str = "localhost", from_address: str = "billing@company.com") -> None:
        self._smtp_host = smtp_host
        self._from_address = from_address

    def notify(self, invoice: Invoice, recipient: str) -> None:
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText(f"Invoice for {invoice.customer} total: ${invoice.calculate_total():.2f}")
        msg["Subject"] = "Your Invoice"
        msg["From"] = self._from_address
        msg["To"] = recipient
        with smtplib.SMTP(self._smtp_host) as s:
            s.send_message(msg)
```

---

### Pattern 2: Dependency Injection / Inversion of Control (DIP)

High-level modules should not depend on low-level concrete implementations. Both should depend on abstractions. Inject dependencies rather than creating them internally. This enables independent testing and interchangeable implementations.

```python
# ❌ BAD — OrderProcessor tightly coupled to specific database and payment gateway
# Every change to the database driver or payment provider requires modifying this class.
# Violates: Dependency Inversion Principle (DIP)
import sqlite3
import requests


class OrderProcessor:
    """Processes customer orders by directly depending on concrete implementations."""

    def process_order(self, customer_id: int, items: list[dict], total: float) -> str:
        # Directly creates a concrete database connection (low-level dependency)
        self._db = sqlite3.connect("orders.db")
        order_id = self._save_to_db(customer_id, items, total)

        # Directly calls a concrete payment API (low-level dependency)
        payment_success = self._charge_card("4111111111111111", total)

        if payment_success:
            self._db.commit()
            return f"Order {order_id} confirmed"
        else:
            self._db.rollback()
            raise RuntimeError("Payment failed")

    def _save_to_db(self, customer_id: int, items: list[dict], total: float) -> int:
        cursor = self._db.cursor()
        cursor.execute("INSERT INTO orders (customer_id, total) VALUES (?, ?)", (customer_id, total))
        self._db.commit()
        return cursor.lastrowid

    def _charge_card(self, card_number: str, amount: float) -> bool:
        resp = requests.post(
            "https://payment-gateway.example.com/charge",
            json={"card": card_number, "amount": amount},
            timeout=10,
        )
        return resp.status_code == 200


# ✅ GOOD — OrderProcessor depends only on abstractions (interfaces).
# Low-level details (database driver, payment provider) are injected from outside.
# Follows: Dependency Inversion Principle (DIP) — high-level modules depend on
#         abstractions, not concretions. Enables dependency injection and mocking.
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol


class OrderRepository(Protocol):
    """Abstraction for persisting orders.

    Any class that can save and retrieve orders implements this interface.
    SQLite, PostgreSQL, MongoDB, or an in-memory store — OrderProcessor doesn't care.
    """

    @abstractmethod
    def save(self, customer_id: int, items: list[dict], total: float) -> int:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...


class PaymentGateway(Protocol):
    """Abstraction for processing payments.

    Any payment provider (Stripe, PayPal, bank transfer) implements this interface.
    Swapping providers requires zero changes to OrderProcessor.
    """

    @abstractmethod
    def charge(self, card_number: str, amount: float) -> bool:
        ...


@dataclass
class OrderResult:
    order_id: int
    confirmed: bool
    error: str | None = None


class OrderProcessor:
    """Processes customer orders using injected abstractions.

    Depends ONLY on OrderRepository and PaymentGateway protocols.
    No knowledge of SQLite, HTTP, or any specific payment provider.
    """

    def __init__(
        self,
        order_repo: OrderRepository,
        payment_gateway: PaymentGateway,
    ) -> None:
        # Dependencies injected, not created — DIP in action
        self._order_repo = order_repo
        self._payment_gateway = payment_gateway

    def process_order(self, customer_id: int, items: list[dict], total: float) -> OrderResult:
        try:
            order_id = self._order_repo.save(customer_id, items, total)
            payment_success = self._payment_gateway.charge("4111111111111111", total)

            if payment_success:
                return OrderResult(order_id=order_id, confirmed=True)
            else:
                self._order_repo.rollback()
                return OrderResult(order_id=order_id, confirmed=False, error="Payment declined")

        except Exception as exc:
            self._order_repo.rollback()
            return OrderResult(order_id=-1, confirmed=False, error=str(exc))


# Concrete implementations are wired at application startup (composition root)
class SqliteOrderRepository:
    """SQLite-backed order persistence — a LOW-LEVEL detail."""

    def __init__(self, db_path: str = "orders.db") -> None:
        self._db = sqlite3.connect(db_path)

    def save(self, customer_id: int, items: list[dict], total: float) -> int:
        cursor = self._db.cursor()
        cursor.execute("INSERT INTO orders (customer_id, total) VALUES (?, ?)", (customer_id, total))
        self._db.commit()
        return cursor.lastrowid

    def rollback(self) -> None:
        self._db.rollback()


class StripePaymentGateway:
    """Stripe payment integration — another LOW-LEVEL detail.

    Swapping to PayPal only requires creating a new PaymentGateway implementation
    and changing the wiring at startup — OrderProcessor code never changes.
    """

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def charge(self, card_number: str, amount: float) -> bool:
        # In production: actual Stripe SDK call
        return True  # Simplified for demonstration
```

---

### Pattern 3: Strategy Pattern (GoF — Behavioral)

Define a family of algorithms, encapsulate each one, and make them interchangeable. The strategy pattern lets the algorithm vary independently from clients that use it. Eliminates long if/else or switch chains that select behavior.

```python
# ❌ BAD — Shipping calculator uses a giant switch statement
# Every new shipping method requires modifying this class (violates Open/Closed Principle).
# The business logic for calculating shipping is tangled with the selection logic.
class ShippingCalculator:
    """Calculates shipping cost based on a method string.

    Problem: Every new shipping method requires adding another elif branch.
    Violates Open/Closed Principle — the class must be MODIFIED to add new behavior.
    """

    def calculate(self, weight: float, method: str, destination: str) -> float:
        if method == "standard":
            return weight * 2.50
        elif method == "express":
            return weight * 5.00 + 10.00
        elif method == "overnight":
            return weight * 12.00 + 25.00
        elif method == "economy_international":
            return weight * 1.00 + 15.00
        elif method == "priority_international":
            return weight * 3.50 + 30.00
        else:
            raise ValueError(f"Unknown shipping method: {method}")


# ✅ GOOD — Each shipping strategy is a standalone class implementing a common interface.
# Adding a new shipping method requires creating ONE new class — no modification
# to existing code. Follows: Open/Closed Principle (OCP) — open for extension,
# closed for modification.
from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol


class ShippingMethod(Enum):
    STANDARD = "standard"
    EXPRESS = "express"
    OVERNIGHT = "overnight"
    ECONOMY_INTERNATIONAL = "economy_international"
    PRIORITY_INTERNATIONAL = "priority_international"


class ShippingStrategy(Protocol):
    """Strategy interface: any class that can calculate shipping cost."""

    @abstractmethod
    def calculate(self, weight: float, destination: str) -> float:
        ...


class StandardShipping:
    """Standard ground shipping: $2.50 per pound."""

    def calculate(self, weight: float, destination: str = "domestic") -> float:
        base_rate = 2.50
        if destination == "remote":
            base_rate *= 1.5
        return weight * base_rate


class ExpressShipping:
    """Express 3-day shipping: $5.00 per pound + $10.00 base fee."""

    def calculate(self, weight: float, destination: str = "domestic") -> float:
        return weight * 5.00 + 10.00


class OvernightShipping:
    """Next-day overnight shipping: $12.00 per pound + $25.00 base fee."""

    def calculate(self, weight: float, destination: str = "domestic") -> float:
        base_rate = 12.00
        if destination == "remote":
            base_rate += 15.00
        return weight * base_rate + 25.00


class EconomyInternationalShipping:
    """Economy international: $1.00 per pound + $15.00 flat fee."""

    def calculate(self, weight: float, destination: str = "international") -> float:
        if destination == "domestic":
            raise ValueError("Economy international requires an international destination")
        return weight * 1.00 + 15.00


class PriorityInternationalShipping:
    """Priority international: $3.50 per pound + $30.00 flat fee."""

    def calculate(self, weight: float, destination: str = "international") -> float:
        if destination == "domestic":
            raise ValueError("Priority international requires an international destination")
        return weight * 3.50 + 30.00


# Strategy Registry: maps shipping method enum to its strategy implementation.
# Adding a new strategy only requires: (1) create the class, (2) register it.
# No existing code is modified — Open/Closed Principle satisfied.
class ShippingCalculator:
    """Calculates shipping cost by delegating to the selected strategy.

    The calculator does NOT contain shipping logic — it delegates to the
    active ShippingStrategy. This is the Strategy pattern in action.
    """

    _strategies: dict[ShippingMethod, ShippingStrategy] = {
        ShippingMethod.STANDARD: StandardShipping(),
        ShippingMethod.EXPRESS: ExpressShipping(),
        ShippingMethod.OVERNIGHT: OvernightShipping(),
        ShippingMethod.ECONOMY_INTERNATIONAL: EconomyInternationalShipping(),
        ShippingMethod.PRIORITY_INTERNATIONAL: PriorityInternationalShipping(),
    }

    def set_strategy(self, method: ShippingMethod) -> None:
        """Switch the shipping strategy at runtime. Strategies are interchangeable."""
        if method not in self._strategies:
            raise ValueError(f"Unsupported shipping method: {method}")

    def calculate(self, weight: float, method: ShippingMethod, destination: str = "domestic") -> float:
        """Delegate shipping calculation to the active strategy object."""
        strategy = self._strategies[method]
        return strategy.calculate(weight, destination)


# Demonstration: the calculator works without knowing the internal details
# of any specific shipping strategy.
def demo() -> None:
    calculator = ShippingCalculator()
    weight = 10.0
    print(f"Standard:  ${calculator.calculate(weight, ShippingMethod.STANDARD):.2f}")
    print(f"Express:   ${calculator.calculate(weight, ShippingMethod.EXPRESS):.2f}")
    print(f"Overnight: ${calculator.calculate(weight, ShippingMethod.OVERNIGHT, 'remote'):.2f}")


demo()
```

---

### Pattern 4: Factory Pattern (GoF — Creational)

Define an interface for creating objects but let subclasses decide which class to instantiate. The factory pattern centralizes object creation logic, reducing duplication and making it easy to introduce new concrete types without changing client code.

```python
# ❌ BAD — Document creation scattered across multiple places with duplicated logic
# Every new document type requires scanning the codebase to find where instances
# are created and adding a new conditional. Violates SRP and Open/Closed Principle.
from datetime import datetime


class PdfDocument:
    def __init__(self, title: str, content: str) -> None:
        self.title = title
        self.content = content
        self.created_at = datetime.now()

    def render(self) -> str:
        return f"[PDF] {self.title}\n{self.content}\nGenerated: {self.created_at}"


class DocxDocument:
    def __init__(self, title: str, content: str) -> None:
        self.title = title
        self.content = content
        self.created_at = datetime.now()

    def render(self) -> str:
        return f"[DOCX] {self.title}\n{self.content}\nGenerated: {self.created_at}"


class HtmlDocument:
    def __init__(self, title: str, content: str) -> None:
        self.title = title
        self.content = content
        self.created_at = datetime.now()

    def render(self) -> str:
        return f"<html><head><title>{self.title}</title></head><body>{self.content}</body></html>"


# Every place that creates documents repeats this conditional logic:
def create_document_bad(format_type: str, title: str, content: str) -> object:
    """Scattered factory logic — duplicated everywhere documents are created."""
    if format_type == "pdf":
        return PdfDocument(title, content)
    elif format_type == "docx":
        return DocxDocument(title, content)
    elif format_type == "html":
        return HtmlDocument(title, content)
    else:
        raise ValueError(f"Unknown format: {format_type}")


# Clients must know about concrete classes and format strings:
# report = create_document_bad("pdf", "Annual Report", "Q4 results...")
# marketing = create_document_bad("html", "Newsletter", "New features...")
# Every new format type requires finding ALL call sites and adding branches.


# ✅ GOOD — DocumentFactory centralizes creation logic in one place.
# New document types are added by creating a new class and registering it —
# client code never changes. Follows: Open/Closed Principle (OCP) and SRP.
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Document(ABC):
    """Abstract base for all document types.

    Defines the contract that all concrete documents must implement.
    The factory and clients depend only on this abstraction.
    """

    title: str
    content: str
    created_at: datetime = field(default_factory=datetime.now)

    @abstractmethod
    def render(self) -> str:
        """Render the document to its target format string."""
        ...


class PdfDocument(Document):
    def render(self) -> str:
        return f"[PDF] {self.title}\n{self.content}\nGenerated: {self.created_at}"


class DocxDocument(Document):
    def render(self) -> str:
        return f"[DOCX] {self.title}\n{self.content}\nGenerated: {self.created_at}"


class HtmlDocument(Document):
    def render(self) -> str:
        return f"<html><head><title>{self.title}</title></head><body>{self.content}</body></html>"


class MarkdownDocument(Document):
    """New document type added without modifying any existing code."""

    def render(self) -> str:
        return f"# {self.title}\n\n{self.content}\n*Generated: {self.created_at}*"


class DocumentFactory:
    """Centralized factory for creating document instances.

    Responsibility: Create the correct Document subclass based on format type.
    Client code depends only on this factory and the Document abstraction.
    To add a new format: (1) create a class, (2) register it in FORMATS.
    Zero changes needed in any client code.
    """

    # Registry of format name -> constructor. Add new formats here only.
    FORMATS: dict[str, type[Document]] = {
        "pdf": PdfDocument,
        "docx": DocxDocument,
        "html": HtmlDocument,
        "markdown": MarkdownDocument,
    }

    @classmethod
    def create(cls, format_type: str, title: str, content: str) -> Document:
        """Create a document of the requested format.

        Args:
            format_type: One of 'pdf', 'docx', 'html', 'markdown'.
            title: The document title.
            content: The document body content.

        Returns:
            A Document instance ready to render.

        Raises:
            ValueError: If the format_type is not registered.
        """
        constructor = cls.FORMATS.get(format_type)
        if constructor is None:
            available = ", ".join(sorted(cls.FORMATS.keys()))
            raise ValueError(f"Unknown format '{format_type}'. Available: {available}")
        return constructor(title=title, content=content)


# Clients interact only with the factory and the Document abstraction:
# report = DocumentFactory.create("pdf", "Annual Report", "Q4 results...")
# blog = DocumentFactory.create("markdown", "Blog Post", "New features...")
# No client code needs to know about PdfDocument, DocxDocument, etc.
def demo() -> None:
    report = DocumentFactory.create("pdf", "Annual Report", "Q4 revenue up 15%")
    blog = DocumentFactory.create("markdown", "Blog Post", "We just launched v2")
    email = DocumentFactory.create("html", "Newsletter", "New features inside")

    for doc in [report, blog, email]:
        print(doc.render())
        print()


demo()
```

---

### Pattern 5: DRY Violation vs. Proper Abstraction

Don't repeat yourself — but don't over-abstract either. The key insight: DRY means "every piece of knowledge has a single, unambiguous, authoritative representation." Copy-pasted code that shares logic is a DRY violation. Extracting abstractions for code that doesn't actually share behavior is over-engineering.

```python
# ❌ BAD — DRY violation: two methods with nearly identical validation logic
# The business rule "email must match the RFC 5322 pattern" is duplicated,
# meaning a fix to one copy won't fix the other.
import re
from dataclasses import dataclass
from datetime import date


class UserProfileValidator:
    """Validates user profiles with duplicated logic everywhere."""

    def validate_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

    def validate_recovery_email(self, email: str) -> bool:
        # DRY violation: same regex, duplicated — if the pattern changes,
        # both copies must be updated or bugs will diverge.
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

    def validate_username(self, username: str) -> bool:
        return 3 <= len(username) <= 30 and username.isalnum()

    def validate_display_name(self, display_name: str) -> bool:
        # DRY violation: same constraint as username length, different name
        return 3 <= len(display_name) <= 30


# ✅ GOOD — Shared validation logic extracted into reusable components.
# The DRY principle is satisfied: the regex lives in one place.
# The abstraction is justified because multiple validation points reuse it.
import re as _re
from dataclasses import dataclass, field
from datetime import date
from typing import Protocol


class ValidationError:
    """Describes a single validation failure."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message

    def __repr__(self) -> str:
        return f"ValidationError({self.field!r}: {self.message!r})"


class Validator(Protocol):
    """Protocol for any validation function."""

    def validate(self, value: str) -> bool:
        ...


class RegexValidator:
    """Validates a string against a regex pattern.

    Single, reusable validator — follows DRY by extracting the pattern
    matching logic into a reusable class.
    """

    def __init__(self, pattern: str, error_message: str = "Invalid value") -> None:
        self._pattern = _re.compile(pattern)
        self._error_message = error_message

    def validate(self, value: str) -> bool:
        return bool(self._pattern.match(value))


class LengthValidator:
    """Validates a string length falls within a range."""

    def __init__(self, min_length: int = 1, max_length: int | None = None, error_message: str | None = None) -> None:
        self._min_length = min_length
        self._max_length = max_length
        self._error_message = error_message or f"Length must be between {min_length} and {max_length or 'unbounded'}"

    def validate(self, value: str) -> bool:
        if len(value) < self._min_length:
            return False
        if self._max_length is not None and len(value) > self._max_length:
            return False
        return True


class AndValidator:
    """Combines multiple validators — all must pass (logical AND)."""

    def __init__(self, *validators: Validator) -> None:
        self._validators = validators

    def validate(self, value: str) -> bool:
        return all(v.validate(value) for v in self._validators)


class UserProfileValidator:
    """Validates user profile fields using composable, reusable validators.

    Email regex is defined once in EMAIL_PATTERN and reused by all validators
    that need email validation. Adding a new field only requires defining
    its validator — no duplication of validation logic.
    """

    EMAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    # Email validator reused for both primary and recovery email
    _email_validator = RegexValidator(EMAIL_PATTERN, "Must be a valid email address")
    _username_validator = AndValidator(
        LengthValidator(3, 30, "Must be 3-30 alphanumeric characters"),
        RegexValidator(r"^[a-zA-Z][a-zA-Z0-9_]*$", "Must start with a letter"),
    )
    _display_name_validator = LengthValidator(1, 100, "Must be 1-100 characters")

    def validate_email(self, email: str) -> list[ValidationError]:
        errors: list[ValidationError] = []
        if not self._email_validator.validate(email):
            errors.append(ValidationError("email", "Must be a valid email address"))
        return errors

    def validate_recovery_email(self, email: str) -> list[ValidationError]:
        # Reuses the same _email_validator — no duplicated regex
        errors: list[ValidationError] = []
        if not self._email_validator.validate(email):
            errors.append(ValidationError("recovery_email", "Must be a valid email address"))
        return errors

    def validate_username(self, username: str) -> list[ValidationError]:
        errors: list[ValidationError] = []
        if not self._username_validator.validate(username):
            errors.append(ValidationError("username", "Invalid username"))
        return errors

    def validate_display_name(self, display_name: str) -> list[ValidationError]:
        errors: list[ValidationError] = []
        if not self._display_name_validator.validate(display_name):
            errors.append(ValidationError("display_name", "Invalid display name"))
        return errors


def demo() -> None:
    validator = UserProfileValidator()

    # All these use the same email regex internally — changing the pattern
    # in EMAIL_PATTERN fixes both validators automatically.
    assert not validator.validate_email("not-an-email")
    assert not validator.validate_recovery_email("bad-email")
    assert validator.validate_email("user@example.com")
    assert validator.validate_recovery_email("recover@example.com")


demo()
```

---

### Pattern 6: YAGNI — Over-Engineering Prevention

You Aren't Gonna Need It. Don't build abstractions for hypothetical future requirements. Every abstraction must solve a current, concrete problem. When code is simple enough, adding a pattern creates more complexity than it prevents.

```python
# ❌ BAD — Premature abstraction for a problem that doesn't exist yet
# Four classes to solve a two-line problem. This is pattern-driven design,
# which is anti-pattern-driven design. The abstraction layer adds cognitive
# overhead with zero current benefit.
from abc import ABC, abstractmethod
from typing import Protocol


class PriceFormatter(Protocol):
    """Abstract protocol for formatting prices — but there's only ONE format."""

    @abstractmethod
    def format(self, amount: float) -> str:
        ...


class DollarFormatter:
    """Concrete formatter — the ONLY one that exists and is ever needed."""

    def format(self, amount: float) -> str:
        return f"${amount:.2f}"


class EuroFormatter:
    """Concrete formatter for Euros — never instantiated, never needed."""
    # This exists because "we might need it later" — classic YAGNI violation.

    def format(self, amount: float) -> str:
        return f"€{amount:.2f}"


class PriceFormatterFactory:
    """Factory to create formatters — for a single-product system."""

    @staticmethod
    def create(currency: str) -> PriceFormatter:
        if currency == "USD":
            return DollarFormatter()
        elif currency == "EUR":
            return EuroFormatter()
        raise ValueError(f"Unsupported currency: {currency}")


class PriceDisplayService:
    """Service that uses the factory to format prices — for a single format."""

    def __init__(self, currency: str) -> None:
        self._formatter = PriceFormatterFactory.create(currency)

    def format_price(self, amount: float) -> str:
        return self._formatter.format(amount)

    def format_total(self, items: list[float]) -> str:
        total = sum(items)
        return self._formatter.format(total)


# Usage in a system that ONLY displays USD prices:
service = PriceDisplayService("USD")
result = service.format_total([19.99, 29.99, 9.99])  # $59.97
# Five classes, two layers of indirection, one format: $59.97
# This is not architecture — it's a costume.


# ✅ GOOD — One function that does one thing. Simple, correct, complete.
# No abstraction until there's a real need. When/if multiple currencies
# are actually required, extract the abstraction then (YAGNI satisfied).
def format_price(amount: float, currency: str = "USD") -> str:
    """Format a monetary amount with the appropriate currency symbol.

    Currently supports only USD. When a second currency is genuinely
    required (not hypothetical), a formatter registry can be added.

    Args:
        amount: The monetary amount to format.
        currency: ISO 4217 currency code (default: USD).

    Returns:
        Formatted price string with currency symbol and two decimal places.
    """
    symbols: dict[str, str] = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency, "$")
    return f"{symbol}{amount:.2f}"


def format_total(items: list[float], currency: str = "USD") -> str:
    """Format the total of a list of prices.

    Simple composition of sum + format — no factory, no strategy, no protocol.
    If we later need per-item formatting, this function is trivially extended.
    """
    total = sum(items)
    return format_price(total, currency)


def demo() -> None:
    assert format_price(59.97) == "$59.97"
    assert format_total([19.99, 29.99, 9.99]) == "$59.97"
    assert format_price(42.50, "EUR") == "€42.50"
    assert format_total([9.99, 14.99], "GBP") == "£24.98"


demo()
```

---

## Constraints

### MUST DO

- Always start by asking "What changes frequently?" to find the right abstraction point
- Prefer composition over inheritance — composition gives flexible runtime behavior without the fragility of deep class hierarchies
- Verify any proposed pattern actually reduces complexity before applying it — count classes, not lines
- Use the simplest pattern that solves the current problem (YAGNI)
- Ensure every new class has a single, well-defined responsibility (SRP)
- Reference the SOLID principles when explaining design decisions
- When extracting an interface, let the implementation drive the interface shape — don't design interfaces in isolation
- Use Python protocols (`typing.Protocol`) for structural typing when an abstract base class is overkill
- Keep GoF pattern class counts minimal — a Strategy should be one small class, not a hierarchy

### MUST NOT DO

- Never apply a pattern without a concrete problem it solves — pattern-driven design is anti-pattern-driven design
- Never create abstractions for hypothetical future needs (YAGNI violation)
- Never use inheritance when composition solves the problem more cleanly
- Never apply GoF patterns to trivial code — KISS always wins
- Never create an abstraction layer just to "be proper" — every abstraction must earn its keep
- Never combine multiple SOLID principle violations without addressing each one independently
- Never create an interface with a single method — that's a callback, not a design pattern
- Never use the Singleton pattern to share state — use dependency injection instead

---

## Output Template

When applying this skill, the model's output must contain:

1. **Problem Analysis** — Identify what changes frequently, what SOLID principle is violated, and which concrete code smells are present.

2. **Principle Recommendation** — State which SOLID principle (or combination) applies and why, with a clear justification linking the principle to the observed problem.

3. **Pattern Match** — Determine if a GoF pattern fits the structural problem. If no pattern provides clear value, explicitly state that KISS wins and provide the simplest correct solution.

4. **Refactored Code** — Produce complete, working code implementing the recommended approach. Every class must have typed signatures, docstrings, and a clear single responsibility.

5. **YAGNI Check** — Confirm the proposed abstraction solves a current, concrete problem — not a hypothetical future one. If the abstraction adds more classes than it removes complexity, recommend the simpler alternative.

---

## Related Skills

| Skill                    | Purpose                                                     |
| ------------------------ | ----------------------------------------------------------- |
| `code-philosophy`        | 5 Laws of Elegant Defense — complements design pattern guidance with data flow philosophy |
| `clean-code`             | General clean code practices that align with SOLID and DRY principles |
| `test-driven-development`| TDD workflow — design patterns emerge naturally from test-first development |

---

## SOLID Quick Reference

| Principle | Question | Symptom of Violation |
|-----------|----------|---------------------|
| **S**ingle Responsibility | What is this class's one reason to change? | Class grows indefinitely, tests touch unrelated concerns |
| **O**pen/Closed | Can I add new behavior without modifying existing code? | Every new feature requires editing existing classes |
| **L**iskov Substitution | Can I swap a subtype for its base without breaking anything? | `TypeError`, `isinstance` checks in client code, fragile base class |
| **I**nterface Segregation | Does every implementor need every method? | Blanket `pass` implementations, unused methods on interfaces |
| **D**ependency Inversion | Do high-level modules depend on abstractions? | `import sqlite3` in business logic, hard to test without real dependencies |

## GoF Pattern Selection Guide

| Problem | Pattern | Category |
|---------|---------|----------|
| Need to create objects without specifying exact class | Factory Method, Abstract Factory | Creational |
| Need to ensure only one instance exists | Singleton (use DI instead) | Creational |
| Need to vary object construction step-by-step | Builder | Creational |
| Need to make objects cloneable | Prototype | Creational |
| Need to adapt one interface to another | Adapter | Structural |
| Need to compose objects into tree structures | Composite | Structural |
| Need to add behavior without subclassing | Decorator | Structural |
| Need a simplified interface to a complex subsystem | Facade | Structural |
| Need to share objects efficiently | Flyweight | Structural |
| Need to substitute behavior at runtime | Strategy, State | Behavioral |
| Need to chain handlers for a request | Chain of Responsibility | Behavioral |
| Need to encapsulate a request as an object | Command | Behavioral |
| Need to define algorithm skeletons | Template Method | Behavioral |
| Need to observe state changes | Observer | Behavioral |

---

## Composition over Inheritance — Key Rules

1. **Use inheritance only for "is-a" relationships** — `Dog is a Animal`. If it's "has-a" or "uses-a", prefer composition.

2. **Prefer small interfaces** — A protocol with 1-3 methods is easier to implement and mock than a deep class hierarchy.

3. **Compose behavior, not just data** — Inject strategies, formatters, and repositories rather than subclassing for each variant.

4. **Favor delegation** — Delegate to injected dependencies. It's explicit, testable, and doesn't break when the parent class changes.

```python
# Composition over inheritance — the preferred approach
class PaymentProcessor:
    """Processes payments using injected strategies. No inheritance needed."""

    def __init__(
        self,
        gateway: PaymentGateway,
        fraud_checker: FraudDetection,
        logger: Logger,
    ) -> None:
        self._gateway = gateway
        self._fraud_checker = fraud_checker
        self._logger = logger

    def process(self, amount: float, card: str) -> PaymentResult:
        if not self._fraud_checker.is_safe(card, amount):
            self._logger.warn("Fraud detected", card=card, amount=amount)
            return PaymentResult(approved=False, reason="fraud")
        return self._gateway.charge(card, amount)

# This is superior to inheritance because:
# - Swap fraud detection without subclassing
# - Add logging without changing payment behavior
# - Test with mocks easily
# - No fragile base class problem
```

---

*This skill complements `code-philosophy` (5 Laws of Elegant Defense). Together, they ensure both internal logic flow and architectural structure are clean, maintainable, and resistant to future change.*
