#!/bin/bash

# Test pipeline for Task 7: Reduction with Different Synchronization Methods
# Runs compilation, correctness verification, and quick benchmark

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Task 7: Reduction Synchronization - Test Pipeline ===${NC}"

# Determine project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Step 1: Compile
echo -e "\n${BLUE}Step 1: Compiling...${NC}"
if bash "$SCRIPT_DIR/compile.sh"; then
    echo -e "${GREEN}✓ Compilation successful${NC}"
else
    echo -e "${RED}✗ Compilation failed${NC}"
    exit 1
fi

# Binary location
BINARY="$PROJECT_ROOT/bin/reduction_sync"

# Step 2: Verify correctness
echo -e "\n${BLUE}Step 2: Verifying correctness...${NC}"
if "$BINARY" --verify; then
    echo -e "${GREEN}✓ Correctness verification passed${NC}"
else
    echo -e "${RED}✗ Correctness verification failed${NC}"
    exit 1
fi

# Step 3: Quick benchmark
echo -e "\n${BLUE}Step 3: Running quick benchmark...${NC}"
mkdir -p "$PROJECT_ROOT/results"
QUICK_OUTPUT="$PROJECT_ROOT/results/quick_test.csv"

# Test parameters
SIZE=1000000
THREADS=4
RUNS=5

echo -e "${YELLOW}Testing with array size $SIZE, $THREADS threads, $RUNS runs${NC}"

# Test each method
for method in sequential builtin atomic critical lock; do
    echo -ne "${YELLOW}Testing $method...${NC}"
    if "$BINARY" "$SIZE" "$THREADS" "$method" "$RUNS" "$QUICK_OUTPUT" > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗ FAILED${NC}"
    fi
done

echo -e "\n${GREEN}✓ Quick benchmark complete${NC}"
echo -e "${YELLOW}Results saved to: $QUICK_OUTPUT${NC}"

# Step 4: Check Python dependencies
echo -e "\n${BLUE}Step 4: Checking Python dependencies...${NC}"

check_python_package() {
    if python3 -c "import $1" 2>/dev/null; then
        echo -e "${GREEN}✓ $1 is installed${NC}"
        return 0
    else
        echo -e "${RED}✗ $1 is not installed${NC}"
        return 1
    fi
}

ALL_DEPS_OK=true
for package in pandas matplotlib numpy; do
    if ! check_python_package "$package"; then
        ALL_DEPS_OK=false
    fi
done

if [ "$ALL_DEPS_OK" = true ]; then
    echo -e "${GREEN}✓ All Python dependencies are installed${NC}"
else
    echo -e "${YELLOW}⚠ Some Python dependencies are missing${NC}"
    echo -e "${YELLOW}Install with: pip3 install pandas matplotlib numpy${NC}"
fi

# Summary
echo -e "\n${GREEN}=== Test Pipeline Complete ===${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Run full benchmark:"
echo "     cd $SCRIPT_DIR"
echo "     ./run_benchmarks.sh"
echo ""
echo "  2. Analyze results:"
echo "     cd $PROJECT_ROOT/analysis"
echo "     python3 analyze.py $QUICK_OUTPUT"
echo ""
echo "  3. Generate graphs:"
echo "     python3 plot_graphs.py"