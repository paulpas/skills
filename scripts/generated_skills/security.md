---
name: security
description: Implements security best practices including input validation, authentication patterns, encryption, and vulnerability prevention in application code.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  triggers: security, OWASP, vulnerability, injection, authentication, encryption, secure coding
  role: implementation
  scope: implementation
  output-format: code
  related-skills: coding-code-review, coding-security-review
---

# Code Quality Specialist

Implements comprehensive code quality practices including review, testing, refactoring, security, and architectural patterns.

## TL;DR Checklist

- [ ] Validate and sanitize all user input (SQL injection, XSS prevention)
- [ ] Use parameterized queries instead of string concatenation
- [ ] Implement proper authentication with secure session management
- [ ] Store secrets in environment variables or secret management tools
- [ ] Use HTTPS for all communications
- [ ] Implement rate limiting on sensitive endpoints
- [ ] Follow principle of least privilege for access control

---

## When to Use

Use this skill when:

- Implementing user authentication and authorization
- Building APIs that handle sensitive data
- Integrating with external services and APIs
- Setting up database connections and queries
- Implementing encryption for data at rest or in transit
- Building applications that process financial or personal data
- Conducting security audits or penetration testing preparation

---

## When NOT to Use

Avoid this skill for:

- Implementing security for non-sensitive data (security has overhead)
- Prototyping where security is not a concern (fix before production)
- When you lack understanding of the threat model and attack surface
- Using security tools without understanding their limitations
- As a replacement for security audits by specialized professionals

---

## Core Workflow

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
   **Checkpoint:** Security documentation is available for review and audit.

---

## Implementation Patterns

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

**Checkpoint:** Rate limiting prevents brute force attacks on sensitive endpoints.

---

## Constraints

### MUST DO
- Validate and sanitize all user input before processing
- Use parameterized queries to prevent SQL injection
- Hash passwords with bcrypt or scrypt, never store plaintext
- Implement proper session management with secure cookies
- Log security events for auditing
- Follow principle of least privilege for all access
- Use HTTPS for all communications

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
| `coding-code-review` | Security-focused code review to identify vulnerabilities |
| `coding-security-audit` | Comprehensive security audit of entire application |
| `coding-secret-management` | Secure handling of secrets and credentials |
| `coding-authentication` | Authentication patterns and best practices |
| `coding-encryption` | Encryption patterns for data protection |
