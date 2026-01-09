#!/bin/bash

mkdir -p ../bin

if [[ "$OSTYPE" == "darwin"* ]]; then    
    if ! brew list libomp &>/dev/null; then
        brew install libomp
    fi
    
    LIBOMP_PREFIX=$(brew --prefix libomp)
    
    clang -Xpreprocessor -fopenmp -O3 -Wall \
          -I"$LIBOMP_PREFIX/include" \
          -L"$LIBOMP_PREFIX/lib" \
          -lomp \
          -o ../bin/min_max ../src/min_max.c -lm
else
    gcc -fopenmp -O3 -Wall -o ../bin/min_max ../src/min_max.c -lm
fi

if [ $? -eq 0 ]; then
    ../bin/min_max 1000 2 reduction 1 > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        exit 1
    fi
else
    exit 1
fi
