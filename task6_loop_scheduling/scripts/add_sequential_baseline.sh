#!/bin/bash

# Script to add sequential baseline runs to existing benchmark results

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Adding Sequential Baselines ===${NC}"

# Determine project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Binary location
BINARY="$PROJECT_ROOT/bin/loop_scheduling"

# Check if binary exists
if [ ! -f "$BINARY" ]; then
    echo -e "${RED}Error: Binary not found at $BINARY${NC}"
    echo -e "${YELLOW}Please run compile.sh first${NC}"
    exit 1
fi

# Check for results file argument
if [ $# -lt 1 ]; then
    echo -e "${RED}Error: No results file specified${NC}"
    echo "Usage: $0 <results_file.csv>"
    exit 1
fi

RESULTS_FILE="$1"

if [ ! -f "$RESULTS_FILE" ]; then
    echo -e "${RED}Error: Results file not found: $RESULTS_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}Results file: $RESULTS_FILE${NC}"

# Benchmark parameters
ITERATIONS=(1000 2000 5000 10000)
RUNS=10

echo -e "${YELLOW}Adding sequential baselines for iterations: ${ITERATIONS[@]}${NC}"
echo ""

# Run sequential baselines
for iterations in "${ITERATIONS[@]}"; do
    echo -ne "${YELLOW}Running sequential baseline for $iterations iterations...${NC}"
    
    if "$BINARY" "$iterations" 1 sequential 0 "$RUNS" "$RESULTS_FILE" > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗ FAILED${NC}"
    fi
done

echo ""
echo -e "${GREEN}=== Sequential baselines added ===${NC}"
echo -e "${YELLOW}You can now run the analysis:${NC}"
echo "  cd $PROJECT_ROOT/analysis"
echo "  python3 analyze.py $RESULTS_FILE"