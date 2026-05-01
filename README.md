# Agent Skill Router — Intelligent Skill Routing for AI Agents

**An AI skill routing system that automatically selects and injects the right expertise into your AI's context.** With 1,827+ skills across 5 domains and built-in compression, the router delivers expert knowledge without manual commands.

```
You → "review this Python code for security issues"
      ↓
skill-router auto-fires → embeds task → vector search → LLM ranks → loads skills
      ↓
Full expert skills injected into context — AI answers as expert reviewer
```

**Key Features:**
- 🎯 **1,827+ Skills** across Agent, CNCF, Coding, Programming, and Trading domains
- 🔄 **Auto-Routing** — tasks automatically match the most relevant skills
- 🗜️ **SkillCompressor** — reduce token overhead by 28-65%
- ⚡ **Fast** — ~10ms warm, ~3.5s cold responses
- 🔌 **MCP Integration** — works with OpenCode's `route_to_skill` tool

---

## Quick Start

### Installation (OpenAI)

```bash
git clone https://github.com/paulpas/agent-skill-router
cd agent-skill-router
OPENAI_API_KEY=sk-... ./install-skill-router.sh --integrate-opencode
```

**Full installation instructions:** [AGENT-MCP.md](./AGENT-MCP.md)

### Local Model (no API key required)

```bash
./install-skill-router.sh \
  --provider llamacpp \
  --embedding-provider llamacpp \
  --llamacpp-url http://localhost:8080
```

---

## How It Works

The skill router is an **MCP (Model Context Protocol) server** that routes tasks to the most relevant skills using:

1. **Semantic Search** — OpenAI embeddings + cosine similarity for candidate retrieval
2. **LLM Ranking** — Intelligent selection and reasoning with gpt-4o-mini (or Anthropic/Claude)
3. **Caching** — Multi-layer cache for optimal performance
4. **Compression** — SkillCompressor reduces token overhead by 28-65%

**Result:** Only the top 1-3 most relevant skills are loaded per request, saving tokens and improving response quality.

---

## Documentation

| File | Purpose |
|------|---------|
| **[AGENT-MCP.md](./AGENT-MCP.md)** | Installation and setup guide for OpenCode, Claude, and other MCP clients |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | Deep dive into system architecture, components, and design patterns |
| **[API.md](./API.md)** | Complete API documentation with curl examples for all endpoints |
| **[SKILL_FORMAT_SPEC.md](./SKILL_FORMAT_SPEC.md)** | Formal skill file specification for creating new skills |

---

## Skill Creation

**New to skill creation?** Start here:

**[AGENTS.md](./AGENTS.md)** — Complete guide for creating new skills with:
- Frontmatter requirements
- Content structure templates
- Trigger engineering best practices
- Quality checklist and common pitfalls

---

## Common Questions

**Have questions?** See the **[README.md](./README.md)** sections above, or check **[AGENTS.md](./AGENTS.md)** for skill documentation guidelines.

---

## Domains

| Domain | Count | Focus |
|--------|-------|-------|
| Agent | 271 | AI orchestration, routing, task decomposition |
| CNCF | 365 | Kubernetes, cloud-native, DevOps |
| Coding | 317 | Software patterns, security, testing |
| Programming | 791 | Algorithms, frameworks, languages |
| Trading | 83 | Execution, risk management, ML models |

---

## License

MIT — All skills are freely available and redistributable.
