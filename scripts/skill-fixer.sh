#!/usr/bin/env bash
# =============================================================================
# skill-fixer.sh — Iteratively fix placeholder/poor code in SKILL.md files
# =============================================================================
#
# Uses llama-server with Qwen3 Coder to detect and fix placeholder code in
# OpenCode SKILL.md files (e.g., `pass` bodies, `return {}`, generic boilerplate).
#
# USAGE:
#   ./scripts/skill-fixer.sh [GLOB_PATTERN] [OPTIONS]
#
# ARGUMENTS:
#   GLOB_PATTERN   Glob pattern for SKILL.md files (default: skills/coding/ds-*/SKILL.md)
#
# OPTIONS:
#   --dry-run        Show what would be done without modifying files
#   --max-retries N  Maximum retry attempts per file (default: 2)
#   --validate-only  Only check for issues, do not fix
#   --help           Show this help message
#
# EXAMPLES:
#   ./scripts/skill-fixer.sh                          # Fix ds-* coding skills
#   ./scripts/skill-fixer.sh --dry-run                # Preview fixes
#   ./scripts/skill-fixer.sh "skills/agent/*/SKILL.md" --max-retries 3
#   ./scripts/skill-fixer.sh --validate-only           # Audit mode only
#
# DEPENDENCIES:
#   - llama-server (at /home/paulpas/llama.cpp/build/bin/llama-server)
#   - jq (for JSON parsing) or python3 as fallback
#   - curl
#   - bash 4.0+
#
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration (basic paths & defaults — before any validation)
# ---------------------------------------------------------------------------
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
readonly LOGS_DIR="$PROJECT_ROOT/logs"
# LOG_FILE is set by init_logging() at runtime
LOG_FILE=""
readonly LLAMA_SERVER_BIN="/home/paulpas/llama.cpp/build/bin/llama-server"

readonly DEFAULT_GLOB="skills/coding/ds-*/SKILL.md"
readonly DEFAULT_MAX_RETRIES=2

# ---------------------------------------------------------------------------
# Quick help check (before model validation so --help always works)
# ---------------------------------------------------------------------------
for _arg in "$@"; do
    if [[ "$_arg" == "--help" || "$_arg" == "-h" ]]; then
        echo "Usage: $0 [GLOB_PATTERN] [--dry-run] [--validate-only] [--max-retries N]"
        echo ""
        echo "Fix placeholder/poor code in SKILL.md files using llama-server with Qwen3 Coder."
        echo ""
        echo "Arguments:"
        echo "  GLOB_PATTERN   Glob pattern for SKILL.md files (default: $DEFAULT_GLOB)"
        echo ""
        echo "Options:"
        echo "  --dry-run        Show what would be done without modifying files"
        echo "  --validate-only  Only check for issues, do not fix"
        echo "  --max-retries N  Maximum retry attempts per file (default: $DEFAULT_MAX_RETRIES)"
        echo "  --help           Show this help message"
        exit 0
    fi
done

# ---------------------------------------------------------------------------
# Resolve model path — find the first GGUF shard file (llama-server auto-discovers the remaining shards)
# ---------------------------------------------------------------------------
find_model_directory() {
    # Search for the first part of a multi-part GGUF model
    local first_part
    first_part=$(find /home/paulpas/.cache/llama.cpp -name "*-00001-of-00004.gguf" 2>/dev/null | head -1)
    if [[ -z "$first_part" ]]; then
        # Fallback: look for 00002-of-00004 and use parent (unlikely but safe)
        first_part=$(find /home/paulpas/.cache/llama.cpp -name "*-00002-of-00004.gguf" 2>/dev/null | head -1)
    fi
    if [[ -n "$first_part" ]]; then
        echo "$first_part"
        return 0
    fi
    return 1
}

MODEL_DIR="$(find_model_directory)" || {
    echo "ERROR: Cannot find Qwen3-Coder-Next Q8_0 model files." >&2
    echo "Looked in: /home/paulpas/.cache/llama.cpp/" >&2
    echo "Expected: GGUF shard file matching *-00001-of-00004.gguf under /home/paulpas/.cache/llama.cpp/" >&2
    exit 1
}
readonly MODEL_DIR

