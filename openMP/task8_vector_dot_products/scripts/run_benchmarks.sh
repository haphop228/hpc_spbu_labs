#!/bin/bash

# Benchmark runner for Task 8: Vector Dot Products with OpenMP Sections
# Tests different thread counts and problem sizes

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Task 8: Vector Dot Products - Benchmark Runner ===${NC}"

# Determine project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Binary location
BINARY="$PROJECT_ROOT/bin/vector_dot_products"

# Check if binary exists
if [ ! -f "$BINARY" ]; then
    echo -e "${RED}Error: Binary not found at $BINARY${NC}"
    echo -e "${YELLOW}Please run compile.sh first${NC}"
    exit 1
fi

# Create results directory
mkdir -p "$PROJECT_ROOT/results"
mkdir -p "$PROJECT_ROOT/data"

# Generate timestamp for output file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="$PROJECT_ROOT/results/benchmark_${TIMESTAMP}.csv"

echo -e "${GREEN}Results will be saved to: $OUTPUT_FILE${NC}"

# Benchmark parameters
NUM_PAIRS=(50 100 200 500)           # Number of vector pairs
VECTOR_SIZES=(1000 5000 10000)       # Size of each vector
THREADS=(1 2 4 8 16 32 64 128)       # Number of threads to test
RUNS=10                               # Number of runs per configuration

echo -e "${YELLOW}Configuration:${NC}"
echo "  Vector pairs: ${NUM_PAIRS[@]}"
echo "  Vector sizes: ${VECTOR_SIZES[@]}"
echo "  Threads: ${THREADS[@]}"
echo "  Runs per config: $RUNS"
echo ""

# Generate test data files
echo -e "${BLUE}Generating test data files...${NC}"
for pairs in "${NUM_PAIRS[@]}"; do
    for size in "${VECTOR_SIZES[@]}"; do
        DATA_FILE="$PROJECT_ROOT/data/vectors_${pairs}x${size}.txt"
        if [ ! -f "$DATA_FILE" ]; then
            echo -ne "${YELLOW}Generating ${pairs} pairs of size ${size}...${NC}"
            if "$BINARY" generate "$pairs" "$size" "$DATA_FILE" > /dev/null 2>&1; then
                echo -e " ${GREEN}✓${NC}"
            else
                echo -e " ${RED}✗ FAILED${NC}"
                exit 1
            fi
        else
            echo -e "${GREEN}✓ Data file exists: ${pairs}x${size}${NC}"
        fi
    done
done
echo ""

# Calculate total number of tests
TOTAL_TESTS=$((${#NUM_PAIRS[@]} * ${#VECTOR_SIZES[@]} * (${#THREADS[@]} + 1)))
CURRENT_TEST=0

# Start time
START_TIME=$(date +%s)

# Run benchmarks
for pairs in "${NUM_PAIRS[@]}"; do
    for size in "${VECTOR_SIZES[@]}"; do
        DATA_FILE="$PROJECT_ROOT/data/vectors_${pairs}x${size}.txt"
        
        echo -e "${BLUE}Testing ${pairs} pairs of size ${size}${NC}"
        
        # Sequential baseline
        CURRENT_TEST=$((CURRENT_TEST + 1))
        PROGRESS=$((CURRENT_TEST * 100 / TOTAL_TESTS))
        echo -ne "${YELLOW}[$CURRENT_TEST/$TOTAL_TESTS - ${PROGRESS}%] "
        echo -ne "pairs=$pairs, size=$size, method=sequential${NC}"
        
        if "$BINARY" benchmark "$DATA_FILE" 1 sequential "$RUNS" "$OUTPUT_FILE" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
        else
            echo -e " ${RED}✗ FAILED${NC}"
        fi
        
        # Parallel with sections
        for threads in "${THREADS[@]}"; do
            CURRENT_TEST=$((CURRENT_TEST + 1))
            PROGRESS=$((CURRENT_TEST * 100 / TOTAL_TESTS))
            
            echo -ne "${YELLOW}[$CURRENT_TEST/$TOTAL_TESTS - ${PROGRESS}%] "
            echo -ne "pairs=$pairs, size=$size, threads=$threads, method=sections${NC}"
            
            if "$BINARY" benchmark "$DATA_FILE" "$threads" sections "$RUNS" "$OUTPUT_FILE" > /dev/null 2>&1; then
                echo -e " ${GREEN}✓${NC}"
            else
                echo -e " ${RED}✗ FAILED${NC}"
            fi
        done
        echo ""
    done
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