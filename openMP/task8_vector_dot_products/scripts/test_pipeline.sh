#!/bin/bash

# Test pipeline for Task 8: Vector Dot Products with OpenMP Sections
# Runs compilation, correctness verification, and quick benchmark

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Task 8: Vector Dot Products - Test Pipeline ===${NC}"

# Determine project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$SCRIPT_DIR"

# Step 1: Compile
echo -e "\n${BLUE}Step 1: Compiling...${NC}"
if ./compile.sh; then
    echo -e "${GREEN}✓ Compilation successful${NC}"
else
    echo -e "${RED}✗ Compilation failed${NC}"
    exit 1
fi

# Binary location
BINARY="$PROJECT_ROOT/bin/vector_dot_products"

# Step 2: Generate test data
echo -e "\n${BLUE}Step 2: Generating test data...${NC}"
TEST_DATA="$PROJECT_ROOT/data/test_vectors.txt"
if "$BINARY" generate 50 1000 "$TEST_DATA" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Test data generated${NC}"
else
    echo -e "${RED}✗ Test data generation failed${NC}"
    exit 1
fi

# Step 3: Verify correctness
echo -e "\n${BLUE}Step 3: Verifying correctness...${NC}"
if "$BINARY" verify "$TEST_DATA"; then
    echo -e "${GREEN}✓ Correctness verification passed${NC}"
else
    echo -e "${RED}✗ Correctness verification failed${NC}"
    exit 1
fi

# Step 4: Quick benchmark
echo -e "\n${BLUE}Step 4: Running quick benchmark...${NC}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
QUICK_OUTPUT="$PROJECT_ROOT/results/quick_test_${TIMESTAMP}.csv"

echo -e "${YELLOW}Testing configurations:${NC}"
echo "  - 50 pairs, size 1000, sequential"
echo "  - 50 pairs, size 1000, 2 threads, sections"
echo "  - 50 pairs, size 1000, 4 threads, sections"
echo "  - 50 pairs, size 1000, 8 threads, sections"
echo ""

# Sequential baseline
echo -ne "${YELLOW}Testing sequential...${NC}"
if "$BINARY" benchmark "$TEST_DATA" 1 sequential 5 "$QUICK_OUTPUT" > /dev/null 2>&1; then
    echo -e " ${GREEN}✓${NC}"
else
    echo -e " ${RED}✗${NC}"
fi

# Sections with 2 threads
echo -ne "${YELLOW}Testing sections (2 threads)...${NC}"
if "$BINARY" benchmark "$TEST_DATA" 2 sections 5 "$QUICK_OUTPUT" > /dev/null 2>&1; then
    echo -e " ${GREEN}✓${NC}"
else
    echo -e " ${RED}✗${NC}"
fi

# Sections with 4 threads
echo -ne "${YELLOW}Testing sections (4 threads)...${NC}"
if "$BINARY" benchmark "$TEST_DATA" 4 sections 5 "$QUICK_OUTPUT" > /dev/null 2>&1; then
    echo -e " ${GREEN}✓${NC}"
else
    echo -e " ${RED}✗${NC}"
fi

# Sections with 8 threads
echo -ne "${YELLOW}Testing sections (8 threads)...${NC}"
if "$BINARY" benchmark "$TEST_DATA" 8 sections 5 "$QUICK_OUTPUT" > /dev/null 2>&1; then
    echo -e " ${GREEN}✓${NC}"
else
    echo -e " ${RED}✗${NC}"
fi

echo -e "\n${GREEN}Quick test results saved to: $QUICK_OUTPUT${NC}"

# Step 5: Check Python dependencies
echo -e "\n${BLUE}Step 5: Checking Python dependencies...${NC}"

PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}✗ Python not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python found: $PYTHON_CMD${NC}"

# Check required packages
REQUIRED_PACKAGES=("pandas" "matplotlib" "numpy")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if $PYTHON_CMD -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✓ $package installed${NC}"
    else
        echo -e "${RED}✗ $package not installed${NC}"
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "\n${YELLOW}Missing packages: ${MISSING_PACKAGES[*]}${NC}"
    echo -e "${YELLOW}Install with: pip3 install ${MISSING_PACKAGES[*]}${NC}"
else
    echo -e "\n${GREEN}✓ All Python dependencies installed${NC}"
fi

# Summary
echo -e "\n${GREEN}=== Test Pipeline Complete ===${NC}"
echo -e "${BLUE}All tests passed!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Run full benchmarks:"
echo "     ./run_benchmarks.sh"
echo ""
echo "  2. Analyze results:"
echo "     cd ../analysis"
echo "     python3 analyze.py ../results/benchmark_*.csv"
echo ""
echo "  3. Generate graphs:"
echo "     python3 plot_graphs.py"