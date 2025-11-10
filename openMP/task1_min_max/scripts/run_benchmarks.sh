#!/bin/bash

mkdir -p ../results
RESULTS_FILE="../results/benchmark_$(date +%Y%m%d_%H%M%S).json"

# Configuration
SIZES=(1000000 10000000 100000000)
THREADS=(1 2 4 8 16 32 64 128)
METHODS=("reduction" "no-reduction")
RUNS=10

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