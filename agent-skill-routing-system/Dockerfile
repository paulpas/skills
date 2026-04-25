# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json tsconfig.json ./
RUN npm ci
COPY src/ ./src/
RUN npm run build

# Stage 2: Runtime
FROM node:20-alpine AS runtime
ARG COMPRESSION_LEVEL=4
RUN apk add --no-cache git
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm ci --omit=dev
COPY samples/ ./samples/
EXPOSE 3000
# SKILLS_DIRECTORY is optional when GITHUB_SKILLS_ENABLED=true (remote index is used instead).
# Mount -v /your/skills:/skills:ro only if you want a local override of skill content.
ENV SKILLS_DIRECTORY=/skills
ENV LLM_PROVIDER=openai
ENV LLM_MODEL=gpt-4o-mini
ENV EMBEDDING_PROVIDER=openai
ENV EMBEDDING_MODEL=text-embedding-3-small
# For llamacpp: set to http://host.docker.internal:8080 to reach host's llama.cpp
ENV LLAMACPP_BASE_URL=http://host.docker.internal:8080
ENV GITHUB_SKILLS_ENABLED=true
ENV GITHUB_SKILLS_REPO=https://github.com/paulpas/skills
# Base URL for GitHub raw content — used for skills-index.json and on-demand SKILL.md fetches
ENV GITHUB_RAW_BASE_URL=https://raw.githubusercontent.com/paulpas/skills/main
ENV SKILL_CACHE_DIR=/cache/skills
ENV SKILL_SYNC_INTERVAL=3600
# GITHUB_TOKEN= (optional, set at runtime for private repos or higher rate limits)
# /skills volume mount is optional — skill content is fetched on-demand from GitHub
VOLUME ["/cache"]
ENV LOG_LEVEL=info
# SKILL_COMPRESSION_LEVEL: 0-10+
# 0=off, 1=5% savings, 2=12%, 3=18%, 4=28%, 5=35%, etc.
# Usage: docker build --build-arg COMPRESSION_LEVEL=N .
# Examples:
#   COMPRESSION_LEVEL=0 → no compression (default in source)
#   COMPRESSION_LEVEL=2 → 12% token savings (conservative)
#   COMPRESSION_LEVEL=4 → 28% token savings (recommended default)
#   COMPRESSION_LEVEL=7 → 55% token savings (aggressive)
ENV SKILL_COMPRESSION_LEVEL=${COMPRESSION_LEVEL}
ENV NODE_ENV=production
HEALTHCHECK --interval=60s --timeout=10s --start-period=90s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/health | grep -q '"ready":true' || exit 1
CMD ["node", "dist/index.js"]
