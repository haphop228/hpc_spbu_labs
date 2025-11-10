#!/bin/bash

# Benchmark runner for Task 7: Reduction with Different Synchronization Methods
# Tests different synchronization methods with various thread counts and array sizes

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Task 7: Reduction Synchronization - Benchmark Runner ===${NC}"

# Determine project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Binary location
BINARY="$PROJECT_ROOT/bin/reduction_sync"

# Check if binary exists
if [ ! -f "$BINARY" ]; then
    echo -e "${RED}Error: Binary not found at $BINARY${NC}"
    echo -e "${YELLOW}Please run compile.sh first${NC}"
    exit 1
fi

# Create results directory
mkdir -p "$PROJECT_ROOT/results"

# Generate timestamp for output file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="$PROJECT_ROOT/results/benchmark_${TIMESTAMP}.csv"

echo -e "${GREEN}Results will be saved to: $OUTPUT_FILE${NC}"

# Benchmark parameters (optimized for laptops with ~10 cores)
ARRAY_SIZES=(100000 1000000 10000000)     # Array sizes to test (smaller for speed)
THREADS=(1 2 4 8 16 32 64 128)                      # Number of threads to test (up to 16)
METHODS=("builtin" "atomic" "critical" "lock")  # Synchronization methods
RUNS=5                                     # Number of runs per configuration (reduced)

# First, run sequential baselines for each array size
echo -e "${BLUE}Running sequential baselines...${NC}"
for size in "${ARRAY_SIZES[@]}"; do
    echo -ne "${YELLOW}Sequential baseline for size $size${NC}"
    if "$BINARY" "$size" 1 sequential "$RUNS" "$OUTPUT_FILE" > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗ FAILED${NC}"
    fi
done
echo ""

# Calculate total number of tests
TOTAL_TESTS=$((${#ARRAY_SIZES[@]} * ${#THREADS[@]} * ${#METHODS[@]}))
CURRENT_TEST=0

echo -e "${YELLOW}Configuration:${NC}"
echo "  Array sizes: ${ARRAY_SIZES[@]}"
echo "  Threads: ${THREADS[@]}"
echo "  Methods: ${METHODS[@]}"
echo "  Runs per config: $RUNS"
echo "  Total tests: $TOTAL_TESTS"
echo ""

# Start time
START_TIME=$(date +%s)

# Run benchmarks
for size in "${ARRAY_SIZES[@]}"; do
    echo -e "${BLUE}Testing with array size $size${NC}"
    
    for threads in "${THREADS[@]}"; do
        for method in "${METHODS[@]}"; do
            CURRENT_TEST=$((CURRENT_TEST + 1))
            PROGRESS=$((CURRENT_TEST * 100 / TOTAL_TESTS))
            
            echo -ne "${YELLOW}[$CURRENT_TEST/$TOTAL_TESTS - ${PROGRESS}%] "
            echo -ne "size=$size, threads=$threads, method=$method${NC}"
            
            # Run benchmark
            if "$BINARY" "$size" "$threads" "$method" "$RUNS" "$OUTPUT_FILE" > /dev/null 2>&1; then
                echo -e " ${GREEN}✓${NC}"
            else
                echo -e " ${RED}✗ FAILED${NC}"
            fi
        done
    done
    echo ""
done

# End time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo -e "${GREEN}=== Benchmark Complete ===${NC}"
echo -e "${GREEN}Results saved to: $OUTPUT_FILE${NC}"
echo -e "${YELLOW}Total time: ${MINUTES}m ${SECONDS}s${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Analyze results:"
echo "     cd $PROJECT_ROOT/analysis"
echo "     python3 analyze.py $OUTPUT_FILE"
echo ""
echo "  2. Generate graphs:"
echo "     python3 plot_graphs.py"