#!/usr/bin/env bash
# =============================================================================
# skill-generate.sh — Generate new skills using the Skill Router API
# =============================================================================
#
# Generates SKILL.md files programmatically by combining:
#   1. Skill Router API for domain context and relevant skill discovery
#   2. Local LLM (llama.cpp) for content generation following the format spec
#   3. Automated validation and git integration
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
LLM_SERVER_URL="http://localhost:8080"

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
GENERATED_SKILL=""

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

Generate new skills using the Skill Router API and local LLM.

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

infer_name() {
    local task_lower
    task_lower=$(echo "$TASK" | tr '[:upper:]' '[:lower:]')

    # Extract key terms and convert to kebab-case
    local name
    # Remove common filler words, keep meaningful technical terms
    name=$(echo "$task_lower" | sed -E 's/(generate|create|add|build|implement|write|make|about|for|the|a|an|with|using|of|and|in)//g' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

    # Replace spaces and special chars with hyphens, collapse multiple hyphens
    name=$(echo "$name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g; s/^-//; s/-$//')

    # Ensure it's not too short
    if [[ ${#name} -lt 3 ]]; then
        name="new-skill"
    fi

    echo "$name"
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
    # Use the Skill Router API to find relevant existing skills
    local skills_json=""

    if curl -sf "$API_URL/health" &>/dev/null; then
        # Route the task to find relevant skills
        log_info "Querying Skill Router API for relevant skills..."

        local route_response
        route_response=$(curl -sf -X POST "$API_URL/route" \
            -H "Content-Type: application/json" \
            -d "{
                \"task\": \"$TASK\",
                \"context\": {\"domain\": \"$DOMAIN\", \"type\": \"new\"},
                \"constraints\": {\"maxSkills\": 5}
            }")

        # Extract relevant skill names
        skills_json=$(echo "$route_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    skills = [s.get('name','') for s in data.get('selectedSkills', []) if s.get('name')]
    if not skills:
        # Try candidatePool as fallback
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

fetch_format_spec() {
    if [[ -f "$SKILL_FORMAT_SPEC" ]]; then
        cat "$SKILL_FORMAT_SPEC"
    else
        echo "SKILL_FORMAT_SPEC.md not found at $SKILL_FORMAT_SPEC"
    fi
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

    # Get relevant skills for context
    local relevant_skills=""
    if curl -sf "$API_URL/health" &>/dev/null; then
        relevant_skills=$(get_relevant_skills)
    fi

    # Build the LLM prompt
    local format_spec
    format_spec=$(fetch_format_spec)

    # Get content of relevant skills
    local skill_context=""
    if [[ -n "$relevant_skills" ]]; then
        IFS=',' read -ra skill_arr <<< "$relevant_skills"
        for s in "${skill_arr[@]}"; do
            if [[ -n "$s" ]]; then
                local content
                content=$(fetch_skill_content "$s")
                if [[ -n "$content" ]]; then
                    skill_context+="# Relevant skill: $s
$content
---

"
                fi
            fi
        done
    fi

    # Try using llama.cpp server if available
    if curl -sf "$LLM_SERVER_URL" &>/dev/null; then
        log_info "Using local LLM (llama.cpp at $LLM_SERVER_URL) for generation..."

        local llm_response
        # Build JSON payload safely with jq to avoid breaking on quotes/backslashes in $format_spec, $skill_context
        local system_msg="You are an expert skill writer for the OpenCode Agent Skill Router. Generate a complete, production-ready SKILL.md file following the format specification EXACTLY. Do NOT include any markdown code fences around the output — output the raw Markdown content directly. Every code block must contain substantive implementation code — NO pass statements, NO return {}, NO placeholder comments like 'example pattern for' or 'TODO'. All code must be complete, working examples with real logic. The skill must follow the SKILL_FORMAT_SPEC.md completely. Generate ONLY the SKILL.md content, nothing else."
        local user_msg="TASK: $TASK\n\nDOMAIN: $domain\nSKILL NAME: $skill_name\nTAGS: $tags\n\nFORMAT SPECIFICATION:\n${format_spec}\n\nRELEVANT SKILL CONTEXT:\n${skill_context}\n\nGenerate a complete SKILL.md for this skill. Follow the format specification exactly. Include all required sections, substantive code examples, proper YAML frontmatter, and domain-appropriate content. The skill must be immediately useful when loaded by an AI agent."

        llm_response=$(jq -n \
            --arg sys "$system_msg" \
            --arg usr "$user_msg" \
            '{
                model: "",
                messages: [
                    {role: "system", content: $sys},
                    {role: "user", content: $usr}
                ],
                max_tokens: 8192,
                temperature: 0.1
            }' | curl -sf "$LLM_SERVER_URL/v1/chat/completions" \
            -H "Content-Type: application/json" \
            -d @-)

        GENERATED_SKILL=$(echo "$llm_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
except json.JSONDecodeError as e:
    print(f'ERROR: Invalid JSON from LLM server: {e}', file=sys.stderr)
    sys.exit(1)
try:
    message = data['choices'][0]['message']
    content = message.get('content', '')
    # Fallback for reasoning models (e.g., Qwen3-Coder-Next) that put content in reasoning_content
    if not content:
        content = message.get('reasoning_content', '')
    if not content:
        print('ERROR: Empty response from model (both content and reasoning_content are empty)', file=sys.stderr)
        sys.exit(1)
    print(content, end='')
except (KeyError, IndexError) as e:
    print(f'ERROR: Unexpected LLM response structure: {e}', file=sys.stderr)
    print(f'Response keys: {list(data.keys())}', file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f'ERROR: Failed to extract content: {e}', file=sys.stderr)
    sys.exit(1)
")

        if [[ -n "$GENERATED_SKILL" ]]; then
            log_ok "LLM generated skill content"
        else
            log_warn "LLM generation failed, will try with expanded prompt..."
            GENERATED_SKILL=""
        fi
    else
        log_warn "llama.cpp server not available at $LLM_SERVER_URL"
        log_warn "Cannot generate skill content without an LLM"
        log_info "Run: ./llama.cpp/build/bin/llama-server -m <model-path>"
        log_info "Or provide a generated SKILL.md file directly"
        return 1
    fi

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

    # Infer name if not specified
    if [[ -z "$NAME" ]]; then
        NAME=$(infer_name)
        log_info "Inferred skill name: $NAME"
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

    # Commit and push
    commit_and_push "$DOMAIN" "$NAME"

    echo ""
    log_ok "Done! Skill created at: $SKILLS_DIR/$DOMAIN/$NAME/SKILL.md"
}

main "$@"
