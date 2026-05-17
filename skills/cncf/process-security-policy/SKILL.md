---
compatibility: opencode
completeness: 95
content-types:
- guidance
- examples
- do-dont
- config
description: '"Creates or updates SECURITY.md defining the vulnerability reporting process" disclosure timeline, and supported
  versions for CNCF projects'
how_to_guide: https://contribute.cncf.io/projects/best-practices/security/
id: security-policy
license: MIT
maturity: stable
mcp_servers: null
metadata:
  domain: cncf
  output-format: manifests
  role: reference
  scope: infrastructure
  triggers: creates, defining, process security policy, process-security-policy, updates, vulnerability scanning, security,
    security auditing
  version: 1.0.0
name: security-policy
template_source: https://github.com/cncf/tag-security/blob/main/project-resources/templates/SECURITY.md
---
  related-skills: cncf-aws-kms, cncf-aws-s3, cncf-aws-secrets-manager, cncf-azure-key-vault




# CNCF Security Policy Process

Creates or updates `SECURITY.md` with the project's vulnerability reporting channel, supported versions matrix, and response timeline.

## When to Use

Use when:
- A CNCF incubating or graduating project does not yet have a `SECURITY.md`
- The existing `SECURITY.md` is missing the reporting channel, response SLA, or supported versions
- A project is working toward an OpenSSF Best Practices badge (requires a security disclosure policy)

Do NOT use when:
- The repository is documentation-only with no executable code — link to the parent project's SECURITY.md instead

## Steps

1. **Fetch the template.**
   If GitHub MCP available: `github_get_contents` path=`cncf/tag-security/main/project-resources/templates/SECURITY.md`
   Otherwise: `gh api repos/cncf/tag-security/contents/project-resources/templates/SECURITY.md`

2. **Fill in Reporting a Vulnerability:**
   - Primary: GitHub Private Vulnerability Reporting
     (`Settings → Code security → Private vulnerability reporting → Enable`)
   - Fallback: security@<project>.io or security@lists.cncf.io
   ⚠️ Never direct reporters to a public GitHub issue — this exposes the vulnerability before a patch exists.

3. **Fill in Supported Versions table.** Mark EOL versions clearly.
   ⚠️ Define how a version reaches EOL, or link to RELEASES.md that does.

4. **Fill in Response Timeline** (CNCF recommended):
   - Acknowledge: within 2 business days
   - Triage + severity: within 5 business days
   - Patch + coordinated disclosure: within 90 days (non-critical) / 7 days (critical)
   ⚠️ All dates must use UTC to avoid timezone ambiguity with downstream distributors.

5. **Enable GitHub Private Vulnerability Reporting** in repo settings if not already on:
   `https://github.com/<org>/<repo>/settings/security_analysis`

6. **Set up OpenSSF tooling.** See the `openssf-scorecards` and `openssf-badge` skills.

7. **Remove all TODO markers and instruction links.**

## Checklist

- [ ] Reporting channel documented (GitHub PVR or email)
- [ ] Supported versions table filled in with EOL criteria
- [ ] Response timeline defined in UTC (graduation)
- [ ] GitHub Private Vulnerability Reporting enabled in repo settings (graduation)
- [ ] OpenSSF Best Practices badge applied for and link in README (graduation — hard gate)
- [ ] OpenSSF Scorecards action added (graduation)
- [ ] Branch protection rules enforced on default branch (graduation)
- [ ] 2FA enforced on GitHub org (graduation)
- [ ] No `TODO` markers remain

## Knowledge Reference

- CNCF Security Policy Best Practices: https://contribute.cncf.io/projects/best-practices/security/
- OpenSSF Best Practices: https://openssf.org/best-practices/
- CNCF TAG Security: https://github.com/cncf/tag-security
---

## Core Workflow

1. **Assess Requirements** — Understand the use case, scale, integration needs, and existing infrastructure. **Checkpoint:** Document requirements, constraints, and success criteria.

2. **Design Architecture** — Plan component interactions, data flow, and deployment strategy using cloud-native best practices. **Checkpoint:** Verify the architecture addresses all requirements and follows CNCF conventions.

3. **Implement & Configure** — Create manifests, configurations, and deployment scripts. Include resource limits, health checks, and observability hooks. **Checkpoint:** Validate all YAML against schema and test in a staging environment.

4. **Deploy & Monitor** — Apply manifests to the cluster, verify component health, and confirm observability is working. **Checkpoint:** Confirm all pods/services are running, probes passing, and metrics/alerts configured.

---

## Constraints

### MUST DO
- Include at least one complete working YAML manifest example
- Note when content is auto-generated vs. manually verified
- Reference relevant CNCF project documentation

### MUST NOT DO
- Deploy manifests without testing in a staging environment first
- Use deprecated API versions (e.g., apps/v1beta1)
- Omit resource limits and requests in Kubernetes manifests
