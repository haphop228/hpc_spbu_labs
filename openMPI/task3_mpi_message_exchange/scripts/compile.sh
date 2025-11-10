#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Compiling MPI Message Exchange Program ===${NC}"
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

# Function to check if MPI is working
check_mpi() {
    local compiler=$1
    echo -e "${YELLOW}Checking MPI support...${NC}"
    
    # Create a simple test program
    cat > /tmp/mpi_test.cpp << 'EOF'
#include <mpi.h>
#include <iostream>
int main(int argc, char** argv) {
    MPI_Init(&argc, &argv);
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    if (rank == 0) {
        std::cout << "MPI is working with " << size << " processes" << std::endl;
    }
    MPI_Finalize();
    return 0;
}
EOF
    
    if $compiler /tmp/mpi_test.cpp -o /tmp/mpi_test 2>/dev/null; then
        if mpirun -np 2 /tmp/mpi_test >/dev/null 2>&1; then
            rm -f /tmp/mpi_test /tmp/mpi_test.cpp
            return 0
        fi
    fi
    rm -f /tmp/mpi_test /tmp/mpi_test.cpp
    return 1
}

COMPILER=""
CXXFLAGS=""

case "$OS" in
    Darwin*)
        echo -e "${YELLOW}macOS detected - checking for MPI compilers...${NC}"
        
        # Try mpic++ (OpenMPI)
        if command -v mpic++ &> /dev/null; then
            COMPILER="mpic++"
            CXXFLAGS="-std=c++11 -O3 -Wall -Wextra"
            if check_mpi "$COMPILER"; then
                echo -e "${GREEN}✓ Using mpic++ (OpenMPI)${NC}"
            else
                echo -e "${RED}✗ MPI test failed${NC}"
                exit 1
            fi
        else
            echo -e "${RED}✗ MPI compiler not found${NC}"
            echo -e "${YELLOW}Please install OpenMPI:${NC}"
            echo -e "  ${BLUE}brew install open-mpi${NC}"
            exit 1
        fi
        ;;
        
    Linux*)
        echo -e "${YELLOW}Linux detected - checking for MPI compilers...${NC}"
        
        # Try mpic++ or mpicxx
        if command -v mpic++ &> /dev/null; then
            COMPILER="mpic++"
            CXXFLAGS="-std=c++11 -O3 -Wall -Wextra"
            if check_mpi "$COMPILER"; then
                echo -e "${GREEN}✓ Using mpic++ (OpenMPI/MPICH)${NC}"
            else
                echo -e "${RED}✗ MPI test failed${NC}"
                exit 1
            fi
        elif command -v mpicxx &> /dev/null; then
            COMPILER="mpicxx"
            CXXFLAGS="-std=c++11 -O3 -Wall -Wextra"
            if check_mpi "$COMPILER"; then
                echo -e "${GREEN}✓ Using mpicxx (MPICH)${NC}"
            else
                echo -e "${RED}✗ MPI test failed${NC}"
                exit 1
            fi
        else
            echo -e "${RED}✗ MPI compiler not found${NC}"
            echo -e "${YELLOW}Please install OpenMPI or MPICH:${NC}"
            echo -e "  ${BLUE}sudo apt-get install libopenmpi-dev${NC}"
            echo -e "  ${BLUE}# or${NC}"
            echo -e "  ${BLUE}sudo apt-get install mpich${NC}"
            exit 1
        fi
        ;;
        
    *)
        echo -e "${RED}✗ Unsupported OS: $OS${NC}"
        exit 1
        ;;
esac

SOURCE="src/message_exchange.cpp"
OUTPUT="bin/message_exchange"

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
    
    # Test MPI functionality
    echo ""
    echo -e "${YELLOW}Testing MPI functionality...${NC}"
    if mpirun -np 2 $OUTPUT 1024 5 2>&1 | grep -q "Benchmark Results"; then
        echo -e "${GREEN}✓ MPI is working correctly!${NC}"
    else
        echo -e "${YELLOW}⚠ Warning: Could not verify MPI functionality${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}=== Compilation Complete ===${NC}"
    echo ""
    echo -e "${BLUE}Usage:${NC}"
    echo "  mpirun -np 2 $OUTPUT <message_size> <iterations> [output_file]"
    echo ""
    echo -e "${BLUE}Examples:${NC}"
    echo "  mpirun -np 2 $OUTPUT 1024 100"
    echo "  mpirun -np 2 $OUTPUT 1048576 50 results/benchmark.csv"
    exit 0
else
    echo -e "${RED}✗ Compilation failed!${NC}"
    exit 1
fi