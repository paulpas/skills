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
ARG ENABLE_LLM_COMPRESSION=true
ARG OPENAI_MODEL=gpt-4o-mini

RUN apk add --no-cache git
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm ci --omit=dev
COPY samples/ ./samples/

# Environment configuration
EXPOSE 3000
ENV SKILLS_DIRECTORY=/skills
ENV LLM_PROVIDER=openai
ENV LLM_MODEL=gpt-4o-mini
ENV EMBEDDING_PROVIDER=openai
ENV EMBEDDING_MODEL=text-embedding-3-small
ENV LLAMACPP_BASE_URL=http://host.docker.internal:8080
ENV GITHUB_SKILLS_ENABLED=true
ENV GITHUB_SKILLS_REPO=https://github.com/paulpas/skills
ENV GITHUB_RAW_BASE_URL=https://raw.githubusercontent.com/paulpas/skills/main
ENV SKILL_CACHE_DIR=/cache/skills
ENV SKILL_SYNC_INTERVAL=3600
ENV LOG_LEVEL=info

# OpenAI-based LLM compression configuration
ENV OPENAI_API_KEY=""
ENV OPENAI_MODEL="gpt-4o-mini"
ENV OPENAI_BASE_URL=""
ENV OPENAI_ORG_ID=""
ENV ENABLE_LLM_COMPRESSION="true"

# LLM-based skill compression configuration
ARG SKILL_COMPRESSION_ENABLED=true
ARG SKILL_COMPRESSION_STRATEGY=moderate
ARG SKILL_COMPRESSION_LLM_MODEL=claude-3-haiku
ARG SKILL_COMPRESSION_MEMORY_TTL_MINUTES=60
ARG SKILL_COMPRESSION_DISK_TTL_DAYS=7
ARG SKILL_COMPRESSION_LAZY_WRITE_INTERVAL_MS=5000

ENV SKILL_COMPRESSION_ENABLED=$SKILL_COMPRESSION_ENABLED
ENV SKILL_COMPRESSION_STRATEGY=$SKILL_COMPRESSION_STRATEGY
ENV SKILL_COMPRESSION_LLM_MODEL=$SKILL_COMPRESSION_LLM_MODEL
ENV SKILL_COMPRESSION_MEMORY_TTL_MINUTES=$SKILL_COMPRESSION_MEMORY_TTL_MINUTES
ENV SKILL_COMPRESSION_DISK_TTL_DAYS=$SKILL_COMPRESSION_DISK_TTL_DAYS
ENV SKILL_COMPRESSION_LAZY_WRITE_INTERVAL_MS=$SKILL_COMPRESSION_LAZY_WRITE_INTERVAL_MS

# Regex-based skill compression level (legacy)
ENV SKILL_COMPRESSION_LEVEL=${COMPRESSION_LEVEL:-4}

# Compression cache configuration
ENV COMPRESSION_CACHE_SIZE_MB="512"
ENV COMPRESSION_CACHE_TTL_HOURS="24"
ENV COMPRESSION_RETRY_THRESHOLD="2"

ENV NODE_ENV=production

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=90s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/health | grep -q '"ready":true' || exit 1

# Mount configuration
VOLUME ["/cache", "/app/cache/compressed"]

CMD ["node", "dist/index.js"]
