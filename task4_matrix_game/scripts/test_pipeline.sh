#!/usr/bin/env bash

# Test pipeline for Task 4: Matrix Game (Maximin)
# Runs compilation, correctness tests, and quick benchmark

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Task 4: Matrix Game (Maximin) - Test Pipeline ===${NC}\n"

# Step 1: Compilation
echo -e "${BLUE}Step 1: Compiling...${NC}"
./compile.sh
echo ""

# Step 2: Correctness verification
echo -e "${BLUE}Step 2: Running correctness tests...${NC}"
../bin/matrix_game 100 4 reduction 1
echo ""

# Step 3: Quick benchmark
echo -e "${BLUE}Step 3: Running quick benchmark...${NC}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
QUICK_OUTPUT="../results/quick_test_${TIMESTAMP}.csv"

echo "N,num_threads,method,iteration,execution_time_ms,result_value" > "$QUICK_OUTPUT"

SIZES=(100 500 1000)
THREADS=(1 2 4 8)
METHODS=("reduction")
RUNS=3

echo "Testing configurations:"
echo "  Sizes: ${SIZES[*]}"
echo "  Threads: ${THREADS[*]}"
echo "  Methods: ${METHODS[*]}"
echo "  Runs: $RUNS"
echo ""

for SIZE in "${SIZES[@]}"; do
    for METHOD in "${METHODS[@]}"; do
        for THREADS_COUNT in "${THREADS[@]}"; do
            printf "  N=%4d, Method=%-10s, Threads=%2d ... " "$SIZE" "$METHOD" "$THREADS_COUNT"
            if ../bin/matrix_game "$SIZE" "$THREADS_COUNT" "$METHOD" "$RUNS" "$QUICK_OUTPUT" > /dev/null 2>&1; then
                echo -e "${GREEN}✓${NC}"
            else
                echo -e "${RED}✗${NC}"
            fi
        done
    done
done

echo ""
echo -e "${GREEN}Quick benchmark results saved to: $QUICK_OUTPUT${NC}"

# Step 4: Check Python dependencies
echo -e "\n${BLUE}Step 4: Checking Python dependencies...${NC}"
if command -v python3 &> /dev/null; then
    echo "✓ Python3 found"
    
    # Check for required packages
    MISSING_PACKAGES=()
    
    if ! python3 -c "import pandas" 2>/dev/null; then
        MISSING_PACKAGES+=("pandas")
    fi
    
    if ! python3 -c "import matplotlib" 2>/dev/null; then
        MISSING_PACKAGES+=("matplotlib")
    fi
    
    if ! python3 -c "import numpy" 2>/dev/null; then
        MISSING_PACKAGES+=("numpy")
    fi
    
    if [ ${#MISSING_PACKAGES[@]} -eq 0 ]; then
        echo "✓ All required Python packages are installed"
    else
        echo -e "${YELLOW}⚠ Missing packages: ${MISSING_PACKAGES[*]}${NC}"
        echo "Install with: pip3 install ${MISSING_PACKAGES[*]}"
    fi
else
    echo -e "${RED}✗ Python3 not found${NC}"
fi

echo -e "\n${GREEN}=== Test Pipeline Complete ===${NC}"
echo ""
echo "Next steps:"
echo "  1. Run full benchmarks: ./run_benchmarks.sh"
echo "  2. Analyze results: python3 ../analysis/analyze.py $QUICK_OUTPUT"
echo "  3. Generate graphs: python3 ../analysis/plot_graphs.py"