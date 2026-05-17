---
compatibility: opencode
completeness: 95
content-types:
- guidance
- examples
- do-dont
- config
description: '"Creates or updates an incident response plan covering detection, triage" communication, and post-incident review
  for CNCF projects'
how_to_guide: https://contribute.cncf.io/projects/best-practices/security/
id: incident-response
license: MIT
maturity: stable
mcp_servers: null
metadata:
  domain: cncf
  output-format: manifests
  related-skills: null
  role: reference
  scope: infrastructure
  triggers: covering, creates, process incident response, process-incident-response, updates
  version: 1.0.0
name: incident-response
template_source: https://github.com/cncf/tag-security/blob/main/project-resources/templates/INCIDENT-RESPONSE.md
---
# CNCF Incident Response Process

Creates or updates an incident response plan with the step-by-step process for triaging, remediating, and disclosing a confirmed security vulnerability.

## When to Use

Use when:
- A project has never formally documented how it responds to a confirmed vulnerability
- The project is expanding its security team and needs a shared runbook
- A post-incident review revealed gaps in the response process

Do NOT use when:
- The project does not yet have a `SECURITY.md` — the reporting channel must exist before defining the response process; run the security-policy skill first

## Steps

1. **Fetch the template.**
   If GitHub MCP available: `github_get_contents` path=`cncf/tag-security/main/project-resources/templates/INCIDENT-RESPONSE.md`
   Otherwise: `gh api repos/cncf/tag-security/contents/project-resources/templates/INCIDENT-RESPONSE.md`

2. **Fill in Triage:** who is notified first, severity rating (CVSS or project-defined),
   decision criteria for patch vs. mitigate.

3. **Fill in Remediation:** branching strategy, who has access to private security forks,
   how patches are tested without public disclosure.
   ⚠️ Access to private forks must be defined now — unclear access during an active incident delays patching.

4. **Fill in Coordinated Disclosure:** how downstream distributors are notified before
   public disclosure, embargo period, and GitHub Security Advisory publishing process.
   ⚠️ Verify the timeline matches the response timeline in SECURITY.md — inconsistencies are a graduation finding.

5. **Fill in Communication:** what the public announcement includes, which channels
   are used (GitHub Security Advisory, project mailing list), who approves.
   ⚠️ One named person must own each active incident; "the security contacts will handle it" is not a runbook.

6. **Fill in Post-Incident Review:** blameless retrospective process and how learnings
   feed back into the security policy.

7. **Cross-link to the security self-assessment** under Remediation or Post-Incident Review.

## Checklist

- [ ] Triage process documented with severity definitions
- [ ] Private patch development access defined by name/role (graduation)
- [ ] Coordinated disclosure timeline defined and consistent with SECURITY.md (graduation)
- [ ] Named incident commander role defined (graduation)
- [ ] Public communication plan documented
- [ ] Post-incident review process defined
- [ ] Cross-link to security self-assessment present (graduation)
- [ ] GitHub Security Advisory draft workflow verified accessible to all contacts (graduation)

## Knowledge Reference

- CNCF Incident Response: https://contribute.cncf.io/projects/best-practices/security/
- CNCF TAG Security: https://github.com/cncf/tag-security
- GitHub Security Advisories: https://docs.github.com/en/code-security/security-advisories
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
