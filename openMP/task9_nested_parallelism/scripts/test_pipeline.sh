#!/bin/bash

# Full test pipeline for Task 9: Nested Parallelism
# Compiles, verifies correctness, and runs quick benchmark

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Task 9: Nested Parallelism - Test Pipeline ==="
echo ""

# Step 1: Compile
echo "Step 1: Compiling..."
echo "----------------------------------------"
bash "$SCRIPT_DIR/compile.sh"
echo ""

# Step 2: Check nested parallelism support
echo "Step 2: Checking nested parallelism support..."
echo "----------------------------------------"
"$PROJECT_DIR/bin/nested_parallelism" 100 2 flat 1 2>&1 | grep -A 20 "Checking Nested Parallelism Support"
echo ""

# Step 3: Verify correctness
echo "Step 3: Verifying correctness..."
echo "----------------------------------------"
"$PROJECT_DIR/bin/nested_parallelism" 100 2 flat 1 2>&1 | grep -A 15 "Correctness Verification"
echo ""

# Step 4: Quick benchmark
echo "Step 4: Running quick benchmark..."
echo "----------------------------------------"
echo "Testing flat parallelism (1000x1000, 4 threads)..."
"$PROJECT_DIR/bin/nested_parallelism" 1000 4 flat 3
echo ""

echo "Testing nested parallelism (1000x1000, 2x2=4 threads)..."
"$PROJECT_DIR/bin/nested_parallelism" 1000 2:2 nested 3
echo ""

# Step 5: Check Python dependencies
echo "Step 5: Checking Python dependencies..."
echo "----------------------------------------"
if command -v python3 &> /dev/null; then
    echo "✓ Python3 found: $(python3 --version)"
    
    # Check for required packages
    MISSING_PACKAGES=""
    
    if ! python3 -c "import pandas" 2>/dev/null; then
        MISSING_PACKAGES="$MISSING_PACKAGES pandas"
    fi
    
    if ! python3 -c "import matplotlib" 2>/dev/null; then
        MISSING_PACKAGES="$MISSING_PACKAGES matplotlib"
    fi
    
    if ! python3 -c "import numpy" 2>/dev/null; then
        MISSING_PACKAGES="$MISSING_PACKAGES numpy"
    fi
    
    if [ -n "$MISSING_PACKAGES" ]; then
        echo "✗ Missing Python packages:$MISSING_PACKAGES"
        echo "  Install with: pip3 install$MISSING_PACKAGES"
    else
        echo "✓ All required Python packages are installed"
    fi
else
    echo "✗ Python3 not found"
    echo "  Please install Python 3"
fi

echo ""
echo "=========================================="
echo "Test Pipeline Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Run full benchmarks: bash $SCRIPT_DIR/run_benchmarks.sh"
echo "  2. Analyze results: cd $PROJECT_DIR/analysis && python3 analyze.py ../results/benchmark_*.csv"
echo "  3. Generate graphs: python3 plot_graphs.py"
echo ""