#!/bin/bash

# Quick test pipeline for Task 3: Numerical Integration
# Performs compilation, correctness check, and quick benchmark

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}=== Task 3: Numerical Integration - Test Pipeline ===${NC}\n"

# Step 1: Compilation
echo -e "${BLUE}Step 1: Compilation${NC}"
./compile.sh
echo ""

# Step 2: Correctness verification
echo -e "${BLUE}Step 2: Correctness Verification${NC}"
echo "Running verification tests..."
../bin/integration x2 0 1 100000 4 reduction 1 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Correctness verification passed${NC}"
else
    echo -e "${RED}✗ Correctness verification failed${NC}"
    exit 1
fi
echo ""

# Step 3: Quick benchmark
echo -e "${BLUE}Step 3: Quick Benchmark${NC}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
QUICK_OUTPUT="../results/quick_test_${TIMESTAMP}.csv"

echo "Running quick benchmark (small scale)..."
echo "  Size: 1,000,000"
echo "  Threads: 1, 2, 4, 8"
echo "  Methods: reduction"
echo ""

# Initialize CSV
echo "function,a,b,N,num_threads,method,iteration,execution_time_ms,result_value" > "$QUICK_OUTPUT"

# Quick tests
SIZES=(1000000)
THREADS=(1 2 4 8)
METHODS=("reduction")
RUNS=3

for SIZE in "${SIZES[@]}"; do
    for METHOD in "${METHODS[@]}"; do
        for THREADS_COUNT in "${THREADS[@]}"; do
            printf "  Testing: N=%d, Method=%-13s, Threads=%d ... " "$SIZE" "$METHOD" "$THREADS_COUNT"
            
            if ../bin/integration x2 0 1 "$SIZE" "$THREADS_COUNT" "$METHOD" "$RUNS" "$QUICK_OUTPUT" > /dev/null 2>&1; then
                echo -e "${GREEN}✓${NC}"
            else
                echo -e "${RED}✗${NC}"
            fi
        done
    done
done

echo ""
echo -e "${GREEN}Quick benchmark complete!${NC}"
echo "Results saved to: $QUICK_OUTPUT"
echo ""

# Step 4: Check Python dependencies
echo -e "${BLUE}Step 4: Python Dependencies Check${NC}"
PYTHON_OK=true

if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓ Python 3 found${NC}"
    
    # Check for required packages
    for package in pandas matplotlib numpy; do
        if python3 -c "import $package" 2>/dev/null; then
            echo -e "${GREEN}✓ $package installed${NC}"
        else
            echo -e "${YELLOW}✗ $package not installed${NC}"
            PYTHON_OK=false
        fi
    done
else
    echo -e "${YELLOW}✗ Python 3 not found${NC}"
    PYTHON_OK=false
fi

echo ""

if [ "$PYTHON_OK" = true ]; then
    echo -e "${GREEN}All dependencies satisfied!${NC}"
    echo ""
    echo "You can now run analysis:"
    echo "  python3 ../analysis/analyze.py $QUICK_OUTPUT"
    echo "  python3 ../analysis/plot_graphs.py"
else
    echo -e "${YELLOW}Some Python dependencies missing.${NC}"
    echo "Install with: pip3 install pandas matplotlib numpy"
fi

echo ""
echo -e "${GREEN}=== Test Pipeline Complete ===${NC}"
echo ""
echo "Next steps:"
echo "  1. Run full benchmarks: ./run_benchmarks.sh"
echo "  2. Analyze results: python3 ../analysis/analyze.py <results_file>"
echo "  3. Generate graphs: python3 ../analysis/plot_graphs.py"