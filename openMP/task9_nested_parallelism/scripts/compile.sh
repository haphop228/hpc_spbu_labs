#!/bin/bash

# Compilation script for Task 9: Nested Parallelism
# Automatically detects OS and compiler, compiles with OpenMP support

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$PROJECT_DIR/src"
BIN_DIR="$PROJECT_DIR/bin"

echo "=== Task 9: Nested Parallelism - Compilation ==="
echo "Project directory: $PROJECT_DIR"

# Create bin directory if it doesn't exist
mkdir -p "$BIN_DIR"

# Detect OS
OS="$(uname -s)"
echo "Operating System: $OS"

# Compiler selection
CXX=""
CXXFLAGS="-std=c++17 -O3 -fopenmp -Wall"
LDFLAGS="-fopenmp"

if [[ "$OS" == "Darwin" ]]; then
    echo "Detected macOS"
    
    # Try to find GCC with OpenMP support
    if command -v g++-13 &> /dev/null; then
        CXX="g++-13"
        echo "Using g++-13"
    elif command -v g++-12 &> /dev/null; then
        CXX="g++-12"
        echo "Using g++-12"
    elif command -v g++-11 &> /dev/null; then
        CXX="g++-11"
        echo "Using g++-11"
    else
        # Try Clang with libomp
        if command -v clang++ &> /dev/null; then
            CXX="clang++"
            echo "Using clang++ with libomp"
            
            # Check if libomp is installed
            if brew list libomp &> /dev/null; then
                LIBOMP_PREFIX=$(brew --prefix libomp)
                CXXFLAGS="-std=c++17 -O3 -Xclang -fopenmp -Wall -I$LIBOMP_PREFIX/include"
                LDFLAGS="-L$LIBOMP_PREFIX/lib -lomp"
            else
                echo "Warning: libomp not found. Installing..."
                brew install libomp
                LIBOMP_PREFIX=$(brew --prefix libomp)
                CXXFLAGS="-std=c++17 -O3 -Xclang -fopenmp -Wall -I$LIBOMP_PREFIX/include"
                LDFLAGS="-L$LIBOMP_PREFIX/lib -lomp"
            fi
        else
            echo "Error: No suitable compiler found!"
            echo "Please install GCC or libomp:"
            echo "  brew install gcc"
            echo "  or"
            echo "  brew install libomp"
            exit 1
        fi
    fi
elif [[ "$OS" == "Linux" ]]; then
    echo "Detected Linux"
    
    if command -v g++ &> /dev/null; then
        CXX="g++"
        echo "Using g++"
    else
        echo "Error: g++ not found!"
        echo "Please install: sudo apt-get install g++"
        exit 1
    fi
else
    echo "Error: Unsupported operating system: $OS"
    exit 1
fi

# Compile
echo ""
echo "Compiling nested_parallelism.cpp..."
echo "Compiler: $CXX"
echo "Flags: $CXXFLAGS"
echo "Linker flags: $LDFLAGS"
echo ""

$CXX $CXXFLAGS "$SRC_DIR/nested_parallelism.cpp" -o "$BIN_DIR/nested_parallelism" $LDFLAGS

if [ $? -eq 0 ]; then
    echo "✓ Compilation successful!"
    echo "Binary: $BIN_DIR/nested_parallelism"
    
    # Test OpenMP
    echo ""
    echo "Testing OpenMP support..."
    export OMP_NUM_THREADS=2
    
    # Create a simple test
    echo "Running quick verification..."
    if "$BIN_DIR/nested_parallelism" 100 2 flat 1 > /dev/null 2>&1; then
        echo "✓ OpenMP is working correctly!"
    else
        echo "✗ Warning: OpenMP test failed"
    fi
else
    echo "✗ Compilation failed!"
    exit 1
fi

echo ""
echo "=== Compilation Complete ==="