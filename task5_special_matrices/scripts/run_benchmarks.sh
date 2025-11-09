#!/usr/bin/env bash

# Benchmark script for Task 5: Special Matrices with OpenMP Scheduling
# Tests different matrix types, thread counts, and scheduling strategies

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Task 5: Special Matrices - Benchmark Suite ===${NC}"

# Configuration
BINARY="../bin/special_matrices"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="../results/benchmark_${TIMESTAMP}.csv"

# Test parameters
SIZES=(500 1000 2000 3000)                    # Matrix sizes (NxN)
MATRIX_TYPES=("banded" "lower" "upper")       # Matrix types to test
BANDWIDTH=10                                   # Bandwidth for banded matrices
THREADS=(1 2 4 8 16 32 64 128)                # Thread counts
SCHEDULES=("static" "dynamic" "guided")        # Scheduling strategies
CHUNK_SIZES=(0 10 50)                          # Chunk sizes (0 = default)
RUNS=10                                        # Iterations per configuration

# Check if binary exists
if [ ! -f "$BINARY" ]; then
    echo -e "${YELLOW}Binary not found. Compiling...${NC}"
    ./compile.sh
fi

# Create output directory
mkdir -p ../results

# Initialize CSV file
echo "N,matrix_type,bandwidth,num_threads,schedule,chunk_size,iteration,execution_time_ms,result_value" > "$OUTPUT_FILE"

# Calculate total tests
TOTAL_TESTS=$((${#SIZES[@]} * ${#MATRIX_TYPES[@]} * ${#THREADS[@]} * ${#SCHEDULES[@]} * ${#CHUNK_SIZES[@]}))
CURRENT_TEST=0

echo -e "\n${BLUE}Configuration:${NC}"
echo "  Matrix sizes (N): ${SIZES[*]}"
echo "  Matrix types: ${MATRIX_TYPES[*]}"
echo "  Bandwidth (for banded): $BANDWIDTH"
echo "  Thread counts: ${THREADS[*]}"
echo "  Scheduling strategies: ${SCHEDULES[*]}"
echo "  Chunk sizes: ${CHUNK_SIZES[*]}"
echo "  Runs per config: $RUNS"
echo "  Total configurations: $TOTAL_TESTS"
echo "  Output file: $OUTPUT_FILE"

START_TIME=$(date +%s)

echo -e "\n${GREEN}Starting benchmarks...${NC}\n"

# Run benchmarks
for SIZE in "${SIZES[@]}"; do
    echo -e "${BLUE}Matrix Size: ${SIZE}x${SIZE}${NC}"
    
    for MATRIX_TYPE in "${MATRIX_TYPES[@]}"; do
        echo -e "  ${YELLOW}Matrix Type: $MATRIX_TYPE${NC}"
        
        for SCHEDULE in "${SCHEDULES[@]}"; do
            echo -e "    Schedule: $SCHEDULE"
            
            for CHUNK in "${CHUNK_SIZES[@]}"; do
                # Skip chunk size variations for static with default (0)
                if [[ "$SCHEDULE" == "static" && "$CHUNK" -ne 0 ]]; then
                    continue
                fi
                
                CHUNK_LABEL="default"
                if [[ "$CHUNK" -ne 0 ]]; then
                    CHUNK_LABEL="$CHUNK"
                fi
                
                for THREADS_COUNT in "${THREADS[@]}"; do
                    CURRENT_TEST=$((CURRENT_TEST + 1))
                    PROGRESS=$((CURRENT_TEST * 100 / TOTAL_TESTS))
                    
                    printf "      [%3d%%] Threads: %3d, Chunk: %-7s ... " "$PROGRESS" "$THREADS_COUNT" "$CHUNK_LABEL"
                    
                    # Run benchmark
                    if $BINARY "$SIZE" "$MATRIX_TYPE" "$BANDWIDTH" "$THREADS_COUNT" "$SCHEDULE" "$CHUNK" "$RUNS" "$OUTPUT_FILE" > /dev/null 2>&1; then
                        echo -e "${GREEN}✓${NC}"
                    else
                        echo -e "${RED}✗ FAILED${NC}"
                    fi
                done
            done
            echo ""
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