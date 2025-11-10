#!/bin/bash

# Compilation script for Task 4: Matrix Game (Maximin) with OpenMP
# Supports macOS and Linux with automatic compiler detection

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Task 4: Matrix Game (Maximin) - Compilation Script ===${NC}"

# Detect OS
OS=$(uname -s)
echo "Detected OS: $OS"

# Create necessary directories
mkdir -p ../bin
mkdir -p ../results
mkdir -p ../graphs

# Compiler selection based on OS
if [[ "$OS" == "Darwin" ]]; then
    echo -e "${YELLOW}macOS detected${NC}"
    
    # Check for GCC (preferred for macOS)
    if command -v g++-13 &> /dev/null; then
        CXX="g++-13"
        echo "Using GCC 13"
    elif command -v g++-12 &> /dev/null; then
        CXX="g++-12"
        echo "Using GCC 12"
    elif command -v g++-11 &> /dev/null; then
        CXX="g++-11"
        echo "Using GCC 11"
    else
        # Try Clang with libomp
        if command -v clang++ &> /dev/null; then
            CXX="clang++"
            echo "Using Clang (will check for libomp)"
            
            # Check if libomp is installed
            if ! brew list libomp &> /dev/null; then
                echo -e "${YELLOW}libomp not found. Installing...${NC}"
                brew install libomp
            fi
            
            LIBOMP_PREFIX=$(brew --prefix libomp)
            EXTRA_FLAGS="-I${LIBOMP_PREFIX}/include -L${LIBOMP_PREFIX}/lib"
        else
            echo -e "${RED}Error: No suitable compiler found${NC}"
            echo "Please install GCC: brew install gcc"
            echo "Or install libomp for Clang: brew install libomp"
            exit 1
        fi
    fi
elif [[ "$OS" == "Linux" ]]; then
    echo -e "${YELLOW}Linux detected${NC}"
    
    if command -v g++ &> /dev/null; then
        CXX="g++"
        echo "Using system GCC"
    else
        echo -e "${RED}Error: g++ not found${NC}"
        echo "Please install: sudo apt-get install g++"
        exit 1
    fi
else
    echo -e "${RED}Unsupported OS: $OS${NC}"
    exit 1
fi

# Compilation flags
if [[ "$CXX" == "clang++" ]]; then
    # Clang needs -Xpreprocessor for OpenMP
    CXXFLAGS="-std=c++17 -O3 -Xpreprocessor -fopenmp -Wall -Wextra"
else
    CXXFLAGS="-std=c++17 -O3 -fopenmp -Wall -Wextra"
fi
SOURCE="../src/matrix_game.cpp"
OUTPUT="../bin/matrix_game"

echo -e "\n${GREEN}Compiling...${NC}"
echo "Compiler: $CXX"
echo "Flags: $CXXFLAGS $EXTRA_FLAGS"
echo "Source: $SOURCE"
echo "Output: $OUTPUT"

# Compile
if [[ "$CXX" == "clang++" ]]; then
    # Clang needs explicit -lomp linking
    if $CXX $CXXFLAGS $EXTRA_FLAGS $SOURCE -o $OUTPUT -lomp; then
        echo -e "${GREEN}✓ Compilation successful!${NC}"
    else
        echo -e "${RED}✗ Compilation failed!${NC}"
        exit 1
    fi
else
    if $CXX $CXXFLAGS $EXTRA_FLAGS $SOURCE -o $OUTPUT; then
        echo -e "${GREEN}✓ Compilation successful!${NC}"
    else
        echo -e "${RED}✗ Compilation failed!${NC}"
        exit 1
    fi
fi

# Test OpenMP
echo -e "\n${GREEN}Testing OpenMP support...${NC}"
$OUTPUT 100 4 reduction 1 > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ OpenMP is working correctly!${NC}"
else
    echo -e "${RED}✗ OpenMP test failed!${NC}"
    exit 1
fi

# Display binary info
echo -e "\n${GREEN}Binary information:${NC}"
ls -lh $OUTPUT
file $OUTPUT

echo -e "\n${GREEN}=== Compilation Complete ===${NC}"
echo "Binary location: $OUTPUT"
echo ""
echo "Quick test:"
echo "  $OUTPUT 1000 4 reduction 10"
echo ""
echo "Run full benchmarks:"
echo "  ./run_benchmarks.sh"