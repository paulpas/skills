---
name: code-review
description: Analyzes code diffs and files to identify bugs, security vulnerabilities, code smells, and architectural concerns, producing a structured review report with prioritized, actionable feedback.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
  domain: coding
  triggers: code review, pull request, PR review, code quality, security audit, OWASP, architectural review
  role: review
  scope: review
  output-format: report
  related-skills: coding-security-review, coding-test-driven-development
---

# Code Quality Specialist

Implements comprehensive code quality practices including review, testing, refactoring, security, and architectural patterns.

## TL;DR Checklist

- [ ] Identify security vulnerabilities (injection, authentication, authorization)
- [ ] Check for code smells (long methods, large classes, tight coupling)
- [ ] Verify adherence to project conventions and style guide
- [ ] Validate error handling and edge cases
- [ ] Check test coverage and test quality
- [ ] Review architectural decisions and dependencies
- [ ] Provide constructive, actionable feedback with specific recommendations

---

## When to Use

Use this skill when:

- Reviewing code changes before merging to main branch
- Onboarding new team members and establishing code quality standards
- Identifying security vulnerabilities in existing codebases
- Preparing code for production deployment
- Improving technical documentation through code clarity
- Conducting peer code reviews in agile development cycles
- Auditing third-party code integrations for quality and security

---

## When NOT to Use

Avoid this skill for:

- Fixing critical production bugs where speed is paramount — fix first, review later
- Trivial changes (typo fixes, whitespace) — consider automated formatting instead
- Skills that require deep domain expertise not available in the reviewer's knowledge
- Reviewing code with significantly different conventions than your team's standards
- As a substitute for automated testing — review complements, doesn't replace, tests

---

## Core Workflow

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
   **Checkpoint:** Approved code meets all team quality and security standards.

---

## Implementation Patterns

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

**Checkpoint:** Review checklist runs automatically and blocks merge for critical issues.

---

## Constraints

### MUST DO
- Review security vulnerabilities first — flag any critical issues before code quality
- Provide specific, actionable feedback with suggestions for improvement
- Reference project style guide and coding standards explicitly
- Verify tests exist and cover edge cases before approving
- Use positive reinforcement to recognize good practices
- Document all review decisions in comments for audit trail
- Block merge for critical security issues, even if code otherwise looks good

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
| `coding-security-review` | Specialized security-focused code review with deep OWASP analysis |
| `coding-test-driven-development` | TDD practices for writing tests before implementation |
| `coding-refactoring` | Refactoring techniques to improve code quality after review |
| `coding-architecture` | Architectural patterns and design principles for code review |
| `coding-continuous-integration` | CI pipeline setup for automated code quality checks |
