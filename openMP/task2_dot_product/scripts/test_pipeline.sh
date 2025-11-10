#!/bin/bash

echo -e "${BLUE}=== Dot Product Pipeline Test ===${NC}"
echo ""

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# Step 1: Compile
echo -e "${YELLOW}Step 1: Compiling...${NC}"
./scripts/compile.sh
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Compilation failed!${NC}"
    exit 1
fi
echo ""

# Step 2: Quick functionality test
echo -e "${YELLOW}Step 2: Running quick functionality test...${NC}"
./bin/dot_product 100000 4 reduction 3
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Functionality test failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Functionality test passed${NC}"
echo ""

# Step 3: Quick benchmark
echo -e "${YELLOW}Step 3: Running quick benchmark...${NC}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="results/test_${TIMESTAMP}.csv"

mkdir -p results

# Quick test with smaller configuration
SIZES=(1000000 10000000)
THREADS=(1 2 4 8)
METHODS=("reduction" "no-reduction")
RUNS=5

echo "vector_size,num_threads,method,iteration,execution_time_ms,result_value" > "$OUTPUT_FILE"

TOTAL_TESTS=$((${#SIZES[@]} * ${#THREADS[@]} * ${#METHODS[@]}))
CURRENT_TEST=0

for size in "${SIZES[@]}"; do
    for method in "${METHODS[@]}"; do
        for threads in "${THREADS[@]}"; do
            CURRENT_TEST=$((CURRENT_TEST + 1))
            echo -e "  [$CURRENT_TEST/$TOTAL_TESTS] Testing: size=$size, threads=$threads, method=$method"
            ./bin/dot_product $size $threads $method $RUNS "$OUTPUT_FILE" > /dev/null 2>&1
            if [ $? -ne 0 ]; then
                echo -e "${RED}  ✗ Test failed${NC}"
                exit 1
            fi
        done
    done
done

echo -e "${GREEN}✓ Quick benchmark completed${NC}"
echo -e "${GREEN}✓ Results saved to: $OUTPUT_FILE${NC}"
echo ""

# Step 4: Check if Python is available for analysis
if command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Step 4: Checking Python dependencies...${NC}"
    
    # Check if required packages are installed
    python3 -c "import pandas, matplotlib, numpy" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Python dependencies available${NC}"
        echo ""
        echo -e "${YELLOW}You can now run analysis:${NC}"
        echo -e "  ${BLUE}python3 analysis/analyze.py $OUTPUT_FILE${NC}"
        echo -e "  ${BLUE}python3 analysis/plot_graphs.py${NC}"
    else
        echo -e "${YELLOW}⚠ Some Python packages are missing${NC}"
        echo -e "${YELLOW}Install with:${NC}"
        echo -e "  ${BLUE}pip3 install pandas matplotlib numpy seaborn${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Python3 not found - skipping analysis check${NC}"
fi

echo ""
echo -e "${GREEN}=== Pipeline Test Complete ===${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "  ✓ Compilation successful"
echo "  ✓ Functionality test passed"
echo "  ✓ Quick benchmark completed"
echo "  ✓ Results saved to: $OUTPUT_FILE"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Run full benchmark: ${BLUE}./scripts/run_benchmarks.sh${NC}"
echo -e "  2. Analyze results: ${BLUE}python3 analysis/analyze.py results/benchmark_*.csv${NC}"
echo -e "  3. Generate graphs: ${BLUE}python3 analysis/plot_graphs.py${NC}"
echo ""