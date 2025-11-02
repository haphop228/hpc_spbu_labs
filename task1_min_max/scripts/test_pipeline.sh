#!/bin/bash
# Quick test of the complete pipeline

echo "Testing complete pipeline with small dataset..."
echo ""

# Create test results
mkdir -p results
RESULTS_FILE="results/test_benchmark.json"

echo "Step 1: Running small benchmark..."
echo "[" > "$RESULTS_FILE"

# Small test: 100K elements, 1,2,4,8,16 threads, both methods, 3 runs
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

echo ""
echo "Step 2: Analyzing results..."
cd analysis
python3 analyze.py "$RESULTS_FILE"

echo ""
echo "Step 3: Generating graphs..."
python3 plot_graphs.py

echo ""
echo "✓ Pipeline test complete!"
echo "Check results/ and report/ directories"
