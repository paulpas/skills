# Agent Skill Router API

Complete API documentation for the Agent Skill Router - an intelligent task-to-skill matching system that enables auto-routing of AI agent tasks to specialized skills.

---

## API Overview

### Base URL

```
http://localhost:3000
```

### Authentication

None required. The API is designed for local development and containerized deployment.

### Content Type

All POST requests require the `Content-Type: application/json` header.

### Error Handling

The router returns standard HTTP status codes:

| Code | Description |
|------|-------------|
| `200` | Success |
| `400` | Invalid request body or missing required fields |
| `404` | Skill not found or endpoint doesn't exist |
| `500` | Internal server error |
| `503` | Service unavailable |

Error responses follow this format:

```json
{
  "error": "Error message describing what went wrong"
}
```

---

## Health & Status Endpoints

### GET /health

Check if the skill router service is running.

**Example Request:**

```bash
curl http://localhost:3000/health
```

**Example Response:**

```json
{
  "status": "healthy",
  "timestamp": "2026-04-30T12:00:00Z",
  "version": "1.0.0"
}
```

---

### GET /stats

Get statistics about loaded skills and MCP tools.

**Example Request:**

```bash
curl http://localhost:3000/stats
```

**Example Response:**

```json
{
  "skills": {
    "totalSkills": 463,
    "categories": ["agent", "cncf", "coding", "trading", "programming"],
    "tags": ["implementation", "reference", "orchestration", "review"]
  },
  "mcpTools": {
    "route_to_skill": true,
    "list_skills": true
  }
}
```

---

## Skills Management Endpoints

### GET /skills

List all loaded skills with metadata.

**Example Request:**

```bash
curl http://localhost:3000/skills
```

**Example Response:**

```json
[
  {
    "name": "code-philosophy",
    "description": "Internal logic and data flow philosophy (The 5 Laws of Elegant Defense)",
    "domain": "coding",
    "role": "reference",
    "triggers": ["code philosophy", "elegant defense", "5 laws"],
    "source": "skills/coding/code-philosophy/SKILL.md"
  },
  {
    "name": "trading-risk-stop-loss",
    "description": "Implements stop-loss strategies for position risk management",
    "domain": "trading",
    "role": "implementation",
    "triggers": ["stop loss", "trailing stop", "ATR stop"],
    "source": "skills/trading/risk-stop-loss/SKILL.md"
  }
]
```

---

### GET /skill/:name

Get the full content of a specific skill by name.

**Example Request:**

```bash
curl http://localhost:3000/skill/code-philosophy
```

**Example Response:**

```markdown
# Code Philosophy

Internal logic and data flow philosophy (The 5 Laws of Elegant Defense).

## When to Use

- Implementing new features
- Writing utility functions
- Designing data processing pipelines

## Core Workflow

1. **Early Exit** — Guard clauses handle edge cases at the top
2. **Parse Don't Validate** — Data parsed at boundaries, trusted internally
...
```

**Error Response (Skill Not Found):**

```json
{
  "error": "Skill 'nonexistent-skill' not found"
}
```

---

## Routing & Execution Endpoints

### POST /route

Route a task description to the most relevant skills. Returns selected skills with confidence scores and execution plan.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task` | string | Yes | Natural language description of the task |
| `context` | object | No | Additional context (environment, user, etc.) |
| `constraints` | object | No | Constraints like maxSkills, domain filters |

**Example Request:**

```bash
curl -X POST http://localhost:3000/route \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Deploy a Kubernetes manifest to production",
    "context": {"environment": "production"},
    "constraints": {"maxSkills": 3}
  }'
```

**Example Response:**

```json
{
  "skills": [
    {
      "name": "cncf-kubernetes",
      "confidence": 0.94,
      "matchScore": 94.5,
      "source": "skills/cncf/kubernetes/SKILL.md"
    },
    {
      "name": "cncf-helm",
      "confidence": 0.78,
      "matchScore": 78.2,
      "source": "skills/cncf/helm/SKILL.md"
    }
  ],
  "executionPlan": "sequential",
  "totalMatches": 2,
  "latencyMs": 45
}
```

**Optional Parameters:**

- `constraints.maxSkills`: Limit the number of returned skills (default: 5)
- `constraints.domain`: Filter by domain (agent, cncf, coding, trading, programming)
- `constraints.role`: Filter by role (implementation, reference, orchestration, review)

---

### POST /execute

Execute a task using specified skills. This endpoint triggers skill execution with the provided inputs.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `task` | string | Yes | Natural language description of the task |
| `inputs` | object | Yes | Input data for the skills |
| `skills` | array | Yes | Array of skill names to execute |

**Example Request:**

```bash
curl -X POST http://localhost:3000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Deploy a Kubernetes manifest to production",
    "inputs": {
      "manifest": "apiVersion: v1\nkind: Pod\nmetadata:\n  name: example\nspec:\n  containers:\n  - name: example\n    image: nginx"
    },
    "skills": ["cncf-kubernetes"]
  }'
