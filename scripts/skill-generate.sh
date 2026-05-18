#!/usr/bin/env bash
# =============================================================================
# skill-generate.sh — Generate new skills using the Skill Router API + Opencode
# =============================================================================
#
# Generates SKILL.md files programmatically by combining:
#   1. Opencode (llamacpp/anomaly-llama-cpp-model) for intelligent generation
#   2. Skill Router API for domain context and relevant skill discovery
#   3. Automated validation and git integration
#   4. Supporting file updates (skills-index.json, README.md, API reload)
#
# USAGE:
#   ./scripts/skill-generate.sh "Generate a skill about X" [OPTIONS]
#
# OPTIONS:
#   -d, --domain DOMAIN       Domain (cncf, coding, agent, go, linux, trading,
#                             programming, writing, or NEW_DOMAIN)
#   -n, --name NAME           Skill name (kebab-case, auto-inferred if omitted)
#   -t, --tags TAG1,TAG2,...  Comma-separated tags
#   --no-push                 Save locally only, do not commit/push
#   --domain-list             List all domains and their skill counts
#   --help                    Show this help message
#
# EXAMPLES:
#   ./scripts/skill-generate.sh "Generate a skill about Kubernetes networking"
#   ./scripts/skill-generate.sh "Add a Go concurrency pattern for rate limiting" \
#       -d go -n rate-limiting
#   ./scripts/skill-generate.sh "Create a trading skill about VWAP strategies" \
#       --no-push
#
# =============================================================================

set -euo pipefail

# ─── Defaults ─────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$PROJECT_ROOT/skills"
INSTALL_CONF="$PROJECT_ROOT/install-skill-router.conf"
SKILL_FORMAT_SPEC="$PROJECT_ROOT/SKILL_FORMAT_SPEC.md"
API_URL="http://localhost:3000"
OPENCODE_MODEL="llamacpp/anomaly-llama-cpp-model"

# Valid domains
VALID_DOMAINS=("agent" "cncf" "coding" "go" "linux" "programming" "trading" "writing")

# ─── State ────────────────────────────────────────────────────────────────────
TASK=""
DOMAIN=""
NAME=""
TAGS=""
NO_PUSH=false
DOMAIN_LIST=false
PUSH_ALLOWED=false

# ─── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ─── Functions ────────────────────────────────────────────────────────────────

log_info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

show_help() {
    cat <<'HELP'
Usage: ./scripts/skill-generate.sh "Task description" [OPTIONS]

Generate new skills using the Skill Router API and Opencode agent.

ARGUMENTS:
  "Task description"    Describe the skill you want to generate

OPTIONS:
  -d, --domain DOMAIN   Domain: agent, cncf, coding, go, linux, trading,
                        programming, writing, or a new domain name
  -n, --name NAME       Skill name in kebab-case (auto-inferred from task)
  -t, --tags TAGS       Comma-separated tags (e.g., "kubernetes,networking")
  --no-push             Save locally only, do not commit/push to git
  --domain-list         List all domains and their skill counts
  --help                Show this help message

EXAMPLES:
  ./scripts/skill-generate.sh "Generate a skill about Kubernetes networking"
  ./scripts/skill-generate.sh "Add a Go rate limiting pattern" -d go -n rate-limiting
  ./scripts/skill-generate.sh "Create a VWAP trading strategy" --no-push
HELP
}

check_push_permission() {
    # Check if push is allowed based on config and git status

    # 1. Check install-skill-router.conf setting
    local contribute="true"
    if [[ -f "$INSTALL_CONF" ]]; then
        contribute=$(grep "^AUTO_SKILL_CONTRIBUTE" "$INSTALL_CONF" 2>/dev/null | cut -d= -f2 | tr -d '[:space:]' || echo "true")
    fi

    # 2. Check --no-push flag
    if [[ "$NO_PUSH" == "true" ]]; then
        log_warn "Push disabled (--no-push flag)"
        PUSH_ALLOWED=false
        return
    fi

    # 3. Check config
    if [[ "$contribute" != "true" ]]; then
        log_warn "Push disabled by install-skill-router.conf (AUTO_SKILL_CONTRIBUTE=false)"
        PUSH_ALLOWED=false
        return
    fi

    # 4. Check git remote exists
    if ! git remote get-url origin &>/dev/null; then
        log_warn "No git remote 'origin' configured — saving locally only"
        PUSH_ALLOWED=false
        return
    fi

    # 5. Check if we can actually push (dry test)
    if git push --dry-run origin main &>/dev/null; then
        PUSH_ALLOWED=true
        log_ok "Push to git is enabled"
    else
        log_warn "Cannot push to git (network/auth issue) — saving locally only"
        PUSH_ALLOWED=false
    fi
}

