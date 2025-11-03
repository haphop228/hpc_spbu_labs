#!/bin/bash

echo -e "${BLUE}=== Dot Product Benchmark Suite ===${NC}"
echo ""

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# Check if binary exists
if [ ! -f "bin/dot_product" ]; then
    echo -e "${RED}✗ Binary not found!${NC}"
    echo -e "${YELLOW}Please compile first:${NC}"
    echo -e "  ${BLUE}./scripts/compile.sh${NC}"
    exit 1
fi

# Create results directory
mkdir -p results

# Generate timestamp for this benchmark run
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="results/benchmark_${TIMESTAMP}.csv"

echo -e "${GREEN}Results will be saved to: $OUTPUT_FILE${NC}"
echo ""

# Benchmark configuration
# Vector sizes: 10^6, 10^7, 10^8
SIZES=(1000000 10000000 100000000)
# Thread counts: 1, 2, 4, 8, 16, 32, 64, 128
THREADS=(1 2 4 8 16 32 64 128)
# Methods: reduction and no-reduction
METHODS=("reduction" "no-reduction")
# Number of iterations per configuration
RUNS=10

# Calculate total number of tests
TOTAL_TESTS=$((${#SIZES[@]} * ${#THREADS[@]} * ${#METHODS[@]}))
CURRENT_TEST=0

echo -e "${BLUE}Benchmark Configuration:${NC}"
echo "  Vector sizes: ${SIZES[@]}"
echo "  Thread counts: ${THREADS[@]}"
echo "  Methods: ${METHODS[@]}"
echo "  Iterations per config: $RUNS"
echo "  Total configurations: $TOTAL_TESTS"
echo ""

# Create CSV header
echo "vector_size,num_threads,method,iteration,execution_time_ms,result_value" > "$OUTPUT_FILE"

# Function to run a single benchmark
run_single_benchmark() {
    local size=$1
    local threads=$2
    local method=$3
    
    CURRENT_TEST=$((CURRENT_TEST + 1))
    
    echo -e "${YELLOW}[$CURRENT_TEST/$TOTAL_TESTS] Running: size=$size, threads=$threads, method=$method${NC}"
    
    # Run the benchmark
    ./bin/dot_product $size $threads $method $RUNS "$OUTPUT_FILE" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✓ Completed${NC}"
    else
        echo -e "${RED}  ✗ Failed${NC}"
        return 1
    fi
}

# Start time
START_TIME=$(date +%s)

echo -e "${BLUE}Starting benchmark runs...${NC}"
echo ""

# Run all benchmarks
for size in "${SIZES[@]}"; do
    echo -e "${BLUE}=== Vector Size: $size ===${NC}"
    
    for method in "${METHODS[@]}"; do
        echo -e "${YELLOW}Method: $method${NC}"
        
        for threads in "${THREADS[@]}"; do
            run_single_benchmark $size $threads $method
            
            # Small delay to prevent system overload
            sleep 0.5
        done
        
        echo ""
    done
    
    echo ""
done

# End time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo -e "${GREEN}=== Benchmark Complete ===${NC}"
echo ""
echo -e "${BLUE}Summary:${NC}"
echo "  Total tests run: $CURRENT_TEST"
echo "  Total duration: ${DURATION}s"
echo "  Results saved to: $OUTPUT_FILE"
echo ""

# Count lines in output file (excluding header)
RESULT_COUNT=$(($(wc -l < "$OUTPUT_FILE") - 1))
echo -e "${GREEN}✓ $RESULT_COUNT results recorded${NC}"

# Create a summary file
SUMMARY_FILE="results/benchmark_${TIMESTAMP}_summary.txt"
echo "Dot Product Benchmark Summary" > "$SUMMARY_FILE"
echo "=============================" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "Timestamp: $(date)" >> "$SUMMARY_FILE"
echo "Duration: ${DURATION}s" >> "$SUMMARY_FILE"
echo "Total configurations: $TOTAL_TESTS" >> "$SUMMARY_FILE"
echo "Results recorded: $RESULT_COUNT" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "Configuration:" >> "$SUMMARY_FILE"
echo "  Vector sizes: ${SIZES[@]}" >> "$SUMMARY_FILE"
echo "  Thread counts: ${THREADS[@]}" >> "$SUMMARY_FILE"
echo "  Methods: ${METHODS[@]}" >> "$SUMMARY_FILE"
echo "  Iterations per config: $RUNS" >> "$SUMMARY_FILE"
echo "" >> "$SUMMARY_FILE"
echo "Output file: $OUTPUT_FILE" >> "$SUMMARY_FILE"

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "  1. Analyze results: ${BLUE}python3 analysis/analyze.py $OUTPUT_FILE${NC}"
echo -e "  2. Generate graphs: ${BLUE}python3 analysis/plot_graphs.py${NC}"
echo ""