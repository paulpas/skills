---
name: input-validation
description: Validates, sanitizes, and transforms inbound data through typed schema checks, OWASP-compliant sanitization, and defensive parsing to prevent injection attacks and data corruption.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  triggers: input validation, data sanitization, schema validation, input filtering, sanitize user input, prevent injection, OWASP, form validation, parse and validate, defense in depth, data entry
  role: implementation
  scope: implementation
  output-format: code
  content-types: [code, guidance, do-dont, examples]
  related-skills: security-review, test-driven-development, error-handling
---

# Input Validation and Sanitization Manager

Validates, sanitizes, and transforms inbound data through typed schema checks, OWASP-compliant sanitization, and defensive parsing to ensure no corrupted or malicious payload reaches business logic. Treat every external input — user form data, API payloads, file uploads, environment variables, database queries — as hostile until proven otherwise.

## TL;DR Checklist

- [ ] Define explicit schema for every input endpoint (types, formats, ranges)
- [ ] Sanitize before validation to strip dangerous characters and encoding tricks
- [ ] Reject unknown/extra fields rather than silently ignoring them
- [ ] Never use raw user input in SQL queries, shell commands, or template rendering
- [ ] Log validation failures with enough context to debug without leaking data
- [ ] Test boundary conditions: empty strings, nulls, oversized payloads, encoding edge cases

---

## When to Use

Use this skill when:

- Building API endpoints that accept user-provided JSON, form data, or query parameters
- Processing file uploads where you must validate content type and size before saving
- Writing CLI tools that parse command-line arguments and environment variables
- Integrating with third-party webhooks or data feeds whose schema may change
- Implementing configuration loaders that merge defaults, env vars, and config files
- Reviewing existing code for injection vulnerabilities or missing input guards

---

## When NOT to Use

Avoid this skill for:

- Output formatting or display logic — use output templating/rendering skills instead
- Business rule validation (e.g., "can this user afford this trade") — that's domain logic
- Network-level filtering (firewall rules, IP blocking) — that's infrastructure security
- Data transformation pipelines where the source is already trusted and validated upstream

---

## Core Workflow

1. **Identify Input Surface** — Enumerate every data entry point: request body, headers, query params, cookies, file uploads, env vars, config files. **Checkpoint:** If an input originates outside your process boundary, it needs validation.

2. **Define Schema Contract** — Specify the expected shape with types, required fields, allowed values, and constraints (min/max length, regex patterns, numeric ranges). Use a schema library rather than hand-rolled checks. **Checkpoint:** Every field has an explicit type; no field uses "any" or "unknown."

3. **Sanitize Input** — Strip or escape dangerous characters before validation. Handle encoding normalization (UTF-8), trim whitespace, and neutralize injection payloads. **Checkpoint:** After sanitization, the data should be safe for downstream processing but semantically unchanged where it matters.

4. **Validate Against Schema** — Run sanitized input through schema validation. Reject if any constraint is violated. Collect all errors rather than failing on the first one so callers get full feedback. **Checkpoint:** Validation either passes completely or fails completely — partial acceptance is a vulnerability.

5. **Transform to Internal Types** — Convert validated external representations into your internal domain types (e.g., string `"2024-01-15"` → `datetime.date`). **Checkpoint:** Internal types are never raw strings from user input after this step.

6. **Log and Handle Failures** — Record validation failures at appropriate log levels with sufficient context for debugging but without leaking sensitive data. Return structured error responses to callers. **Checkpoint:** Log entries contain field names and rule violations, not the raw problematic input.

---

## Implementation Patterns / Reference Guide

### Pattern 1: Schema Validation with Pydantic (Python)

Use Pydantic models to define strict contracts. This is the gold standard for Python APIs.

```python
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from datetime import date


class UserRegistrationInput(BaseModel):
    """Schema for user registration form data."""
    
    username: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Alphanumeric username with underscores and hyphens only"
    )
    email: EmailStr = Field(description="Valid email address")
    age: int = Field(ge=13, le=150, description="Age in years, compliant with COPPA")
    display_name: Optional[str] = Field(default=None, max_length=100)
    
    @field_validator("username")
    @classmethod
    def sanitize_username(cls, v: str) -> str:
        """Strip whitespace and normalize to lowercase before validation."""
        return v.strip().lower()
    
    @field_validator("display_name")
    @classmethod
    def strip_display_name(cls, v: Optional[str]) -> Optional[str]:
        """Trim whitespace from display name if present."""
        if v is not None:
            return v.strip()
        return v
```

