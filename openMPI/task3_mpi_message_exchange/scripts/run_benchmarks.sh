#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== MPI Message Exchange Benchmark Suite ===${NC}"
echo ""

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# Check if binary exists
if [ ! -f "bin/message_exchange" ]; then
    echo -e "${RED}✗ Binary not found. Please compile first:${NC}"
    echo -e "  ${BLUE}./scripts/compile.sh${NC}"
    exit 1
fi

# Create results directory
mkdir -p results

# Generate timestamp for output file
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="results/benchmark_${TIMESTAMP}.csv"

echo -e "${YELLOW}Output file: $OUTPUT_FILE${NC}"
echo ""

# Message sizes to test (in bytes)
# From 1 byte to 16 MB, covering a wide range
MESSAGE_SIZES=(
    1                # 1 byte
    10               # 10 bytes
    100              # 100 bytes
    1024             # 1 KB
    10240            # 10 KB
    102400           # 100 KB
    1048576          # 1 MB
    2097152          # 2 MB
    4194304          # 4 MB
    8388608          # 8 MB
    16777216         # 16 MB
)

# Number of iterations for each message size
# More iterations for smaller messages (faster), fewer for larger (slower)
ITERATIONS=100

echo -e "${BLUE}Benchmark Configuration:${NC}"
echo "  Message sizes: ${#MESSAGE_SIZES[@]} different sizes"
echo "  Iterations per size: $ITERATIONS"
echo "  Total tests: ${#MESSAGE_SIZES[@]}"
echo ""

# Progress tracking
TOTAL_TESTS=${#MESSAGE_SIZES[@]}
CURRENT_TEST=0

# Run benchmarks
for size in "${MESSAGE_SIZES[@]}"; do
    CURRENT_TEST=$((CURRENT_TEST + 1))
    
    # Format size for display
    if [ $size -ge 1048576 ]; then
        SIZE_DISPLAY="$(echo "scale=2; $size / 1048576" | bc) MB"
    elif [ $size -ge 1024 ]; then
        SIZE_DISPLAY="$(echo "scale=2; $size / 1024" | bc) KB"
    else
        SIZE_DISPLAY="$size bytes"
    fi
    
    echo -e "${YELLOW}[$CURRENT_TEST/$TOTAL_TESTS] Testing message size: $SIZE_DISPLAY${NC}"
    
    # Run the benchmark
    mpirun -np 2 bin/message_exchange $size $ITERATIONS "$OUTPUT_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Test completed${NC}"
    else
        echo -e "${RED}✗ Test failed${NC}"
    fi
    echo ""
done

echo -e "${GREEN}=== Benchmark Complete ===${NC}"
echo ""
echo -e "${BLUE}Results saved to: $OUTPUT_FILE${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Analyze results:"
echo -e "     ${BLUE}python3 analysis/analyze.py $OUTPUT_FILE${NC}"
echo ""
echo "  2. Generate graphs:"
echo -e "     ${BLUE}python3 analysis/plot_graphs.py${NC}"
echo ""

# Create a summary
echo -e "${YELLOW}Creating summary...${NC}"
if command -v python3 &> /dev/null; then
    python3 - << EOF
import csv
import sys

try:
    with open('$OUTPUT_FILE', 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)
    
    if data:
        print("\n${BLUE}Quick Summary:${NC}")
        print(f"  Total measurements: {len(data)}")
        
        # Find fastest and slowest
        fastest = min(data, key=lambda x: float(x['avg_time_ms']))
        slowest = max(data, key=lambda x: float(x['avg_time_ms']))
        
        print(f"\n  Fastest (smallest message):")
        print(f"    Size: {fastest['message_size_bytes']} bytes")
        print(f"    Time: {float(fastest['avg_time_ms']):.6f} ms")
        print(f"    Bandwidth: {float(fastest['bandwidth_mbps']):.2f} MB/s")
        
        print(f"\n  Slowest (largest message):")
        print(f"    Size: {slowest['message_size_bytes']} bytes")
        print(f"    Time: {float(slowest['avg_time_ms']):.6f} ms")
        print(f"    Bandwidth: {float(slowest['bandwidth_mbps']):.2f} MB/s")
        
        # Find best bandwidth
        best_bw = max(data, key=lambda x: float(x['bandwidth_mbps']))
        print(f"\n  Best bandwidth:")
        print(f"    Size: {best_bw['message_size_bytes']} bytes")
        print(f"    Bandwidth: {float(best_bw['bandwidth_mbps']):.2f} MB/s")
except Exception as e:
    print(f"Could not create summary: {e}", file=sys.stderr)
EOF
fi

echo ""
echo -e "${GREEN}Done!${NC}"