list_domains() {
    echo "Skill Router Domains:"
    echo "====================="

    # Try API first
    if curl -sf "$API_URL/health" &>/dev/null; then
        local total
        total=$(curl -sf "$API_URL/stats" | python3 -c "import sys,json; print(json.load(sys.stdin)['skills']['totalSkills'])" 2>/dev/null || echo "unknown")
        echo ""
        echo "API Reports: $total total skills"
        echo ""
    fi

    # Count skills per domain from the repo
    if [[ -d "$SKILLS_DIR" ]]; then
        for domain in "$SKILLS_DIR"/*/; do
            if [[ -d "$domain" ]]; then
                local domain_name
                domain_name=$(basename "$domain")
                local count
                count=$(find "$domain" -name "SKILL.md" 2>/dev/null | wc -l)
                printf "  %-20s %d skills\n" "$domain_name" "$count"
            fi
        done

        # Also check for domains from the API
        local api_total
        api_total=$(curl -sf "$API_URL/stats" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['skills']['totalSkills'])" 2>/dev/null || echo "0")
        local repo_total
        repo_total=$(find "$SKILLS_DIR" -name "SKILL.md" 2>/dev/null | wc -l)

        if [[ "$api_total" != "$repo_total" && "$api_total" != "0" ]]; then
            local diff=$((api_total - repo_total))
            if [[ "$diff" -gt 0 ]]; then
                echo ""
                echo "  ...and $diff skills sourced from GitHub/remote"
            fi
        fi
    fi
}

infer_domain() {
    local task_lower
    task_lower=$(echo "$TASK" | tr '[:upper:]' '[:lower:]')

    # Keyword-based domain inference
    if echo "$task_lower" | grep -qE "agent|orchestrat|dispatch|rout|conductor|multi-agent|agent workflow"; then
        echo "agent"
    elif echo "$task_lower" | grep -qE "cncf|kubernetes|k8s|docker|container|helm|istio|envoy|service mesh|cloud native|kafka|rabbitmq|etcd|consul|vault"; then
        echo "cncf"
    elif echo "$task_lower" | grep -qE "go |golang|goroutine|channel|gofmt|go mod|gopher|golang.org"; then
        echo "go"
    elif echo "$task_lower" | grep -qE "linux|kernel|systemd|bash|shell|nftables|selinux|filesystem|procfs|sysctl|udev"; then
        echo "linux"
    elif echo "$task_lower" | grep -qE "trading|stock|crypto|forex|futures|options|quant|alpha|market|order|execution|portfolio|risk|backtest|signal|algo|momentum|mean reversion|stat arb|pairs|vwap|twap|slippage|fill"; then
        echo "trading"
    elif echo "$task_lower" | grep -qE "algorithm|sorting|search|graph|dp|dynamic programming|complexity|big o|data structure|tree|hash|binary|heap|stack|queue|linked list|dynamic|recursion|greedy"; then
        echo "programming"
    elif echo "$task_lower" | grep -qE "python|javascript|typescript|rust|java|c\+\+|ruby|php|scala|swift|kotlin|web|api|fullstack|frontend|backend|database|orm|sql|react|angular|vue"; then
        echo "coding"
    else
        echo "coding"  # Default to coding
    fi
}

parse_ndjson_text() {
    # Parse opencode NDJSON output, extract text from the FIRST 'text' event only.
    # Opencode appends a skill citation footer (> 📖 skill(...)) as a separate event.
    # We only want the actual LLM response text.

    local found_first=false
    while IFS= read -r line; do
        local etype
        etype=$(echo "$line" | jq -r '.type // empty' 2>/dev/null)
        if [[ "$etype" == "text" && "$found_first" == "false" ]]; then
            found_first=true
            local text
            text=$(echo "$line" | jq -r '.part.text // empty' 2>/dev/null)
            # Strip the automatic skill citation footer that opencode appends
            text=$(echo "$text" | sed '/^> 📖 skill/d; s/^> 📖 skill.*$//')
            printf '%s' "$text"
        fi
    done
}

generate_name() {
    # Use opencode to intelligently name the skill based on its actual purpose.
    # Returns a kebab-case name, max 100 chars. Retries up to 3 times.
    # Robust against opencode footer corruption by extracting kebab-case words.

    local domain="$1"
    local max_attempts=3
    local attempt=0

    while [[ $attempt -lt $max_attempts ]]; do
        attempt=$((attempt + 1))

        local raw_output
        raw_output=$(opencode run "You are a skill naming engine for the OpenCode Agent Skill Router. Output ONLY a single kebab-case skill name on one line. No explanation, no preamble, no footer. Example: design-patterns. The skill is about: $TASK" \
            -m "$OPENCODE_MODEL" \
            --dangerously-skip-permissions \
            --format json 2>/dev/null | parse_ndjson_text)

        # Extract ALL kebab-case candidates from raw output (words with 3+ alpha chars,
        # separated by hyphens). This ignores footers, emojis, markdown, etc.
        # A valid name is 3-100 chars, only lowercase letters, digits, and hyphens.
        local name
        # First, clean the raw output to find the best kebab-case name
        name=$(echo "$raw_output" | tr -cs '[:lower:][:digit:]-' '\n' | \
            grep -E '^[a-z]{3,}' | \
            head -1)

        # Validate length
        if [[ ${#name} -le 100 && ${#name} -ge 3 ]]; then
            echo "$name"
            return 0
        fi

        log_warn "Attempt $attempt: no valid name extracted (${#name:-0} chars), retrying..."
    done

    log_error "Name generation failed all $max_attempts attempts"
    # Final fallback: domain-based
    echo "${domain}-skill"
    return 1
}

check_api_health() {
    if ! curl -sf "$API_URL/health" &>/dev/null; then
        log_warn "Skill Router API at $API_URL is not available"
        log_info "Starting API... (it may take a moment to initialize)"

        # Try to start the API
        if command -v docker &>/dev/null; then
            log_info "Attempting to start skill-router container..."
            if docker ps --filter name=skill-router --format '{{.Names}}' | grep -q "skill-router"; then
                docker start skill-router 2>/dev/null || true
            else
                log_warn "skill-router container not found. Start it with:"
                log_info "  docker run -d --name skill-router -p 3000:3000 agent-skill-router:latest"
            fi

            # Wait for it to be ready
            local retries=30
            while [[ $retries -gt 0 ]]; do
                if curl -sf "$API_URL/health" &>/dev/null; then
                    log_ok "Skill Router API is ready"
                    return 0
                fi
                sleep 2
                retries=$((retries - 1))
            done
            log_warn "API did not become available in time"
            return 1
        fi

        return 1
    fi
    return 0
}

get_relevant_skills() {
    local max_skills="${1:-5}"
    local skills_json=""

    if curl -sf "$API_URL/health" &>/dev/null; then
        log_info "Querying Skill Router API for relevant skills..."

        local route_response
        route_response=$(curl -sf -X POST "$API_URL/route" \
            -H "Content-Type: application/json" \
            -d "{
                \"task\": \"$TASK\",
                \"context\": {\"domain\": \"$DOMAIN\", \"type\": \"new\"},
                \"constraints\": {\"maxSkills\": $max_skills}
            }")

        skills_json=$(echo "$route_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    skills = [s.get('name','') for s in data.get('selectedSkills', []) if s.get('name')]
    if not skills:
        skills = [s for s in data.get('candidatePool', [])][:3]
    print(','.join(skills))
except:
    print('')
" 2>/dev/null || echo "")
    fi

    echo "$skills_json"
}

fetch_skill_content() {
    local skill_name="$1"
    local content=""

    # Try API first
    if curl -sf "$API_URL/health" &>/dev/null; then
        content=$(curl -sf "$API_URL/skill/$skill_name" 2>/dev/null || echo "")
    fi

    # Fallback to local file
    if [[ -z "$content" ]]; then
        local path
        path=$(find "$SKILLS_DIR" -path "*/$skill_name/SKILL.md" -type f 2>/dev/null | head -1)
        if [[ -n "$path" && -f "$path" ]]; then
            content=$(cat "$path")
        fi
    fi

    echo "$content"
}

