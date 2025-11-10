#!/bin/bash

# Compilation script for Task 8: Vector Dot Products with OpenMP Sections
# Automatically detects OS and compiles with appropriate OpenMP flags

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Task 8: Vector Dot Products - Compilation ===${NC}"

# Detect OS
OS="$(uname -s)"
echo -e "${YELLOW}Detected OS: $OS${NC}"

# Determine project root (parent of scripts directory)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo -e "${YELLOW}Project root: $PROJECT_ROOT${NC}"

# Create bin directory if it doesn't exist
mkdir -p "$PROJECT_ROOT/bin"
mkdir -p "$PROJECT_ROOT/data"

# Source and output files
SRC_FILE="$PROJECT_ROOT/src/vector_dot_products.cpp"
OUT_FILE="$PROJECT_ROOT/bin/vector_dot_products"

# Compilation flags
CXXFLAGS="-std=c++17 -O3 -Wall"
OMPFLAG="-fopenmp"
CLANG_OMPFLAG="-Xpreprocessor -fopenmp"

# Detect compiler and compile based on OS
case "$OS" in
    Darwin*)
        echo -e "${YELLOW}macOS detected${NC}"
        
        # Try to find GCC with OpenMP support
        if command -v g++-13 &> /dev/null; then
            CXX="g++-13"
            echo -e "${GREEN}Using g++-13${NC}"
        elif command -v g++-12 &> /dev/null; then
            CXX="g++-12"
            echo -e "${GREEN}Using g++-12${NC}"
        elif command -v g++-11 &> /dev/null; then
            CXX="g++-11"
            echo -e "${GREEN}Using g++-11${NC}"
        elif brew list libomp &> /dev/null 2>&1; then
            # Use Clang with libomp
            CXX="clang++"
            LIBOMP_PREFIX=$(brew --prefix libomp)
            CXXFLAGS="$CXXFLAGS -I$LIBOMP_PREFIX/include"
            OMPFLAG="$CLANG_OMPFLAG"
            LDFLAGS="-L$LIBOMP_PREFIX/lib -lomp"
            echo -e "${GREEN}Using clang++ with libomp${NC}"
        else
            echo -e "${RED}Error: No suitable compiler found${NC}"
            echo -e "${YELLOW}Please install one of:${NC}"
            echo "  1. GCC with OpenMP: brew install gcc"
            echo "  2. libomp for Clang: brew install libomp"
            exit 1
        fi
        ;;
        
    Linux*)
        echo -e "${YELLOW}Linux detected${NC}"
        
        if command -v g++ &> /dev/null; then
            CXX="g++"
            echo -e "${GREEN}Using g++${NC}"
        else
            echo -e "${RED}Error: g++ not found${NC}"
            echo "Please install: sudo apt-get install g++"
            exit 1
        fi
        ;;
        
    *)
        echo -e "${RED}Unsupported OS: $OS${NC}"
        exit 1
        ;;
esac

# Compile
echo -e "${BLUE}Compiling...${NC}"
echo "Command: $CXX $CXXFLAGS $OMPFLAG $SRC_FILE -o $OUT_FILE $LDFLAGS"

if [ -z "$LDFLAGS" ]; then
    $CXX $CXXFLAGS $OMPFLAG "$SRC_FILE" -o "$OUT_FILE"
else
    $CXX $CXXFLAGS $OMPFLAG "$SRC_FILE" -o "$OUT_FILE" $LDFLAGS
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Compilation successful!${NC}"
    echo -e "${GREEN}Binary created: $OUT_FILE${NC}"
    
    # Generate test data
    echo -e "\n${BLUE}Generating test data...${NC}"
    "$OUT_FILE" generate 10 100 "$PROJECT_ROOT/data/test_vectors.txt"
    
    # Test correctness
    echo -e "\n${BLUE}Testing correctness...${NC}"
    if "$OUT_FILE" verify "$PROJECT_ROOT/data/test_vectors.txt"; then
        echo -e "${GREEN}✓ Correctness verification passed!${NC}"
    else
        echo -e "${RED}✗ Correctness verification failed${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Compilation failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}=== Compilation Complete ===${NC}"
echo -e "${YELLOW}You can now run the program:${NC}"
echo "  $OUT_FILE generate 100 1000 data/vectors.txt"
echo "  $OUT_FILE benchmark data/vectors.txt 4 sections 10"
echo "  $OUT_FILE verify data/vectors.txt"