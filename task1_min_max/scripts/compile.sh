#!/bin/bash

mkdir -p ../bin

# Detect OS and set compiler flags
if [[ "$OSTYPE" == "darwin"* ]]; then    
    # Check if libomp is installed
    if ! brew list libomp &>/dev/null; then
        echo "Installing libomp via Homebrew..."
        brew install libomp
    fi
    
    # Get libomp paths
    LIBOMP_PREFIX=$(brew --prefix libomp)
    
    clang -Xpreprocessor -fopenmp -O3 -Wall \
          -I"$LIBOMP_PREFIX/include" \
          -L"$LIBOMP_PREFIX/lib" \
          -lomp \
          -o ../bin/min_max ../src/min_max.c -lm
else
    # Linux or other Unix
    gcc -fopenmp -O3 -Wall -o ../bin/min_max ../src/min_max.c -lm
fi

if [ $? -eq 0 ]; then
    ../bin/min_max 1000 2 reduction 1 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ OpenMP is working correctly!"
    else
        echo "⚠ Warning: Program compiled but OpenMP may not be working"
    fi
else
    echo "✗ Compilation failed!"
    exit 1
fi