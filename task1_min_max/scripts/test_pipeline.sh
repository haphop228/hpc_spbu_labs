#!/bin/bash

mkdir -p results
RESULTS_FILE="results/test_benchmark.json"

echo "Step 1: Running small benchmark..."
echo "[" > "$RESULTS_FILE"

FIRST=1
for size in 100000; do
    for threads in 1 2 4 8 16; do
        for method in "reduction" "no-reduction"; do
            echo "  Testing: size=$size, threads=$threads, method=$method"
            OUTPUT=$(./bin/min_max $size $threads $method 3)
            
            if [ $FIRST -eq 0 ]; then
                echo "," >> "$RESULTS_FILE"
            fi
            FIRST=0
            
            echo "$OUTPUT" >> "$RESULTS_FILE"
        done
    done
done

echo "" >> "$RESULTS_FILE"
echo "]" >> "$RESULTS_FILE"