build_skill_prompt() {
    # Build the full user prompt for opencode.
    # Includes critical format rules (summarized from SKILL_FORMAT_SPEC.md)
    # and relevant skill context from the API.

    local domain="$1"
    local skill_name="$2"
    local tags="$3"

    # Get content of relevant skills for context (up to 2)
    local skill_context=""
    local relevant_skills=""
    if curl -sf "$API_URL/health" &>/dev/null; then
        relevant_skills=$(get_relevant_skills 2)
    fi

    if [[ -n "$relevant_skills" ]]; then
        IFS=',' read -ra skill_arr <<< "$relevant_skills"
        local count=0
        for s in "${skill_arr[@]}"; do
            if [[ -n "$s" && $count -lt 2 ]]; then
                local content
                content=$(fetch_skill_content "$s")
                if [[ -n "$content" ]]; then
                    local short_content
                    short_content=$(echo "$content" | head -30)
                    skill_context+="# Relevant skill: $s
$short_content
---

"
                fi
                count=$((count + 1))
            fi
        done
    fi

    cat <<PROMPT
TASK: $TASK

DOMAIN: $domain
SKILL NAME: $skill_name
TAGS: $tags

FORMAT REQUIREMENTS (from SKILL_FORMAT_SPEC.md):
- Must start with YAML frontmatter delimited by ---, containing at minimum:
  - name: (must match directory name in kebab-case)
  - description: (single line, active verb, specific, <200 chars)
  - license: MIT
  - compatibility: opencode
  - metadata: { version, domain, triggers (3-8 terms), role, scope, output-format, content-types }
- Must have H1 title (human-readable, not kebab-case name)
- Must have role/purpose paragraph (1-3 sentences, model-perspective)
- Must have "## When to Use" section with specific bullet points
- Must have "## Core Workflow" or "## Constraints" section
- Must have "## Constraints" with MUST DO and MUST NOT DO sections

DOMAIN-SPECIFIC RULES:
- coding: Include BAD vs GOOD code examples, reference OWASP/SOLID/DRY
- trading: Python with typed signatures, risk constraints, APEX layout
- go: Idiomatic Go with error wrapping (%w), BAD vs GOOD examples
- linux: Bash with set -euo pipefail, security, idempotent operations
- cncf: YAML manifests, architecture diagrams, integration patterns
- agent: ASCII flow diagram, fallback/error routing
- programming: Algorithm pseudocode, complexity tables
- writing: Before/after text comparisons

LANGUAGE: Default to bash/CLI. Only Python for trading/risk, Go for go/*, YAML/JSON for manifests.

CODE: Every code block must contain substantive, complete, working code — NO pass statements, NO return {}, NO placeholder comments like 'example pattern for' or 'TODO'.

OUTPUT FORMAT: Return ONLY raw SKILL.md text — no markdown code fences, no preamble, no explanation, no footer.

RELEVANT SKILL CONTEXT:
$skill_context
PROMPT
}

generate_skill() {
    local domain="$1"
    local skill_name="$2"
    local tags="$3"

    log_info "Generating skill: $domain/$skill_name"
    log_info "Task: $TASK"

    local output_file="$SKILLS_DIR/$domain/$skill_name/SKILL.md"
    local output_dir
    output_dir=$(dirname "$output_file")

    # Create output directory
    mkdir -p "$output_dir"

    # Check if skill already exists
    if [[ -f "$output_file" ]]; then
        log_warn "Skill already exists at $output_file"
        log_info "Skipping generation (existing file preserved)"
        return 1
    fi

    # Build the prompt
    local user_prompt
    user_prompt=$(build_skill_prompt "$domain" "$skill_name" "$tags")

    # Use opencode for skill generation
    log_info "Generating skill with opencode (model: $OPENCODE_MODEL)..."

    local GENERATED_SKILL
    GENERATED_SKILL=$(opencode run "$user_prompt" \
        -m "$OPENCODE_MODEL" \
        --dangerously-skip-permissions \
        --format json 2>/dev/null | parse_ndjson_text)

    log_info "Generated ${#GENERATED_SKILL} chars, first 100: ${GENERATED_SKILL:0:100}"

    # Trim whitespace and check for empty
    local trimmed
    trimmed=$(echo "$GENERATED_SKILL" | tr -d '[:space:]')
    if [[ -z "$trimmed" ]]; then
        log_error "opencode returned empty response"
        return 1
    fi

    log_ok "Opencode generated skill content"

    # Validate the generated skill
    if ! validate_skill "$GENERATED_SKILL" "$output_file"; then
        return 1
    fi

    # Save the skill
    echo "$GENERATED_SKILL" > "$output_file"
    log_ok "Skill saved to: $output_file"

    # Show skill stats
    local line_count
    line_count=$(wc -l < "$output_file")
    log_info "Skill: $line_count lines"

    return 0
}

validate_skill() {
    local content="$1"
    local output_file="$2"
    local errors=0

    # Check YAML frontmatter
    if ! echo "$content" | grep -q "^---$"; then
        log_error "Missing YAML frontmatter"
        errors=$((errors + 1))
    fi

    # Check name field
    if ! echo "$content" | grep -q "^name:"; then
        log_error "Missing 'name' in frontmatter"
        errors=$((errors + 1))
    fi

    # Check description field
    if ! echo "$content" | grep -q "^description:"; then
        log_error "Missing 'description' in frontmatter"
        errors=$((errors + 1))
    fi

    # Check for placeholder patterns
    if echo "$content" | grep -qE "^\s*pass\s*$"; then
        log_error "Contains 'pass' statement in code (placeholder)"
        errors=$((errors + 1))
    fi

    if echo "$content" | grep -qE "return\s+\{\}"; then
        log_error "Contains 'return {}' (placeholder)"
        errors=$((errors + 1))
    fi

    if echo "$content" | grep -qE "# TODO|FIXME|example.com"; then
        log_error "Contains placeholder comments (TODO/FIXME/example.com)"
        errors=$((errors + 1))
    fi

    # Check H1 title
    if ! echo "$content" | grep -q "^# "; then
        log_error "Missing H1 title"
        errors=$((errors + 1))
    fi

    # Check minimum content (at least 150 lines)
    local line_count
    line_count=$(echo "$content" | wc -l)
    if [[ $line_count -lt 150 ]]; then
        log_warn "Skill is short ($line_count lines), may need more content"
    fi

    if [[ $errors -gt 0 ]]; then
        log_error "$errors validation errors found"
        return 1
    fi

    log_ok "Skill validation passed"
    return 0
}

update_supporting_files() {
    local domain="$1"
    local name="$2"
    local output_file="$SKILLS_DIR/$domain/$name/SKILL.md"

    if [[ ! -f "$output_file" ]]; then
        log_warn "Skill file not found, skipping supporting file updates"
        return 0
    fi

    log_info "Updating supporting files..."

    cd "$PROJECT_ROOT"

    # Regenerate skills-index.json
    if [[ -f "scripts/generate_index.py" ]]; then
        python3 scripts/generate_index.py 2>/dev/null || log_warn "skills-index.json regeneration failed (non-critical)"
        log_ok "skills-index.json updated"
    else
        log_warn "generate_index.py not found, skipping"
    fi

    # Regenerate README.md
    if [[ -f "scripts/generate_readme.py" ]]; then
        python3 scripts/generate_readme.py 2>/dev/null || log_warn "README.md regeneration failed (non-critical)"
        log_ok "README.md updated"
    else
        log_warn "generate_readme.py not found, skipping"
    fi

    # Reload skill-router API to pick up changes
    if curl -sf -X POST "$API_URL/reload" &>/dev/null; then
        log_ok "Skill Router API reloaded"
    else
        log_warn "API reload failed (non-critical — server may need restart)"
    fi
}

commit_and_push() {
    local domain="$1"
    local skill_name="$2"
    local output_file="$SKILLS_DIR/$domain/$skill_name/SKILL.md"

    if [[ ! -f "$output_file" ]]; then
        log_error "Skill file not found: $output_file"
        return 1
    fi

    # Check push permission
    check_push_permission
    if [[ "$PUSH_ALLOWED" != "true" ]]; then
        log_warn "Push to git not allowed — skill saved locally only"
        log_info "To enable push, set AUTO_SKILL_CONTRIBUTE=true in install-skill-router.conf"
        log_info "Or run with --no-push removed"
        return 0
    fi

    # Create branch
    local branch="skill/${domain}/${skill_name}"
    log_info "Creating branch: $branch"
    git checkout -b "$branch" 2>/dev/null || git checkout "$branch"

    # Add and commit
    git add "$output_file"
    git add "$SKILLS_DIR/$domain/" 2>/dev/null || true

    local commit_msg="feat($domain): add $skill_name skill"
    git commit -m "$commit_msg" 2>/dev/null || {
        log_warn "No changes to commit (file may already exist)"
        git checkout main 2>/dev/null || true
        return 0
    }

    # Push
    log_info "Pushing branch to remote..."
    if git push -u origin "$branch" 2>/dev/null; then
        log_ok "Skill pushed: $branch"
        log_info "Branch URL: https://github.com/paulpas/agent-skill-router/tree/$branch"
        log_info "Create a PR with: gh pr create --base main --head $branch --title 'feat($domain): $skill_name' --body 'Generated skill for: $TASK'"
    else
        log_warn "Push failed — committing locally only"
        git checkout main 2>/dev/null || true
        return 1
    fi

    git checkout main 2>/dev/null || true
}

# ─── Main ─────────────────────────────────────────────────────────────────────

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -d|--domain)
                DOMAIN="$2"
                shift 2
                ;;
            -n|--name)
                NAME="$2"
                shift 2
                ;;
            -t|--tags)
                TAGS="$2"
                shift 2
                ;;
            --no-push)
                NO_PUSH=true
                shift
                ;;
            --domain-list)
                DOMAIN_LIST=true
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                TASK="$1"
                shift
                ;;
        esac
    done

    # Domain list mode
    if [[ "$DOMAIN_LIST" == "true" ]]; then
        list_domains
        exit 0
    fi

    # Require task
    if [[ -z "$TASK" ]]; then
        log_error "No task description provided"
        echo ""
        show_help
        exit 1
    fi

    # Check API
    check_api_health || true

    # Infer domain if not specified
    if [[ -z "$DOMAIN" ]]; then
        DOMAIN=$(infer_domain)
        log_info "Inferred domain: $DOMAIN"
    fi

    # Validate domain
    local domain_valid=false
    for d in "${VALID_DOMAINS[@]}"; do
        if [[ "$d" == "$DOMAIN" ]]; then
            domain_valid=true
            break
        fi
    done

    if [[ "$domain_valid" != "true" ]]; then
        log_warn "Domain '$DOMAIN' is not in the standard list: ${VALID_DOMAINS[*]}"
        log_info "Proceeding anyway (new domain)"
    fi

    # Generate name with opencode if not specified
    if [[ -z "$NAME" ]]; then
        NAME=$(generate_name "$DOMAIN")
        log_info "Generated skill name: $NAME (${#NAME} chars)"
    fi

    # Check for existing skill
    local existing
    existing=$(find "$SKILLS_DIR" -path "*/$DOMAIN/$NAME/SKILL.md" -type f 2>/dev/null | head -1)
    if [[ -n "$existing" ]]; then
        log_error "Skill already exists at: $existing"
        exit 1
    fi

    # Generate the skill
    echo ""
    log_info "Generating skill..."
    echo "  Domain: $DOMAIN"
    echo "  Name:   $NAME"
    echo "  Task:   $TASK"
    echo ""

    if ! generate_skill "$DOMAIN" "$NAME" "$TAGS"; then
        log_error "Skill generation failed"
        exit 1
    fi

    # Update supporting files (skills-index.json, README.md, API reload)
    update_supporting_files "$DOMAIN" "$NAME"

    # Commit and push
    commit_and_push "$DOMAIN" "$NAME"

    echo ""
    log_ok "Done! Skill created at: $SKILLS_DIR/$DOMAIN/$NAME/SKILL.md"
}

main "$@"