readonly SERVER_HOST="127.0.0.1"
readonly SERVER_PORT="8080"
readonly SERVER_URL="http://${SERVER_HOST}:${SERVER_PORT}"
readonly HEALTH_URL="${SERVER_URL}/health"

# Temp directory for LLM interaction files
TMPDIR_SKILL_FIXER=""

cleanup_tmpdir() {
    if [[ -n "$TMPDIR_SKILL_FIXER" && -d "$TMPDIR_SKILL_FIXER" ]]; then
        rm -rf "$TMPDIR_SKILL_FIXER"
    fi
}
trap cleanup_tmpdir EXIT

setup_tmpdir() {
    TMPDIR_SKILL_FIXER="$(mktemp -d "${TMPDIR:-/tmp}/skill-fixer.XXXXXX")"
}

# ---------------------------------------------------------------------------
# JSON parser (jq preferred, python3 as fallback)
# ---------------------------------------------------------------------------
parse_json_value() {
    local json_str="$1"
    local query="$2"
    if command -v jq &>/dev/null; then
        echo "$json_str" | jq -r "$query" 2>/dev/null || echo ""
    else
        python3 -c "import json,sys; d=json.load(sys.stdin); print(json.dumps(d))" <<< "$json_str" || echo ""
    fi
}

extract_assistant_content() {
    local response="$1"
    local content
    content=$(parse_json_value "$response" '.choices[0].message.content // empty')
    if [[ -n "$content" && "$content" != "empty" ]]; then
        echo "$content"
        return 0
    fi
    # Fallback to reasoning_content for reasoning models
    local reasoning
    reasoning=$(parse_json_value "$response" '.choices[0].message.reasoning_content // empty')
    if [[ -n "$reasoning" && "$reasoning" != "empty" ]]; then
        echo "$reasoning"
        return 0
    fi
    echo "empty"
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
init_logging() {
    mkdir -p "$LOGS_DIR"
    LOG_FILE="$LOGS_DIR/skill-fixer-$(date +%Y%m%d).log"
}

log() {
    local level="$1"
    shift
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    local msg="[${timestamp}] [${level}] $*"
    echo "$msg" >> "$LOG_FILE"
    if [[ "$level" == "ERROR" || "$level" == "WARN" ]]; then
        echo "$msg" >&2
    fi
}

log_info()  { log "INFO"  "$@"; }
log_warn()  { log "WARN"  "$@"; }
log_error() { log "ERROR" "$@"; }

# ---------------------------------------------------------------------------
# Llama-server lifecycle management
# ---------------------------------------------------------------------------
LLAMA_PID=""

start_llama_server() {
    # Check if already running
    if [[ -n "$LLAMA_PID" ]] && kill -0 "$LLAMA_PID" 2>/dev/null; then
        log_info "Llama-server already running with PID $LLAMA_PID"
        return 0
    fi

    log_info "Starting llama-server with model from $MODEL_DIR"
    echo "Starting llama-server..."

    nohup "$LLAMA_SERVER_BIN" \
        --model "$MODEL_DIR" \
        --host "$SERVER_HOST" \
        --port "$SERVER_PORT" \
        --ctx-size 16384 \
        --n-predict 2048 \
        --temp 0.1 \
        --repeat-penalty 1.1 \
        --seed 42 \
        > "$LOGS_DIR/llama-server-$(date +%Y%m%d).log" 2>&1 &

    LLAMA_PID=$!
    log_info "llama-server started with PID $LLAMA_PID"

    # Wait for server to be ready
    local max_attempts=60
    local attempt=0
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -sf "${HEALTH_URL}" >/dev/null 2>&1; then
            log_info "Llama-server is ready after $(( attempt + 1 )) attempt(s)"
            return 0
        fi
        if ! kill -0 "$LLAMA_PID" 2>/dev/null; then
            log_error "Llama-server process died unexpectedly (PID $LLAMA_PID)"
            return 1
        fi
        attempt=$(( attempt + 1 ))
        sleep 2
    done

    log_error "Llama-server failed to become ready after ${max_attempts} attempts"
    return 1
}

stop_llama_server() {
    if [[ -n "$LLAMA_PID" ]] && kill -0 "$LLAMA_PID" 2>/dev/null; then
        log_info "Stopping llama-server (PID $LLAMA_PID)"
        kill "$LLAMA_PID" 2>/dev/null || true
        local wait_count=0
        while kill -0 "$LLAMA_PID" 2>/dev/null && [[ $wait_count -lt 10 ]]; do
            sleep 1
            wait_count=$(( wait_count + 1 ))
        done
        if kill -0 "$LLAMA_PID" 2>/dev/null; then
            kill -9 "$LLAMA_PID" 2>/dev/null || true
        fi
        log_info "Llama-server stopped"
        LLAMA_PID=""
    fi
}

cleanup() {
    local exit_code=$?
    stop_llama_server
    if [[ $exit_code -ne 0 ]]; then
        log_error "Script exited with code $exit_code"
    fi
    exit $exit_code
}

trap cleanup EXIT INT TERM

# ---------------------------------------------------------------------------
# Issue detection
# ---------------------------------------------------------------------------
declare -a ISSUES_FOUND=()

check_placeholder_patterns() {
    local file_content="$1"
    ISSUES_FOUND=()

    # Write content to temp file for Python to read
    local tmpfile="$TMPDIR_SKILL_FIXER/issues_check_$$"
    echo "$file_content" > "$tmpfile"

    # Use python3 for reliable multi-line pattern matching
    local issues
    issues=$(python3 - "$tmpfile" <<'PYEOF'
import re, sys

content_file = sys.argv[1]
with open(content_file, 'r') as f:
    content = f.read()

issues = []

# Pattern 1: pass as sole body in Python code blocks
if re.search(r'```python.*?pass\n.*?```', content, re.DOTALL):
    issues.append("Python code block contains `pass` as body")

# Pattern 2: return {} in Python blocks
if re.search(r'```python.*?return\s*\{\}\s*\n.*?```', content, re.DOTALL):
    issues.append("Python code block contains `return {}` placeholder")

# Pattern 3: # Example pattern for X comments
if re.search(r'# Example pattern for [A-Z]', content):
    issues.append("Python code block contains `# Example pattern for X` comments")

# Pattern 4: Empty method bodies (def with only pass)
if re.search(r'def\s+\w+\(.*?\):\s*\n\s+pass', content):
    issues.append("Empty method bodies found (def ... : pass)")

# Pattern 5: Generic select_skill boilerplate
if re.search(r'def\s+select_skill\s*\(', content):
    issues.append("Generic `select_skill` boilerplate detected")

# Pattern 6: Generic execute_with_fallback boilerplate
if re.search(r'def\s+execute_with_fallback\s*\(', content):
    issues.append("Generic `execute_with_fallback` boilerplate detected")

for issue in issues:
    print(issue)
PYEOF
    )

    rm -f "$tmpfile"

    while IFS= read -r issue; do
        [[ -n "$issue" ]] && ISSUES_FOUND+=("$issue")
    done <<< "$issues"

    return 0
}

check_structure_patterns() {
    local file_content="$1"

    # YAML frontmatter — check first 30 lines for --- fence and name field
    local first_30
    first_30=$(echo "$file_content" | head -30)
    if ! echo "$first_30" | grep -q '^---'; then
        ISSUES_FOUND+=("Missing YAML frontmatter --- fence")
    fi
    if ! echo "$first_30" | grep -q 'name:'; then
        ISSUES_FOUND+=("Missing YAML frontmatter name field")
    fi

    # H1 title — less strict: just check for any heading 1
    if ! echo "$file_content" | grep -q '^#\s'; then
        ISSUES_FOUND+=("Missing H1 title")
    fi
}

get_issue_summary() {
    if [[ ${#ISSUES_FOUND[@]} -eq 0 ]]; then
        echo "No placeholder or boilerplate issues detected."
    else
        echo "Issues found:"
        for issue in "${ISSUES_FOUND[@]}"; do
            echo "  - $issue"
        done
    fi
}

has_issues() {
    [[ ${#ISSUES_FOUND[@]} -gt 0 ]]
}

# ---------------------------------------------------------------------------
# Validation of fixed output
# ---------------------------------------------------------------------------
validate_output() {
    local original_file="$1"
    local fixed_file="$2"

    # Use python3 - with heredoc and arguments passed via sys.argv
    local errors
    errors=$(python3 - "$original_file" "$fixed_file" <<'PYEOF'
import re, sys

orig_file = sys.argv[1]
fixed_file = sys.argv[2]

try:
    with open(orig_file, 'r') as f:
        original = f.read()
except Exception:
    original = ""

try:
    with open(fixed_file, 'r') as f:
        fixed = f.read()
except Exception as e:
    print(f"Cannot read fixed file: {e}")
    sys.exit(1)

errors = []

# 1. No Python code blocks with `pass` as body
if re.search(r'```python.*?pass\s*\n.*?```', fixed, re.DOTALL):
    errors.append("Output still contains `pass` in Python code blocks")

# 2. No `return {}` in Python code blocks
if re.search(r'```python.*?return\s*\{\}\s*\n.*?```', fixed, re.DOTALL):
    errors.append("Output still contains `return {}` in Python code blocks")

# 3. YAML frontmatter still present (lenient: check first 30 lines for --- and name:)
lines_30 = fixed.split('\n')[:30]
first_30_text = '\n'.join(lines_30)
has_fenced = bool(re.search(r'^---\s*$', first_30_text, re.MULTILINE))
has_name = bool(re.search(r'name:', first_30_text))
if not (has_fenced and has_name):
    errors.append("YAML frontmatter is missing or malformed (missing --- fence or name field)")
else:
    fm = fixed.split('---', 2)
    if len(fm) < 3:
        errors.append("YAML frontmatter is malformed (unclosed ---)")
    else:
        fm_content = fm[1]
        if not re.search(r'^name:', fm_content, re.MULTILINE):
            errors.append("Frontmatter missing 'name' field")
        if not re.search(r'^description:', fm_content, re.MULTILINE):
            errors.append("Frontmatter missing 'description' field")

# 4. H1 title still present (less strict: just check for any heading 1)
if not re.search(r'^#\s+', fixed, re.MULTILINE):
    errors.append("H1 title is missing")

# 5. Code examples are substantive (at least 10 lines)
code_blocks = re.findall(r'```python(.*?)```', fixed, re.DOTALL)
short_blocks = [b for b in code_blocks if len(b.strip().split('\n')) < 10]
if short_blocks:
    errors.append(f"{len(short_blocks)} Python code block(s) are shorter than 10 lines")

# 6. Critical sections preserved (Core Workflow, Implementation Patterns — not all optional sections)
orig_sections = set(re.findall(r'^## .+', original, re.MULTILINE))
fix_sections = set(re.findall(r'^## .+', fixed, re.MULTILINE))

# Critical section patterns that must be present in every valid SKILL.md
critical_patterns = ['Core Workflow', 'Implementation Patterns']
missing_critical = []
for orig_sec in orig_sections:
    sec_lower = orig_sec.lower()
    is_critical = any(cp.lower() in sec_lower for cp in critical_patterns)
    if is_critical and orig_sec not in fix_sections:
        missing_critical.append(orig_sec)

# Also check: fixed must retain at least 70% of original section count
if len(fix_sections) < len(orig_sections) * 0.7:
    errors.append(f"Significant section loss: fixed has {len(fix_sections)} sections vs {len(orig_sections)} original")

if missing_critical:
    errors.append(f"Mandatory section(s) missing: {', '.join(missing_critical[:3])}")

for err in errors:
    print(err)
PYEOF
    )

    local err_count=0
    while IFS= read -r line; do
        [[ -n "$line" ]] && {
            echo "  - $line"
            err_count=$(( err_count + 1 ))
        }
    done <<< "$errors"

    if [[ $err_count -gt 0 ]]; then
        echo "Validation errors:" >&2
        echo "$errors" >&2
        return 1
    fi
    return 0
}

# ---------------------------------------------------------------------------
# LLM interaction
# ---------------------------------------------------------------------------
build_system_prompt() {
    local domain_context="$1"
    local validation_feedback="${2:-}"

    cat <<'BASE'
You are a skill file auditor and fixer for OpenCode SKILL.md files. Your job is to review the file and fix any placeholder, non-functional, or inappropriate code examples while PRESERVING the document structure.

**ABSOLUTE RULES — DO NOT VIOLATE:**
- DO NOT remove, reorder, or modify any existing ## section headings. Keep ALL ## section headings exactly as they are.
- DO NOT remove or rewrite prose text, bullet points, tables, or ASCII diagrams.
- If a code block already contains working code (even if incomplete), IMPROVE it rather than replacing it entirely.
- Your output must be a complete, valid SKILL.md file with all original sections preserved.
- Output ONLY the fixed markdown. No preamble, no thinking, no explanation. No markdown code fences around your output.
BASE

    case "$domain_context" in
        coding-ds)
            cat <<'RULES'

**Critical rules for data science (coding/ds-*) skills:**
- Replace ALL Python code blocks that are placeholders with REAL, WORKING implementations
- Use appropriate libraries: pandas, numpy, scikit-learn, matplotlib, scipy, statsmodels as applicable
- Code blocks must be substantive (at least 15 lines of actual implementation)
- Replace `pass` bodies with actual algorithm implementations
- Replace `return {}` with real result structures
- Replace `# Example pattern for X` comments with real code
- Each code block must be self-contained and runnable
- Include proper imports, error handling, and meaningful variable names
- Use real dataset examples (e.g., make_classification, make_regression, load_iris)
- For classification: show training, prediction, and metrics
- For regression: show fitting, prediction, and evaluation
- For clustering: show fit, labels, and inertia/evaluation
- For visualization: include actual plotting code with labels

**What to preserve:**
- YAML frontmatter (all fields)
- H1 title and all ## section headings
- All prose text, bullet points, tables
- Markdown structure and formatting
- References and related skills tables
RULES
            ;;
        agent)
            cat <<'RULES'

**Critical rules for agent skills:**
- Remove generic `select_skill` boilerplate — this is copy-paste template code that belongs in the skill-router, not individual skills
- Remove generic `execute_with_fallback` boilerplate — same reason
- Replace these with DOMAIN-SPECIFIC code examples that show how THIS particular skill works
- Each code example should demonstrate the actual domain logic, not generic orchestration
- For automation skills: show the specific automation (e.g., Slack API calls, Google Docs API usage)
- For analysis skills: show the specific analysis pipeline
- For development skills: show the actual development workflow code
- For infrastructure skills: show the specific infrastructure code (Terraform, Docker, etc.)
- Code must be substantive (at least 15 lines of actual domain-specific implementation)
- Preserve the orchestration concepts in prose, but put domain-specific code in examples

**What to preserve:**
- YAML frontmatter (all fields)
- H1 title and all ## section headings
- All prose text, bullet points, tables
- ASCII art diagrams (keep them intact)
- References and related skills tables
RULES
            ;;
        *)
            cat <<'RULES'

**Rules:**
- Replace placeholder Python code with actual working implementations
- Code blocks must be substantive (at least 15 lines)
- Replace `pass` with real logic
- Replace `return {}` with real results
- Preserve YAML frontmatter and document structure
RULES
            ;;
    esac

    if [[ -n "$validation_feedback" ]]; then
        cat <<FEEDBACK

**VALIDATION FEEDBACK (previous attempt failed):**
${validation_feedback}

IMPORTANT: You MUST fix the issues identified above. Do NOT produce the same placeholder code. Ensure:
- No \`pass\` in Python code block bodies
- No \`return {}\` placeholders
- Code blocks are at least 15 lines with real implementations
- YAML frontmatter is preserved
- DO NOT remove, reorder, or modify any existing ## section headings
- DO NOT remove or rewrite prose text, bullet points, or tables
- Output ONLY the fixed markdown. No preamble, no thinking, no explanation.
FEEDBACK
    fi
}

# ---------------------------------------------------------------------------
# LLM request builder and caller
# ---------------------------------------------------------------------------
call_llama_server() {
    local file_content_file="$1"
    local domain_context="$2"
    local validation_feedback="${3:-}"

    # Build system prompt to temp file
    local prompt_file="$TMPDIR_SKILL_FIXER/prompt.txt"
    build_system_prompt "$domain_context" "$validation_feedback" > "$prompt_file"

    # Build JSON request using a dedicated Python script (avoids shell escaping issues)
    local json_file="$TMPDIR_SKILL_FIXER/request.json"
    python3 - "$prompt_file" "$file_content_file" "$json_file" <<'PYEOF'
import json, sys

prompt_file = sys.argv[1]
content_file = sys.argv[2]
output_file = sys.argv[3]

with open(prompt_file, 'r') as f:
    system_prompt = f.read()

with open(content_file, 'r') as f:
    content = f.read()

request = {
    "model": "",
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content}
    ],
    "max_tokens": 8192,
    "temperature": 0.1,
    "top_p": 0.95,
    "stop": ["<|eot_id|>", "<|eom_id|>"],
    "stream": False
}

with open(output_file, 'w') as f:
    json.dump(request, f)
PYEOF

    # Call llama-server
    local response
    response=$(curl -sf \
        -X POST "${SERVER_URL}/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d "@$json_file" \
        2>&1) || {
        log_error "LLM API call failed"
        return 1
    }

    # Check for error in response
    local error_msg
    error_msg=$(parse_json_value "$response" '.error.message // empty')
    if [[ -n "$error_msg" ]]; then
        log_error "LLM API returned error: $error_msg"
        return 1
    fi

    local content
    content=$(extract_assistant_content "$response")
    echo "$content"
    return 0
}

# ---------------------------------------------------------------------------
# Domain detection
# ---------------------------------------------------------------------------
detect_domain() {
    local filepath="$1"
    if [[ "$filepath" == *"coding/ds-"* ]]; then
        echo "coding-ds"
    elif [[ "$filepath" == *"agent/"* ]]; then
        echo "agent"
    else
        echo "generic"
    fi
}

# ---------------------------------------------------------------------------
# Process a single file
# ---------------------------------------------------------------------------
process_file() {
    local filepath="$1"
    local dry_run="$2"
    local validate_only="$3"
    local max_retries="$4"

    local rel_path="${filepath#${PROJECT_ROOT}/}"

    log_info "Processing: $rel_path"

    # Read file content to temp file for LLM processing
    local content_file="$TMPDIR_SKILL_FIXER/content.md"
    cp "$filepath" "$content_file"

    # Check for issues
    local file_content
    file_content=$(cat "$filepath")
    check_placeholder_patterns "$file_content"
    check_structure_patterns "$file_content"
    local issue_summary
    issue_summary="$(get_issue_summary)"

    if ! has_issues; then
        if [[ "$validate_only" == "true" ]]; then
            echo "  [OK] No issues found."
        elif [[ "$dry_run" == "true" ]]; then
            echo "  [DRY-RUN] No changes needed: $rel_path"
        else
            echo "  [SKIPPED] No issues found."
        fi
        log_info "[$rel_path] Skipped - no issues found"
        return 0
    fi

    if [[ "$validate_only" == "true" ]]; then
        echo "  [ISSUES] Found issues:"
        echo "$issue_summary" | while IFS= read -r line; do
            echo "    $line"
        done
        log_info "[$rel_path] Validate-only: issues found"
        return 0
    fi

    if [[ "$dry_run" == "true" ]]; then
        echo "  [DRY-RUN] Would fix: $rel_path"
        echo "    Issues:"
        echo "$issue_summary" | while IFS= read -r line; do
            echo "    $line"
        done
        log_info "[$rel_path] Dry-run assessment"
        return 0
    fi

    # Fix mode: call LLM
    echo -n "  [FIXING] $rel_path..."
    log_info "[$rel_path] Beginning fix process"

    local domain_context
    domain_context="$(detect_domain "$filepath")"

    local fixed_file="$TMPDIR_SKILL_FIXER/fixed.md"
    local safety_backup="$TMPDIR_SKILL_FIXER/safety_backup.md"
    local attempt=0
    local last_validation_error=""

    # Create a safety backup before any modifications — the original file must survive
    cp -p "$filepath" "$safety_backup"

    while [[ $attempt -lt $max_retries ]]; do
        attempt=$(( attempt + 1 ))
        log_info "[$rel_path] LLM attempt $attempt of $max_retries (domain: $domain_context)"

        local llm_output
        llm_output="$(call_llama_server "$content_file" "$domain_context" "$last_validation_error")" || {
            last_validation_error="LLM API call failed on attempt $attempt"
            log_error "[$rel_path] LLM API call failed on attempt $attempt"
            if [[ $attempt -lt $max_retries ]]; then
                echo -n " retry..."
                sleep 2
                continue
            fi
            break
        }

        if [[ -z "$llm_output" ]]; then
            last_validation_error="LLM API returned empty response on attempt $attempt"
            log_error "[$rel_path] Empty LLM response on attempt $attempt"
            if [[ $attempt -lt $max_retries ]]; then
                echo -n " retry..."
                sleep 2
                continue
            fi
            break
        fi

        # Write fixed content to temp file for validation
        echo "$llm_output" > "$fixed_file"

        # Validate output
        local validation_errors_file="$TMPDIR_SKILL_FIXER/validation_errors.txt"
        if validate_output "$filepath" "$fixed_file" > "$validation_errors_file" 2>&1; then
            log_info "[$rel_path] Validation passed on attempt $attempt"
            echo " OK (attempt $attempt)"

            # Backup original, then atomically replace with fixed content
            cp -p "$filepath" "${filepath}.bak"
            cp "$fixed_file" "$filepath"
            log_info "[$rel_path] File fixed and saved (backup: ${filepath}.bak)"
            return 0
        else
            last_validation_error="$(cat "$validation_errors_file")"
            log_warn "[$rel_path] Validation failed on attempt $attempt: $last_validation_error"
            if [[ $attempt -lt $max_retries ]]; then
                echo -n " retry..."
                sleep 2
                continue
            fi
            break
        fi
    done

    # All attempts failed — verify and restore original from safety backup
    log_error "[$rel_path] Failed after $max_retries attempts"
    echo " FAILED"
    if [[ -n "$last_validation_error" ]]; then
        echo "    Last error: $(echo "$last_validation_error" | head -5)"
    fi

    # Rollback: ensure original file is intact by restoring from safety backup
    if ! diff -q "$safety_backup" "$filepath" &>/dev/null; then
        echo "  [RESTORE] Original file was modified, restoring from safety backup"
        cp -p "$safety_backup" "$filepath"
        log_warn "[$rel_path] Restored original file from safety backup"
    else
        echo "  [SAFE] Original file preserved (no changes made)"
    fi

    # Clean up stale backup if we didn't actually modify the file
    if [[ -f "${filepath}.bak" ]] && diff -q "$safety_backup" "$filepath" &>/dev/null; then
        rm -f "${filepath}.bak"
        log_info "[$rel_path] Removed stale .bak file (no changes were made)"
    fi

    return 1
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    local glob_pattern="$DEFAULT_GLOB"
    local dry_run="false"
    local validate_only="false"
    local max_retries="$DEFAULT_MAX_RETRIES"

    # Parse arguments — collect positional args for file paths
    local -a positional_args=()
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run)
                dry_run="true"
                shift
                ;;
            --validate-only)
                validate_only="true"
                shift
                ;;
            --max-retries)
                max_retries="${2:-2}"
                shift 2
                ;;
            --help)
                echo "Usage: $0 [GLOB_PATTERN | FILE ...] [--dry-run] [--validate-only] [--max-retries N]"
                echo ""
                echo "Fix placeholder/poor code in SKILL.md files using llama-server with Qwen3 Coder."
                echo ""
                echo "Arguments:"
                echo "  GLOB_PATTERN   Glob pattern for SKILL.md files (default: $DEFAULT_GLOB)"
                echo "  FILE ...       One or more specific SKILL.md file paths"
                echo ""
                echo "Options:"
                echo "  --dry-run        Show what would be done without modifying files"
                echo "  --validate-only  Only check for issues, do not fix"
                echo "  --max-retries N  Maximum retry attempts per file (default: $DEFAULT_MAX_RETRIES)"
                echo "  --help           Show this help message"
                exit 0
                ;;
            *)
                positional_args+=("$1")
                shift
                ;;
        esac
    done

    # Resolve positional arguments: single glob-like arg → glob; multiple args → file list
    if [[ ${#positional_args[@]} -eq 0 ]]; then
        glob_pattern="$DEFAULT_GLOB"
    elif [[ ${#positional_args[@]} -eq 1 ]]; then
        glob_pattern="${positional_args[0]}"
    else
        # Multiple file paths — store as space-separated for glob expansion
        # Each path will be resolved individually below
        glob_pattern=""
    fi

    init_logging
    setup_tmpdir
    log_info "=========================================="
    log_info "skill-fixer.sh starting"
    log_info "Glob pattern: $glob_pattern"
    log_info "Dry run: $dry_run"
    log_info "Validate only: $validate_only"
    log_info "Max retries: $max_retries"
    log_info "Model path: $MODEL_DIR"
    log_info "=========================================="

    # Resolve file paths
    local -a files=()

    if [[ -n "$glob_pattern" ]]; then
        # Single pattern — try glob expansion first, then treat as literal path
        local resolved_pattern
        if [[ "$glob_pattern" == /* ]]; then
            resolved_pattern="$glob_pattern"
        else
            resolved_pattern="${PROJECT_ROOT}/${glob_pattern}"
        fi
        shopt -s nullglob
        # shellcheck disable=SC2086
        files=( $resolved_pattern )
        shopt -u nullglob

        # If glob matched nothing, try treating as literal path (supports exact file paths)
        if [[ ${#files[@]} -eq 0 ]]; then
            if [[ -f "$resolved_pattern" ]]; then
                files=("$resolved_pattern")
            fi
        fi
    else
        # Multiple file paths — resolve each one
        for arg in "${positional_args[@]}"; do
            local resolved
            if [[ "$arg" == /* ]]; then
                resolved="$arg"
            else
                resolved="${PROJECT_ROOT}/${arg}"
            fi
            if [[ -f "$resolved" ]]; then
                files+=("$resolved")
            else
                echo "WARNING: File not found: $arg" >&2
            fi
        done
    fi

    if [[ ${#files[@]} -eq 0 ]]; then
        echo "ERROR: No files matched: ${positional_args[*]:-$DEFAULT_GLOB}"
        log_error "No files matched: ${positional_args[*]:-$DEFAULT_GLOB}"
        exit 1
    fi

    echo "Found ${#files[@]} file(s)"
    echo ""

    # Start llama-server (unless dry-run or validate-only)
    if [[ "$dry_run" == "true" || "$validate_only" == "true" ]]; then
        echo "Running in $(if [[ "$dry_run" == "true" ]]; then echo "dry-run"; else echo "validate-only"; fi) mode — no LLM calls"
        echo ""
    else
        start_llama_server || {
            echo "ERROR: Failed to start llama-server" >&2
            log_error "Failed to start llama-server"
            exit 1
        }
        echo "Llama-server is ready."
        echo ""
    fi

    # Process each file
    local total=0
    local fixed=0
    local failed=0
    local skipped=0

    for filepath in "${files[@]}"; do
        total=$(( total + 1 ))
        echo "File ${total}/${#files[@]}: $filepath"

        if process_file "$filepath" "$dry_run" "$validate_only" "$max_retries"; then
            if [[ "$dry_run" == "true" || "$validate_only" == "true" ]]; then
                skipped=$(( skipped + 1 ))
            else
                # In fix mode, check if issues are gone
                local post_content
                post_content=$(cat "$filepath")
                ISSUES_FOUND=()
                check_placeholder_patterns "$post_content"
                check_structure_patterns "$post_content"
                if has_issues; then
                    failed=$(( failed + 1 ))
                else
                    fixed=$(( fixed + 1 ))
                fi
            fi
        else
            failed=$(( failed + 1 ))
        fi

        echo ""
    done

    # Summary
    echo "============================================"
    echo "           SKILL FIXER SUMMARY"
    echo "============================================"
    echo "  Total files:  $total"
    echo "  Fixed:        $fixed"
    echo "  Failed:       $failed"
    echo "  Skipped:      $skipped"
    echo "============================================"

    log_info "Summary: total=$total fixed=$fixed failed=$failed skipped=$skipped"
    log_info "skill-fixer.sh completed"

    if [[ $failed -gt 0 ]]; then
        return 1
    fi
    return 0
}

main "$@"
