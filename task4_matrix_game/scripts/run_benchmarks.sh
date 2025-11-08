#!/usr/bin/env bash

# Benchmark script for Task 4: Matrix Game (Maximin) with OpenMP
# Tests different matrix sizes, thread counts, and methods

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Task 4: Matrix Game (Maximin) - Benchmark Suite ===${NC}"

# Configuration
BINARY="../bin/matrix_game"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="../results/benchmark_${TIMESTAMP}.csv"

# Test parameters
SIZES=(100 500 1000 2000 3000)          # Matrix sizes (NxN)
THREADS=(1 2 4 8 16 32 64 128)           # Thread counts
METHODS=("reduction")                     # Methods to test
RUNS=10                                   # Iterations per configuration

# Check if binary exists
if [ ! -f "$BINARY" ]; then
    echo -e "${YELLOW}Binary not found. Compiling...${NC}"
    ./compile.sh
fi

# Create output directory
mkdir -p ../results

# Initialize CSV file
echo "N,num_threads,method,iteration,execution_time_ms,result_value" > "$OUTPUT_FILE"

# Calculate total tests
TOTAL_TESTS=$((${#SIZES[@]} * ${#THREADS[@]} * ${#METHODS[@]}))
CURRENT_TEST=0

echo -e "\n${BLUE}Configuration:${NC}"
echo "  Matrix sizes (N): ${SIZES[*]}"
echo "  Thread counts: ${THREADS[*]}"
echo "  Methods: ${METHODS[*]}"
echo "  Runs per config: $RUNS"
echo "  Total configurations: $TOTAL_TESTS"
echo "  Output file: $OUTPUT_FILE"

START_TIME=$(date +%s)

echo -e "\n${GREEN}Starting benchmarks...${NC}\n"

# Run benchmarks
for SIZE in "${SIZES[@]}"; do
    echo -e "${BLUE}Matrix Size: ${SIZE}x${SIZE}${NC}"
    
    for METHOD in "${METHODS[@]}"; do
        echo -e "  ${YELLOW}Method: $METHOD${NC}"
        
        for THREADS_COUNT in "${THREADS[@]}"; do
            CURRENT_TEST=$((CURRENT_TEST + 1))
            PROGRESS=$((CURRENT_TEST * 100 / TOTAL_TESTS))
            
            printf "    [%3d%%] Threads: %3d ... " "$PROGRESS" "$THREADS_COUNT"
            
            # Run benchmark
            if $BINARY "$SIZE" "$THREADS_COUNT" "$METHOD" "$RUNS" "$OUTPUT_FILE" > /dev/null 2>&1; then
                echo -e "${GREEN}✓${NC}"
            else
                echo -e "${RED}✗ FAILED${NC}"
            fi
        done
        echo ""
    done
    echo ""
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo -e "\n${GREEN}=== Benchmarks Complete ===${NC}"
echo "Duration: ${DURATION}s"
echo "Results saved to: $OUTPUT_FILE"
echo ""
echo "Next steps:"
echo "  1. Analyze results: python3 ../analysis/analyze.py $OUTPUT_FILE"
echo "  2. Generate graphs: python3 ../analysis/plot_graphs.py"