**Why this works:** Pydantic handles type coercion, constraint checking, sanitization via validators, and produces structured error messages automatically. The schema is self-documenting and serializable to JSON Schema for API docs.

### Pattern 2: OWASP-Compliant HTML Sanitization (BAD vs. GOOD)

```python
# ❌ BAD — naively stripping all HTML tags leaves XSS vectors through event handlers
# and protocol-relative URLs. Also destroys legitimate rich-text content.
def bad_sanitize_html(raw_input: str) -> str:
    return raw_input.replace("<", "&lt;").replace(">", "&gt;")

# ✅ GOOD — Whitelist-based sanitization using Bleach preserves safe HTML
# while removing dangerous tags, attributes, and protocols per OWASP guidelines.
import bleach


def sanitize_html(raw_input: str, allowed_tags: list[str] | None = None) -> str:
    """Sanitize HTML input by whitelisting safe tags and attributes.
    
    Follows OWASP XSS Prevention Cheat Sheet recommendations for 
    content sanitization using allowlists rather than blocklists.
    
    Args:
        raw_input: Untrusted HTML string from user input.
        allowed_tags: Explicit whitelist of HTML tags to preserve.
            Defaults to basic formatting tags only.
    
    Returns:
        Sanitized HTML string safe for rendering in browser context.
    
    Raises:
        ValueError: If raw_input cannot be decoded as UTF-8.
    """
    if not isinstance(raw_input, str):
        raise ValueError(f"Expected str input, got {type(raw_input).__name__}")
    
    default_tags = {
        "b", "i", "em", "strong", "p", "br", 
        "ul", "ol", "li", "a", "code", "pre",
        "h1", "h2", "h3", "blockquote"
    }
    
    allowed_attrs = {
        "a": {"href", "title", "rel"},
    }
    
    # Strip all protocols except http, https, and mailto for <a> tags
    sanitizer = bleach.Cleaner(
        tags=allowed_tags or default_tags,
        attributes=allowed_attrs,
        protocols=["http", "https", "mailto"],
        strip=True,
    )
    
    return sanitizer.clean(raw_input)
```

### Pattern 3: Defensive JSON Parsing with Fallbacks

Never trust external JSON. Validate structure before accessing fields, and handle malformed input gracefully.

```python
import json
from typing import Any


def parse_json_payload(raw_bytes: bytes, max_size: int = 1_048_576) -> dict[str, Any]:
    """Parse and validate JSON payload with size limits and structure checks.
    
    Implements defense in depth: size limiting prevents DoS via oversized payloads,
    type checking ensures we get a dict (not array or scalar), and field-level
    validation catches schema violations early.
    
    Args:
        raw_bytes: Raw request body bytes from external source.
        max_size: Maximum allowed payload size in bytes (default 1 MB).
    
    Returns:
        Parsed dictionary with validated types.
    
    Raises:
        ValueError: If payload exceeds size limit or has invalid structure.
        json.JSONDecodeError: If payload is not valid JSON.
    """
    # Defense 1: Size limit before parsing (prevents zip bombs, memory exhaustion)
    if len(raw_bytes) > max_size:
        raise ValueError(
            f"Payload size {len(raw_bytes)} exceeds maximum {max_size} bytes"
        )
    
    # Defense 2: Parse with strict mode (no trailing commas, no comments)
    try:
        data = json.loads(raw_bytes, strict=True)
    except json.JSONDecodeError as exc:
        raise json.JSONDecodeError(
            f"Malformed JSON: {exc.msg}", exc.doc, exc.pos
        ) from exc
    
    # Defense 3: Ensure top-level is an object (not array or scalar)
    if not isinstance(data, dict):
        raise ValueError(
            f"Expected JSON object at top level, got {type(data).__name__}"
        )
    
    # Defense 4: Reject deeply nested structures (prevent stack overflow in processing)
    if _get_depth(data) > 10:
        raise ValueError("JSON nesting depth exceeds maximum of 10 levels")
    
    return data


def _get_depth(obj: Any, current: int = 0) -> int:
    """Calculate maximum nesting depth of a JSON structure."""
    if isinstance(obj, dict):
        if not obj:
            return current + 1
        return max(_get_depth(v, current + 1) for v in obj.values())
    elif isinstance(obj, list):
        if not obj:
            return current + 1
        return max(_get_depth(item, current + 1) for item in obj)
    return current
```

