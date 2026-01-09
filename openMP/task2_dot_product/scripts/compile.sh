#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

cd "$PROJECT_ROOT"

mkdir -p bin

OS="$(uname -s)"

check_openmp() {
    local compiler=$1
    local flags=$2
    
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
        for version in 14 13 12 11; do
            if command -v g++-$version &> /dev/null; then
                COMPILER="g++-$version"
                CXXFLAGS="-std=c++11 -O3 -fopenmp -Wall -Wextra"
                if check_openmp "$COMPILER" "$CXXFLAGS"; then
                    break
                fi
            fi
        done
        
        if [ -z "$COMPILER" ]; then
            if command -v clang++ &> /dev/null; then
                if [ -d "/opt/homebrew/opt/libomp" ]; then
                    LIBOMP_PATH="/opt/homebrew/opt/libomp"
                elif [ -d "/usr/local/opt/libomp" ]; then
                    LIBOMP_PATH="/usr/local/opt/libomp"
                else
                    exit 1
                fi
                
                COMPILER="clang++"
                CXXFLAGS="-std=c++11 -O3 -Xclang -fopenmp -Wall -Wextra -I${LIBOMP_PATH}/include -L${LIBOMP_PATH}/lib -lomp"
                
                if ! check_openmp "$COMPILER" "$CXXFLAGS"; then
                    exit 1
                fi
            else
                exit 1
            fi
        fi
        ;;
        
    Linux*)
        if command -v g++ &> /dev/null; then
            COMPILER="g++"
            CXXFLAGS="-std=c++11 -O3 -fopenmp -Wall -Wextra"
            if ! check_openmp "$COMPILER" "$CXXFLAGS"; then
                exit 1
            fi
        else
            exit 1
        fi
        ;;
        
    *)
        exit 1
        ;;
esac

SOURCE="src/dot_product.cpp"
OUTPUT="bin/dot_product"

$COMPILER $CXXFLAGS $SOURCE -o $OUTPUT

if [ $? -eq 0 ]; then
    chmod +x $OUTPUT
else
    exit 1
fi