```

**Example Response:**

```json
{
  "status": "executing",
  "taskId": "task_abc123",
  "skills": ["cncf-kubernetes"],
  "outputs": {},
  "metadata": {
    "executionTimeMs": 1250,
    "skillsExecuted": 1
  }
}
```

**Note:** The `/execute` endpoint may be implemented differently depending on the actual backend. Some implementations may return immediately with a task ID, while others may execute synchronously.

---

## History & Management Endpoints

### GET /access-log

Retrieve the routing history (last 100 requests).

**Example Request:**

```bash
curl http://localhost:3000/access-log
```

**Example Response:**

```json
{
  "totalRequests": 157,
  "entries": [
    {
      "timestamp": "2026-04-30T11:45:23Z",
      "task": "Review this Python code for security issues",
      "topSkill": "coding-security-review",
      "totalMatches": 3,
      "confidence": 0.89,
      "latencyMs": 32
    },
    {
      "timestamp": "2026-04-30T11:42:15Z",
      "task": "Implement a stop loss strategy",
      "topSkill": "trading-risk-stop-loss",
      "totalMatches": 2,
      "confidence": 0.95,
      "latencyMs": 28
    }
  ]
}
```

---

### POST /reload

Force reload skills from the repository. Triggers a `git fetch + reset` and re-indexes all skills.

**Example Request:**

```bash
curl -X POST http://localhost:3000/reload
```

**Example Response:**

```json
{
  "status": "reload initiated",
  "timestamp": "2026-04-30T12:00:00Z",
  "newSkillCount": 465
}
```

**Use Cases:**
- After pushing new skills to the repository
- After modifying skill metadata
- When the skill router doesn't detect new skills automatically

---

## Docker Management

The skill router runs in a Docker container named `skill-router`.

### Check Container Status

```bash
docker ps --filter name=skill-router
```

**Example Output:**

```
CONTAINER ID   IMAGE             COMMAND                  CREATED          STATUS         PORTS                    NAMES
abc123def456   skill-router:latest   "/app/start.sh"          2 hours ago      Up 2 hours     0.0.0.0:3000->3000/tcp   skill-router
```

---

### View Logs

```bash
docker logs skill-router --tail 50 -f
```

**Common Log Output:**

```
[INFO] Skill router started on port 3000
[INFO] Loaded 463 skills from repository
[INFO] Health check endpoint ready
[DEBUG] Skill index refresh completed
```

---

### Restart Container

```bash
docker restart skill-router
```

---

### Stop Container

```bash
docker stop skill-router
```

---

### Start Container

```bash
docker start skill-router
```

---

### Full Container Lifecycle

```bash
# Build and start
docker build -t skill-router .
docker run -d --name skill-router -p 3000:3000 skill-router

# Stop and remove
docker stop skill-router
docker rm skill-router
```

---

## Common Examples

### OpenCode Usage

#### Auto-Routing in OpenCode

Add this to your OpenCode workflow:

```javascript
// At the start of every task
const skill = await route_to_skill("implement a trading strategy with Bollinger Bands");

if (skill) {
  // Follow the skill's guidelines
  console.log(`Loaded skill: ${skill.name}`);
} else {
  // Proceed without skill routing
  console.log("No skill matched, proceeding with default implementation");
}
```

#### Manual Skill Loading

```bash
# Get skill content directly
curl http://localhost:3000/skill/trading-risk-position-sizing
```

---

### curl Examples

#### Simple Health Check

```bash
curl http://localhost:3000/health | jq .
```

**Output:**

```json
{
  "status": "healthy",
  "timestamp": "2026-04-30T12:00:00Z",
  "version": "1.0.0"
}
```

---

#### Route a Complex Task

```bash
curl -X POST http://localhost:3000/route \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Implement position sizing for a crypto trading strategy with 2% risk per trade",
    "context": {"market": "crypto", "riskTolerance": "conservative"},
    "constraints": {"maxSkills": 2, "domain": "trading"}
  }' | jq .