### Pattern 4: Input Validation in CLI Arguments (Python argparse)

Command-line tools also need input validation — users type things wrong.

```python
import argparse
import sys
from pathlib import Path


def validate_file_path(value: str) -> Path:
    """Validate that a file path string points to an existing readable file.
    
    Args:
        value: File path from command-line argument.
    
    Returns:
        Validated Path object.
    
    Raises:
        argparse.ArgumentTypeError: If the path is invalid.
    """
    path = Path(value)
    
    if not path.exists():
        raise argparse.ArgumentTypeError(f"File does not exist: {value}")
    
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"Path is not a file: {value}")
    
    if not os.access(path, os.R_OK):
        raise argparse.ArgumentTypeError(f"File is not readable: {value}")
    
    # Safety check: prevent path traversal attacks
    resolved = path.resolve()
    expected_base = Path("/data/input").resolve()
    if not str(resolved).startswith(str(expected_base)):
        raise argparse.ArgumentTypeError(
            f"Path traversal detected: {value} resolves outside allowed base"
        )
    
    return resolved


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser with validated argument types."""
    parser = argparse.ArgumentParser(
        description="Process input data from files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "input_file",
        type=validate_file_path,
        help="Path to input file (must exist, be a regular file, and be readable)",
    )
    
    parser.add_argument(
        "--max-records",
        type=int,
        default=10000,
        choices=range(1, 1_000_001),
        metavar="N",
        help="Maximum number of records to process (1 to 999999)",
    )
    
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./output"),
        help="Directory for output files (created if not exists)",
    )
    
    return parser


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse and validate CLI arguments with error handling."""
    try:
        return build_parser().parse_args(args)
    except SystemExit as exc:
        # argparse calls sys.exit on error — intercept for clean error handling
        raise ValueError(f"Invalid command-line arguments: {exc}") from exc
```

---

## Constraints

### MUST DO
- Define explicit schema or type contract before writing validation logic
- Sanitize input before validation to neutralize encoding-based bypasses
- Use allowlists (whitelists) for allowed values, NOT blocklists for blocked values
- Validate at the system boundary — don't push raw external data deeper into your codebase
- Return structured error responses that identify which fields failed and why
- Test with adversarial inputs: SQL injection strings, XSS payloads, oversized payloads, null bytes, Unicode edge cases
- Apply the principle of least privilege: reject extra/unknown fields rather than silently ignoring them

### MUST NOT DO
- Concatenate user input into SQL queries, shell commands, or file paths without validation
- Use regex alone for complex validation (SQL injection regexes are famously bypassable)
- Trust `content-type` headers from clients — they are trivially spoofed; inspect actual content
- Log raw user input at any log level — it may contain passwords, tokens, or PII
- Accept partial validation — if one field fails, reject the entire payload
- Use client-side validation as a security boundary — it provides zero protection

---

## Output Template

When implementing or reviewing input validation logic, produce:

1. **Schema Definition** — The complete input contract with types, constraints, and required fields
2. **Sanitization Strategy** — How dangerous content is neutralized before validation
3. **Validation Checks** — Each constraint applied and the error message if violated
4. **Failure Handling** — How errors are logged (what context included/excluded) and returned to callers
5. **Test Coverage Summary** — Adversarial input categories tested (injection, overflow, encoding, boundary)

---

## Related Skills

| Skill | Purpose |
|---|---|
| `security-review` | Comprehensive security audit that catches input validation gaps alongside other vulnerabilities |
| `test-driven-development` | Write validation tests before implementation to ensure all edge cases are covered |
| `error-handling` | Proper error response formatting and structured logging for validation failures |
