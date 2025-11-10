#!/usr/bin/env bash

# Benchmark script for Task 3: Numerical Integration with OpenMP
# Tests different problem sizes, thread counts, and methods

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}=== Task 3: Numerical Integration - Benchmark Suite ===${NC}"

# Configuration
BINARY="../bin/integration"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="../results/benchmark_${TIMESTAMP}.csv"

# Test parameters
SIZES=(1000000 10000000 100000000)  # N values
THREADS=(1 2 4 8 16 32 64 128)      # Thread counts
METHODS=("reduction")
FUNCTIONS=("x2" "sin" "arctan")     # Test functions
RUNS=10                              # Iterations per configuration

# Integration bounds - using simple approach for compatibility
get_bound_a() {
    case "$1" in
        "x2") echo "0" ;;
        "sin") echo "0" ;;
        "arctan") echo "0" ;;
        *) echo "0" ;;
    esac
}

get_bound_b() {
    case "$1" in
        "x2") echo "1" ;;
        "sin") echo "3.14159265358979" ;;
        "arctan") echo "1" ;;
        *) echo "1" ;;
    esac
}

# Check if binary exists
if [ ! -f "$BINARY" ]; then
    echo -e "${YELLOW}Binary not found. Compiling...${NC}"
    ./compile.sh
fi

# Create output directory
mkdir -p ../results

# Initialize CSV file
echo "function,a,b,N,num_threads,method,iteration,execution_time_ms,result_value" > "$OUTPUT_FILE"

# Calculate total tests
TOTAL_TESTS=$((${#SIZES[@]} * ${#THREADS[@]} * ${#METHODS[@]} * ${#FUNCTIONS[@]}))
CURRENT_TEST=0

echo -e "\n${BLUE}Configuration:${NC}"
echo "  Problem sizes (N): ${SIZES[*]}"
echo "  Thread counts: ${THREADS[*]}"
echo "  Methods: ${METHODS[*]}"
echo "  Functions: ${FUNCTIONS[*]}"
echo "  Runs per config: $RUNS"
echo "  Total configurations: $TOTAL_TESTS"
echo "  Output file: $OUTPUT_FILE"

START_TIME=$(date +%s)

echo -e "\n${GREEN}Starting benchmarks...${NC}\n"

# Run benchmarks
for FUNC in "${FUNCTIONS[@]}"; do
    A=$(get_bound_a "$FUNC")
    B=$(get_bound_b "$FUNC")
    
    echo -e "${BLUE}Function: $FUNC, bounds: [$A, $B]${NC}"
    
    for SIZE in "${SIZES[@]}"; do
        echo -e "  ${YELLOW}Size N=$SIZE${NC}"
        
        for METHOD in "${METHODS[@]}"; do
            for THREADS_COUNT in "${THREADS[@]}"; do
                CURRENT_TEST=$((CURRENT_TEST + 1))
                PROGRESS=$((CURRENT_TEST * 100 / TOTAL_TESTS))
                
                printf "    [%3d%%] Method: %-13s Threads: %3d ... " "$PROGRESS" "$METHOD" "$THREADS_COUNT"
                
                # Run benchmark
                if $BINARY "$FUNC" "$A" "$B" "$SIZE" "$THREADS_COUNT" "$METHOD" "$RUNS" "$OUTPUT_FILE" > /dev/null 2>&1; then
                    echo -e "${GREEN}✓${NC}"
                else
                    echo -e "${RED}✗ FAILED${NC}"
                fi
            done
        done
        echo ""
    done
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