```

---

#### List Skills by Domain

```bash
# Note: Filtering is done client-side from the /skills response
curl http://localhost:3000/skills | \
  jq '[.[] | select(.domain == "trading")]'
```

---

#### View Routing History

```bash
curl http://localhost:3000/access-log | \
  jq '.entries[:5] | .[].task'
```

**Output:**

```
"Review this Python code for security issues"
"Implement a stop loss strategy"
"Deploy a Kubernetes manifest to production"
...
```

---

### Automation Examples

#### Reload Skills After Git Push

```bash
#!/bin/bash
# scripts/reload-skill-router.sh

# Push new skills
git add -A
git commit -m "feat: add new trading skills"
git push origin main

# Reload router
curl -X POST http://localhost:3000/reload

# Wait for reload to complete
sleep 2

# Verify
curl http://localhost:3000/stats | jq '.skills.totalSkills'
```

---

#### Monitor Skill Router Health

```bash
#!/bin/bash
# scripts/monitor-router.sh

HEALTH=$(curl -s http://localhost:3000/health)

if echo "$HEALTH" | jq -e '.status == "healthy"' > /dev/null; then
  echo "✅ Skill router is healthy"
  curl -s http://localhost:3000/stats | jq '(.skills.totalSkills | tostring) + " skills loaded"'
else
  echo "❌ Skill router is unhealthy"
  exit 1
fi
```

---

#### Search Skills by Trigger

```bash
#!/bin/bash
# scripts/search-skills.sh

SEARCH_TERM="$1"

curl -s http://localhost:3000/skills | \
  jq -r ".[] | select(.triggers | contains([\"$SEARCH_TERM\"])) | \"\(.name): \(.description)\""
```

**Usage:**

```bash
./scripts/search-skills.sh "stop loss"
```

---

## Error Scenarios and Solutions

### Router Unavailable

**Error:**

```
curl: (7) Failed to connect to localhost port 3000: Connection refused
```

**Solution:**

```bash
# Check if container is running
docker ps --filter name=skill-router

# Start if not running
docker start skill-router

# Or rebuild and start fresh
docker build -t skill-router .
docker run -d --name skill-router -p 3000:3000 skill-router
```

---

### Skill Not Found

**Error:**

```json
{
  "error": "Skill 'nonexistent-skill' not found"
}
```

**Solution:**

```bash
# List all available skills
curl http://localhost:3000/skills | jq '.[].name'

# Check the skill name matches exactly (case-sensitive)
curl http://localhost:3000/skill/coding-code-review
```

---

### Invalid Request Body

**Error:**

```json
{
  "error": "Missing required field: task"
}
```

**Solution:**

Ensure all required fields are present:

```bash
curl -X POST http://localhost:3000/route \
  -H "Content-Type: application/json" \
  -d '{"task": "my task description"}'
```

---

## API Versioning

The API uses path-based versioning. Current version: `v1`

- All endpoints are available at `/v1/endpoint`
- The root path (`/`) is an alias for `/v1/`
- Version is included in the `/health` response

**Example:**

```bash
curl http://localhost:3000/v1/health
```

---

## Rate Limiting

No rate limiting is applied to the API. However, the router implements:
- Request queuing during high load
- Timeout handling (30 second max per request)
- Graceful degradation when skills are unavailable

---

## Troubleshooting

### Common Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| Router not starting | `curl: connection refused` | Check Docker container status, view logs |
| Skills not loading | `/skills` returns empty array | Run `/reload`, check `skills/` directory |
| High latency | `/route` takes > 1 second | Check system resources, reduce `maxSkills` |
| Skills not updated | New skills not found after git pull | Run `/reload` endpoint |

---

## Related Documentation

- [Skill Router GitHub](https://github.com/agent-skill-router)
- [Skill Format Specification](./SKILL_FORMAT_SPEC.md)
- [Skills Index](./skills-index.json)
- [Agent Guide](./AGENTS.md)

---

*Last updated: 2026-04-30*
