#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

if [ ! -f "bin/dot_product" ]; then
    exit 1
fi

mkdir -p results

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="results/benchmark_${TIMESTAMP}.csv"

SIZES=(1000000 10000000 100000000)
THREADS=(1 2 4 8 16 32 64 128)
METHODS=("reduction" "no-reduction")
RUNS=10

echo "vector_size,num_threads,method,iteration,execution_time_ms,result_value" > "$OUTPUT_FILE"

for size in "${SIZES[@]}"; do
    for method in "${METHODS[@]}"; do
        for threads in "${THREADS[@]}"; do
            ./bin/dot_product $size $threads $method $RUNS "$OUTPUT_FILE" > /dev/null 2>&1
            sleep 0.5
        done
    done
done
