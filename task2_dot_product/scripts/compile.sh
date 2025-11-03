#!/bin/bash


echo -e "${BLUE}=== Compiling Dot Product Program ===${NC}"
echo ""

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

# Create bin directory if it doesn't exist
mkdir -p bin

# Detect OS
OS="$(uname -s)"
echo -e "${YELLOW}Detected OS: $OS${NC}"

# Function to check if OpenMP is working
check_openmp() {
    local compiler=$1
    local flags=$2
    echo -e "${YELLOW}Checking OpenMP support...${NC}"
    
    # Create a simple test program
    cat > /tmp/omp_test.cpp << 'EOF'
#include <omp.h>
#include <iostream>
int main() {
    #pragma omp parallel
    {
        #pragma omp single
        std::cout << "OpenMP threads: " << omp_get_num_threads() << std::endl;
    }
    return 0;
}
EOF
    
    if $compiler $flags /tmp/omp_test.cpp -o /tmp/omp_test 2>/dev/null; then
        if /tmp/omp_test >/dev/null 2>&1; then
            rm -f /tmp/omp_test /tmp/omp_test.cpp
            return 0
        fi
    fi
    rm -f /tmp/omp_test /tmp/omp_test.cpp
    return 1
}

COMPILER=""
CXXFLAGS=""

case "$OS" in
    Darwin*)
        echo -e "${YELLOW}macOS detected - checking for compilers...${NC}"
        
        for version in 14 13 12 11; do
            if command -v g++-$version &> /dev/null; then
                COMPILER="g++-$version"
                CXXFLAGS="-std=c++11 -O3 -fopenmp -Wall -Wextra"
                if check_openmp "$COMPILER" "$CXXFLAGS"; then
                    echo -e "${GREEN}✓ Using Homebrew GCC-$version with native OpenMP${NC}"
                    break
                fi
            fi
        done
        
        if [ -z "$COMPILER" ]; then
            if command -v clang++ &> /dev/null; then
                # Check for libomp in Homebrew locations
                if [ -d "/opt/homebrew/opt/libomp" ]; then
                    LIBOMP_PATH="/opt/homebrew/opt/libomp"
                elif [ -d "/usr/local/opt/libomp" ]; then
                    LIBOMP_PATH="/usr/local/opt/libomp"
                else
                    echo -e "${RED}✗ OpenMP library not found${NC}"
                    echo -e "${YELLOW}Please install libomp:${NC}"
                    echo -e "  ${BLUE}brew install libomp${NC}"
                    echo ""
                    echo -e "${YELLOW}Or install GCC for better OpenMP support:${NC}"
                    echo -e "  ${BLUE}brew install gcc${NC}"
                    exit 1
                fi
                
                COMPILER="clang++"
                CXXFLAGS="-std=c++11 -O3 -Xclang -fopenmp -Wall -Wextra -I${LIBOMP_PATH}/include -L${LIBOMP_PATH}/lib -lomp"
                
                if check_openmp "$COMPILER" "$CXXFLAGS"; then
                    echo -e "${GREEN}✓ Using Clang with Homebrew libomp${NC}"
                else
                    echo -e "${RED}✗ OpenMP test failed${NC}"
                    exit 1
                fi
            else
                echo -e "${RED}✗ No suitable compiler found${NC}"
                exit 1
            fi
        fi
        ;;
        
    Linux*)
        echo -e "${YELLOW}Linux detected - checking for compilers...${NC}"
        
        # Try g++ first
        if command -v g++ &> /dev/null; then
            COMPILER="g++"
            CXXFLAGS="-std=c++11 -O3 -fopenmp -Wall -Wextra"
            if check_openmp "$COMPILER" "$CXXFLAGS"; then
                echo -e "${GREEN}✓ Using g++ with OpenMP${NC}"
            else
                echo -e "${RED}✗ OpenMP test failed${NC}"
                exit 1
            fi
        else
            echo -e "${RED}✗ g++ not found${NC}"
            echo -e "${YELLOW}Please install g++:${NC}"
            echo -e "  ${BLUE}sudo apt-get install g++${NC}"
            exit 1
        fi
        ;;
        
    *)
        echo -e "${RED}✗ Unsupported OS: $OS${NC}"
        exit 1
        ;;
esac

SOURCE="src/dot_product.cpp"
OUTPUT="bin/dot_product"

echo ""
echo -e "${BLUE}Compilation settings:${NC}"
echo "  Compiler: $COMPILER"
echo "  Flags: $CXXFLAGS"
echo "  Source: $SOURCE"
echo "  Output: $OUTPUT"
echo ""

# Compile
echo -e "${YELLOW}Compiling...${NC}"
$COMPILER $CXXFLAGS $SOURCE -o $OUTPUT

# Check if compilation was successful
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Compilation successful!${NC}"
    echo -e "${GREEN}✓ Binary created: $OUTPUT${NC}"
    
    # Make executable
    chmod +x $OUTPUT
    
    # Show binary info
    echo ""
    echo -e "${BLUE}Binary information:${NC}"
    ls -lh $OUTPUT
    
    # Test OpenMP
    echo ""
    echo -e "${YELLOW}Testing OpenMP functionality...${NC}"
    export OMP_NUM_THREADS=4
    if $OUTPUT 10000 4 reduction 1 2>&1 | grep -q "Max threads available"; then
        echo -e "${GREEN}✓ OpenMP is working correctly!${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: Could not verify OpenMP functionality${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}=== Compilation Complete ===${NC}"
    exit 0
else
    echo -e "${RED}✗ Compilation failed!${NC}"
    exit 1
fi