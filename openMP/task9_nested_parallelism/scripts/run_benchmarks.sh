#!/bin/bash

# Benchmark runner for Task 9: Nested Parallelism
# Tests both flat and nested parallelism approaches

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BIN_DIR="$PROJECT_DIR/bin"
RESULTS_DIR="$PROJECT_DIR/results"

echo "=== Task 9: Nested Parallelism - Benchmark Runner ==="

# Create results directory
mkdir -p "$RESULTS_DIR"

# Check if binary exists
if [ ! -f "$BIN_DIR/nested_parallelism" ]; then
    echo "Error: Binary not found. Please run compile.sh first."
    exit 1
fi

# Benchmark parameters
SIZES=(500 1000 2000)
THREAD_CONFIGS=(1 2 4 8 16 32 64 128)
RUNS=10

# Generate timestamp for results file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="$RESULTS_DIR/benchmark_${TIMESTAMP}.csv"

echo "Results will be saved to: $RESULTS_FILE"
echo ""
echo "Configuration:"
echo "  Matrix sizes: ${SIZES[*]}"
echo "  Thread configs: ${THREAD_CONFIGS[*]}"
echo "  Runs per config: $RUNS"
echo ""

# Initialize results file
echo "N,num_threads,outer_threads,inner_threads,method,iteration,execution_time_ms,result_value" > "$RESULTS_FILE"

total_tests=$((${#SIZES[@]} * (${#THREAD_CONFIGS[@]} * 2 + 1)))
current_test=0

# Run benchmarks
for SIZE in "${SIZES[@]}"; do
    echo "=========================================="
    echo "Matrix size: ${SIZE}x${SIZE}"
    echo "=========================================="
    
    # Sequential baseline
    echo ""
    echo "Running sequential baseline..."
    current_test=$((current_test + 1))
    echo "Progress: $current_test/$total_tests"
    
    "$BIN_DIR/nested_parallelism" $SIZE 1 sequential $RUNS "$RESULTS_FILE"
    
    # Flat parallelism (single-level)
    for THREADS in "${THREAD_CONFIGS[@]}"; do
        echo ""
        echo "Running flat parallelism with $THREADS threads..."
        current_test=$((current_test + 1))
        echo "Progress: $current_test/$total_tests"
        
        "$BIN_DIR/nested_parallelism" $SIZE $THREADS flat $RUNS "$RESULTS_FILE"
    done
    
    # Nested parallelism (two-level)
    for THREADS in "${THREAD_CONFIGS[@]}"; do
        # Calculate outer and inner thread distribution
        # Try to balance: sqrt(THREADS) for each level
        if [ $THREADS -eq 1 ]; then
            OUTER=1
            INNER=1
        elif [ $THREADS -eq 2 ]; then
            OUTER=2
            INNER=1
        elif [ $THREADS -eq 4 ]; then
            OUTER=2
            INNER=2
        elif [ $THREADS -eq 8 ]; then
            OUTER=4
            INNER=2
        elif [ $THREADS -eq 16 ]; then
            OUTER=4
            INNER=4
        elif [ $THREADS -eq 32 ]; then
            OUTER=8
            INNER=4
        elif [ $THREADS -eq 64 ]; then
            OUTER=8
            INNER=8
        elif [ $THREADS -eq 128 ]; then
            OUTER=16
            INNER=8
        fi
        
        echo ""
        echo "Running nested parallelism with ${OUTER}x${INNER}=$THREADS threads..."
        current_test=$((current_test + 1))
        echo "Progress: $current_test/$total_tests"
        
        "$BIN_DIR/nested_parallelism" $SIZE ${OUTER}:${INNER} nested $RUNS "$RESULTS_FILE"
    done
done

echo ""
echo "=========================================="
echo "Benchmark Complete!"
echo "=========================================="
echo "Results saved to: $RESULTS_FILE"
echo ""
echo "Next steps:"
echo "  1. cd $PROJECT_DIR/analysis"
echo "  2. python3 analyze.py $RESULTS_FILE"
echo "  3. python3 plot_graphs.py"
echo ""