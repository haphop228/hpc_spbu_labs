#!/bin/bash

# Benchmark runner for Task 6: Loop Scheduling Investigation
# Tests different scheduling strategies with various thread counts and chunk sizes

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Task 6: Loop Scheduling - Benchmark Runner ===${NC}"

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

# Create results directory
mkdir -p "$PROJECT_ROOT/results"

# Generate timestamp for output file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="$PROJECT_ROOT/results/benchmark_${TIMESTAMP}.csv"

echo -e "${GREEN}Results will be saved to: $OUTPUT_FILE${NC}"

# Benchmark parameters
ITERATIONS=(1000 2000 5000 10000)  # Number of loop iterations
THREADS=(1 2 4 8 16 32 64 128)     # Number of threads to test
SCHEDULES=("static" "dynamic" "guided")  # Scheduling strategies
CHUNK_SIZES=(0 1 5 10 50)         # Chunk sizes (0 = default)
RUNS=10                            # Number of runs per configuration

# First, run sequential baselines for each iteration count
echo -e "${BLUE}Running sequential baselines...${NC}"
for iterations in "${ITERATIONS[@]}"; do
    echo -ne "${YELLOW}Sequential baseline for $iterations iterations${NC}"
    if "$BINARY" "$iterations" 1 sequential 0 "$RUNS" "$OUTPUT_FILE" > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${RED}✗ FAILED${NC}"
    fi
done
echo ""

# Calculate total number of tests
TOTAL_TESTS=$((${#ITERATIONS[@]} * ${#THREADS[@]} * ${#SCHEDULES[@]} * ${#CHUNK_SIZES[@]}))
CURRENT_TEST=0

echo -e "${YELLOW}Configuration:${NC}"
echo "  Iterations: ${ITERATIONS[@]}"
echo "  Threads: ${THREADS[@]}"
echo "  Schedules: ${SCHEDULES[@]}"
echo "  Chunk sizes: ${CHUNK_SIZES[@]}"
echo "  Runs per config: $RUNS"
echo "  Total tests: $TOTAL_TESTS"
echo ""

# Start time
START_TIME=$(date +%s)

# Run benchmarks
for iterations in "${ITERATIONS[@]}"; do
    echo -e "${BLUE}Testing with $iterations iterations${NC}"
    
    for threads in "${THREADS[@]}"; do
        for schedule in "${SCHEDULES[@]}"; do
            for chunk in "${CHUNK_SIZES[@]}"; do
                CURRENT_TEST=$((CURRENT_TEST + 1))
                PROGRESS=$((CURRENT_TEST * 100 / TOTAL_TESTS))
                
                echo -ne "${YELLOW}[$CURRENT_TEST/$TOTAL_TESTS - ${PROGRESS}%] "
                echo -ne "iterations=$iterations, threads=$threads, schedule=$schedule, chunk=$chunk${NC}"
                
                # Run benchmark
                if "$BINARY" "$iterations" "$threads" "$schedule" "$chunk" "$RUNS" "$OUTPUT_FILE" > /dev/null 2>&1; then
                    echo -e " ${GREEN}✓${NC}"
                else
                    echo -e " ${RED}✗ FAILED${NC}"
                fi
            done
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