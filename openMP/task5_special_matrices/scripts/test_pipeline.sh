#!/usr/bin/env bash

# Test pipeline for Task 5: Special Matrices
# Performs compilation, correctness verification, and quick benchmark

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Task 5: Special Matrices - Test Pipeline ===${NC}"

# Step 1: Compilation
echo -e "\n${BLUE}Step 1: Compiling...${NC}"
./compile.sh

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Compilation failed!${NC}"
    exit 1
fi

# Step 2: Correctness verification
echo -e "\n${BLUE}Step 2: Verifying correctness...${NC}"
../bin/special_matrices 100 banded 5 4 static 0 1 > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Correctness verification passed!${NC}"
else
    echo -e "${RED}✗ Correctness verification failed!${NC}"
    exit 1
fi

# Step 3: Quick benchmark
echo -e "\n${BLUE}Step 3: Running quick benchmark...${NC}"

BINARY="../bin/special_matrices"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="../results/test_${TIMESTAMP}.csv"

mkdir -p ../results

echo "N,matrix_type,bandwidth,num_threads,schedule,chunk_size,iteration,execution_time_ms,result_value" > "$OUTPUT_FILE"

# Test configurations
SIZES=(500 1000)
MATRIX_TYPES=("banded" "lower")
THREADS=(1 4 8)
SCHEDULES=("static" "dynamic" "guided")

echo -e "\nRunning tests..."

for SIZE in "${SIZES[@]}"; do
    for MATRIX_TYPE in "${MATRIX_TYPES[@]}"; do
        for SCHEDULE in "${SCHEDULES[@]}"; do
            for THREADS_COUNT in "${THREADS[@]}"; do
                printf "  Testing: %dx%d %s, %d threads, %s ... " "$SIZE" "$SIZE" "$MATRIX_TYPE" "$THREADS_COUNT" "$SCHEDULE"
                
                if $BINARY "$SIZE" "$MATRIX_TYPE" 10 "$THREADS_COUNT" "$SCHEDULE" 0 3 "$OUTPUT_FILE" > /dev/null 2>&1; then
                    echo -e "${GREEN}✓${NC}"
                else
                    echo -e "${RED}✗${NC}"
                fi
            done
        done
    done
done

echo -e "\n${GREEN}Quick benchmark complete!${NC}"
echo "Results saved to: $OUTPUT_FILE"

# Step 4: Check Python dependencies
echo -e "\n${BLUE}Step 4: Checking Python dependencies...${NC}"

PYTHON_DEPS=("pandas" "matplotlib" "numpy")
MISSING_DEPS=()

for dep in "${PYTHON_DEPS[@]}"; do
    if python3 -c "import $dep" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $dep"
    else
        echo -e "  ${RED}✗${NC} $dep (missing)"
        MISSING_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo -e "\n${GREEN}All Python dependencies are installed!${NC}"
else
    echo -e "\n${YELLOW}Missing dependencies: ${MISSING_DEPS[*]}${NC}"
    echo "Install with: pip3 install ${MISSING_DEPS[*]}"
fi

# Summary
echo -e "\n${GREEN}=== Test Pipeline Complete ===${NC}"
echo ""
echo "Next steps:"
echo "  1. Run full benchmarks: ./run_benchmarks.sh"
echo "  2. Analyze results: python3 ../analysis/analyze.py $OUTPUT_FILE"
echo "  3. Generate graphs: python3 ../analysis/plot_graphs.py"