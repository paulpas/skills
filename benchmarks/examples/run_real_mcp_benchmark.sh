#!/bin/bash
# Example script for running Real MCP Benchmark

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Real MCP Benchmark - Actual HTTP Router Testing         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if router is running
echo -e "\n${YELLOW}Checking router health...${NC}"
if curl -s http://localhost:3000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Router is running${NC}"
else
    echo -e "${RED}❌ Router is not running at localhost:3000${NC}"
    echo -e "   Start it with: ${YELLOW}docker run -p 3000:3000 skill-router${NC}"
    exit 1
fi

# Get router stats
echo -e "\n${YELLOW}Fetching router statistics...${NC}"
STATS=$(curl -s http://localhost:3000/stats)
SKILL_COUNT=$(echo "$STATS" | python3 -c "import sys, json; print(json.load(sys.stdin).get('skills', {}).get('totalSkills', 0))")
echo -e "${GREEN}✅ Router has $SKILL_COUNT skills loaded${NC}"

# Run benchmark
echo -e "\n${YELLOW}Running Real MCP Benchmark...${NC}"
echo ""

cd "$SCRIPT_DIR"

# Determine tier (default: simple)
TIER="${1:-simple}"

python3 harness/benchmark.py \
    --tier "$TIER" \
    --use-real-mcp \
    --verbose \
    --output "results/real-mcp-$(date +%Y%m%d-%H%M%S).json"

echo ""
echo -e "${GREEN}✅ Real MCP Benchmark completed!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  • Check results in: ${YELLOW}benchmarks/results/${NC}"
echo "  • View latest: ${YELLOW}cat benchmarks/results/latest-results.json | python3 -m json.tool${NC}"
echo "  • Learn more: ${YELLOW}cat benchmarks/REAL_MCP_BENCHMARK.md${NC}"
