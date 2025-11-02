#!/bin/bash

# Automated benchmark runner for OpenMP min/max program

echo "Starting OpenMP Min/Max Benchmarks"
echo "==================================="

# Create results directory
mkdir -p ../results
RESULTS_FILE="../results/benchmark_$(date +%Y%m%d_%H%M%S).json"

# Check if executable exists
if [ ! -f "../bin/min_max" ]; then
    echo "Error: Executable not found. Please run compile.sh first."
    exit 1
fi

# Configuration
SIZES=(1000000 10000000 100000000)  # 10^6, 10^7, 10^8
THREADS=(1 2 4 8 16 32)
METHODS=("reduction" "no-reduction")
RUNS=10

echo "Configuration:"
echo "  Vector sizes: ${SIZES[@]}"
echo "  Thread counts: ${THREADS[@]}"
echo "  Methods: ${METHODS[@]}"
echo "  Runs per config: $RUNS"
echo ""
echo "Results will be saved to: $RESULTS_FILE"
echo ""

# Start JSON array
echo "[" > "$RESULTS_FILE"

FIRST=1
TOTAL=$((${#SIZES[@]} * ${#THREADS[@]} * ${#METHODS[@]}))
CURRENT=0

# Run benchmarks
for size in "${SIZES[@]}"; do
    for threads in "${THREADS[@]}"; do
        for method in "${METHODS[@]}"; do
            CURRENT=$((CURRENT + 1))
            echo "[$CURRENT/$TOTAL] Running: size=$size, threads=$threads, method=$method"
            
            # Run the program and capture output
            OUTPUT=$(../bin/min_max $size $threads $method $RUNS)
            
            # Add comma separator if not first entry
            if [ $FIRST -eq 0 ]; then
                echo "," >> "$RESULTS_FILE"
            fi
            FIRST=0
            
            # Append results
            echo "$OUTPUT" >> "$RESULTS_FILE"
        done
    done
done

# Close JSON array
echo "" >> "$RESULTS_FILE"
echo "]" >> "$RESULTS_FILE"

echo ""
echo "✓ Benchmarks completed!"
echo "Results saved to: $RESULTS_FILE"
echo ""
echo "Next steps:"
echo "  1. Run: python3 ../analysis/analyze.py $RESULTS_FILE"
echo "  2. Run: python3 ../analysis/plot_graphs.py"