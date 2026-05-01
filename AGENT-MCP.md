# Installing the Agent Skill Router

**An AI skill routing system that automatically selects and injects the right expertise into your AI's context.**

> **Quick Overview:** The Agent Skill Router is a Docker-based service that routes tasks to the most relevant expert skills from a library of 1,827 skills across 5 domains (Agent, CNCF, Coding, Programming, Trading). It integrates with OpenCode, Claude, and other MCP-compatible clients.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Environment Variables Reference](#environment-variables-reference)
- [Provider-Specific Configurations](#provider-specific-configurations)
- [OpenCode Integration](#opencode-integration)
- [Claude Integration](#claude-integration)
- [Verification Steps](#verification-steps)
- [Common Issues](#common-issues)

---

## Quick Start

### Basic Installation (OpenAI)

```bash
git clone https://github.com/paulpas/agent-skill-router
cd agent-skill-router
OPENAI_API_KEY=sk-... ./install-skill-router.sh --integrate-opencode
```

### Local Model (No API Keys)

```bash
./install-skill-router.sh \
  --provider llamacpp \
  --embedding-provider llamacpp \
  --llamacpp-url http://localhost:8080 \
  --integrate-opencode
```

**What happens:**
1. Docker image `skill-router:latest` is built
2. Container `skill-router` runs on port 3000
3. OpenCode config is updated with MCP integration
4. Systemd user service is enabled (Linux)

---

## Prerequisites

- **Docker** installed and running
- **curl** or **wget** for health checks
- **jq** or **python3** for JSON parsing

```bash
# Verify prerequisites
docker --version
curl --version
```

---

## Installation Methods

### Method 1: OpenAI (Default)

```bash
# With inline API key
./install-skill-router.sh --openai-key sk-...

# Or set environment variable first
export OPENAI_API_KEY=sk-...
./install-skill-router.sh
```

**Default model:** `gpt-4o-mini` for embeddings and ranking  
**Custom model:** Add `--model gpt-4o` to override

### Method 2: Anthropic

```bash
# With inline API key
./install-skill-router.sh \
  --provider anthropic \
  --anthropic-key sk-ant-... \
  --model claude-3-5-haiku-20241022

# Or set environment variable first
export ANTHROPIC_API_KEY=sk-ant-...
./install-skill-router.sh --provider anthropic --model claude-3-5-haiku-20241022
```

**Supported models:**
- `claude-3-5-haiku-20241022`
- `claude-3-5-sonnet-20240620`
- `claude-3-opus-20240229`

### Method 3: Local llama.cpp (No API Keys)

```bash
# Start llama.cpp server first
./server -m models/llama-3-8b.Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --embedding

# Then install router
./install-skill-router.sh \
  --provider llamacpp \
  --embedding-provider llamacpp \
  --llamacpp-url http://localhost:8080 \
  --integrate-opencode
```

**Requirements:**
- llama.cpp server with `/v1/chat/completions` and `/v1/embeddings` endpoints
- OpenAI-compatible API format

---

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key | For OpenAI provider | N/A |
| `ANTHROPIC_API_KEY` | Anthropic API key | For Anthropic provider | N/A |
| `LLM_PROVIDER` | LLM provider: `openai`, `anthropic`, `llamacpp` | No | `openai` |
| `LLM_MODEL` | Model name | No | Provider default |
| `EMBEDDING_PROVIDER` | Embedding provider | No | `openai` |
| `EMBEDDING_MODEL` | Embedding model name | No | Provider default |
| `LLAMACPP_BASE_URL` | llama.cpp server URL | For llamacpp provider | `http://host.docker.internal:8080` |
| `GITHUB_TOKEN` | GitHub token for higher rate limits | No | None |
| `SKILL_SYNC_INTERVAL` | GitHub sync interval (seconds) | No | `3600` (1 hour) |

---

## Provider-Specific Configurations

### OpenAI Configuration

```bash
# Basic installation
OPENAI_API_KEY=sk-... ./install-skill-router.sh --integrate-opencode

# With custom model
OPENAI_API_KEY=sk-... ./install-skill-router.sh \
  --openai-key sk-... \
  --model gpt-4o \
  --embedding-model text-embedding-3-large \
  --integrate-opencode
```

**Environment setup:**
```bash
export OPENAI_API_KEY=sk-...
export LLM_MODEL=gpt-4o
export EMBEDDING_MODEL=text-embedding-3-large
./install-skill-router.sh --integrate-opencode
```

### Anthropic Configuration

```bash
# Basic installation
ANTHROPIC_API_KEY=sk-ant-... ./install-skill-router.sh \
  --provider anthropic \
  --anthropic-key sk-ant-... \
  --model claude-3-5-haiku-20241022 \
  --integrate-opencode

# With environment variables
export ANTHROPIC_API_KEY=sk-ant-...
export LLM_PROVIDER=anthropic
export LLM_MODEL=claude-3-5-sonnet-20240620
./install-skill-router.sh --integrate-opencode
```

### llama.cpp Configuration

```bash
# Step 1: Start llama.cpp server with embeddings
./server -m models/llama-3-8b.Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8080 \
  --embedding

# Step 2: Install router (no API keys required!)
./install-skill-router.sh \
  --provider llamacpp \
  --embedding-provider llamacpp \
  --llamacpp-url http://localhost:8080 \
  --integrate-opencode
```

**Important:** Both LLM and embeddings must be served by the same llama.cpp instance.

---

## OpenCode Integration

The `--integrate-opencode` flag automatically configures OpenCode to use the skill router.

### What It Does

1. **Fetches** `skill-router-api.md` from GitHub to `~/.config/opencode/skill-router-api.md`
2. **Adds** this file to OpenCode's `instructions` array in `opencode.json`
3. **Installs** `skill-router-mcp.js` bridge script to `~/.config/opencode/skill-router-mcp.js`
4. **Injects** MCP server configuration into `opencode.json` `mcp` section
5. **Validates** JSON syntax of the config file

### Manual Integration (If Needed)

If you didn't use `--integrate-opencode` during installation:

```bash
# Fetch the API documentation
mkdir -p ~/.config/opencode
curl -fsSL https://raw.githubusercontent.com/paulpas/skills/main/agent-skill-routing-system/skill-router-api.md \
  -o ~/.config/opencode/skill-router-api.md

# Install the MCP bridge script
curl -fsSL https://raw.githubusercontent.com/paulpas/skills/main/agent-skill-routing-system/skill-router-mcp.js \
  -o ~/.config/opencode/skill-router-mcp.js
```

Then manually edit `~/.config/opencode/opencode.json`:

```json
{
  "instructions": [
    "~/.config/opencode/skill-router-api.md"
  ],
  "mcp": {
    "skill-router": {
      "type": "local",
      "command": ["/usr/bin/node", "~/.config/opencode/skill-router-mcp.js"],
      "enabled": true
    }
  }
}
```

### OpenCode Configuration Checklist

- [ ] `skill-router-api.md` exists at `~/.config/opencode/skill-router-api.md`
- [ ] `skill-router-mcp.js` exists at `~/.config/opencode/skill-router-mcp.js`
- [ ] `~/.config/opencode/opencode.json` has `instructions` array with the API doc path
- [ ] `~/.config/opencode/opencode.json` has `mcp.skill-router` entry
- [ ] OpenCode is restarted after changes

---

## Claude Integration

The `--integrate-claude` flag configures Claude Desktop to use the skill router via MCP.

### What It Does

1. **Installs** `skill-router-mcp.js` bridge script to `~/.config/claude/skill-router-mcp.js`
2. **Injects** MCP server configuration into `claude.json` `mcpServers` section
3. **Validates** JSON syntax

### Installation

```bash
./install-skill-router.sh --integrate-claude
```

### Manual Integration

If you need to integrate manually:

```bash
# Install the MCP bridge script
mkdir -p ~/.config/claude
curl -fsSL https://raw.githubusercontent.com/paulpas/skills/main/agent-skill-routing-system/skill-router-mcp.js \
  -o ~/.config/claude/skill-router-mcp.js
```

Then manually edit `~/.claude.json` or `~/.config/claude/claude.json`:

```json
{
  "mcpServers": {
    "skill-router": {
      "command": "/usr/bin/node",
      "args": ["~/.config/claude/skill-router-mcp.js"],
      "env": {}
    }
  }
}
```

---

## Verification Steps

### 1. Health Check

```bash
# Check if container is running
docker ps --filter name=skill-router

# Check health endpoint
curl http://localhost:3000/health | jq .
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-10-27T...",
  "version": "1.0.0",
  "ready": true,
  "skillsLoaded": 1827,
  "latencyMs": 10
}
```

### 2. Skills Loaded

```bash
curl http://localhost:3000/stats | jq .
```

Expected output should show:
- `totalSkills: 1827`
- `categories: ["agent", "cncf", "coding", "programming", "trading"]`

### 3. Route a Test Task

```bash
curl -X POST http://localhost:3000/route \
  -H "Content-Type: application/json" \
  -d '{
    "task": "review this Python code for security issues",
    "context": {},
    "constraints": {"maxSkills": 3}
  }' | jq .
```

### 4. OpenCode Integration Test

In OpenCode, type any task and verify:
- The `route_to_skill` tool is available
- Skills are automatically routed based on task keywords
- The skill content is injected into context

### 5. Docker Logs

```bash
# View live logs
docker logs skill-router --tail 50 -f

# Check for errors
docker logs skill-router | grep -i error
```

---

## Common Issues

### Issue: Health Check Timeout

**Symptoms:** `Health check failed after 60 attempts`

**Solutions:**
1. Check Docker logs: `docker logs skill-router --tail 50`
2. Verify API key is correct and has credits
3. Check network connectivity: `curl http://localhost:3000/health`

### Issue: "OPENAI_API_KEY is required" Error

**Symptoms:** Installation fails with API key error

**Solutions:**
- Use `--provider llamacpp --embedding-provider llamacpp` for local setup
- Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for cloud providers
- Check that the environment variable is exported: `echo $OPENAI_API_KEY`

### Issue: OpenCode Integration Fails

**Symptoms:** `Could not find opencode.json`

**Solutions:**
1. Use `--config PATH` to specify the location:
   ```bash
   ./install-skill-router.sh --integrate-opencode --config ~/.config/opencode/opencode.json
   ```
2. Check if OpenCode is installed: `ls -la ~/.config/opencode/`

### Issue: llama.cpp Connection Failed

**Symptoms:** `LLM provider error: could not connect to llama.cpp server`

**Solutions:**
1. Verify llama.cpp is running: `curl http://localhost:8080/v1/models`
2. Check that embeddings endpoint works: `curl http://localhost:8080/v1/embeddings`
3. If using Docker Desktop, try `http://host.docker.internal:8080`

### Issue: Skills Not Loading

**Symptoms:** `ready: false` in health check for extended period

**Solutions:**
1. Wait a few minutes - skills load in background
2. Check logs: `docker logs skill-router --tail 100 -f`
3. Verify GitHub sync is working: `curl http://localhost:3000/stats`

### Issue: MCP Tools Not Available in OpenCode

**Symptoms:** `route_to_skill` tool not found

**Solutions:**
1. Restart OpenCode after installation
2. Verify `skill-router-api.md` is in `instructions` array
3. Check JSON syntax: `jq . ~/.config/opencode/opencode.json`

---

## Uninstallation

```bash
# Stop and remove container
docker stop skill-router && docker rm skill-router

# Remove image
docker rmi skill-router:latest

# Remove volume (optional - deletes cached embeddings)
docker volume rm skill-router-cache

# Clean up OpenCode integration
rm ~/.config/opencode/skill-router-api.md
rm ~/.config/opencode/skill-router-mcp.js
```

To remove the MCP entry from `opencode.json`:

```bash
# Using jq
jq 'del(.mcp.skill-router)' ~/.config/opencode/opencode.json > tmp && mv tmp ~/.config/opencode/opencode.json

# Using python3
python3 -c "import json; f=open('~/.config/opencode/opencode.json'); cfg=json.load(f); del cfg['mcp']['skill-router']; open('~/.config/opencode/opencode.json','w').write(json.dumps(cfg,indent=2))"
```

---

## Additional Resources

- [README.md](./README.md) - Project overview and features
- [AGENTS.md](./AGENTS.md) - Agent skill documentation guide
- [SKILL_FORMAT_SPEC.md](./SKILL_FORMAT_SPEC.md) - Skill file format specification
