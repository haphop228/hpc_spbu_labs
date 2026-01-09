#!/bin/bash

# Compilation script for Task 8: Vector Dot Products with Sections

set -e

echo "=== Компиляция Task 8: Vector Dot Products with Sections ==="

# Определение ОС
OS=$(uname -s)
echo "Операционная система: $OS"

# Переход в корневую директорию проекта
cd "$(dirname "$0")/.."

# Создание директорий
mkdir -p bin data results graphs

# Определение компилятора и флагов
if [ "$OS" = "Darwin" ]; then
    # macOS
    echo "Настройка для macOS..."
    
    # Проверка наличия GCC
    if command -v g++-13 &> /dev/null; then
        CXX=g++-13
        echo "Используется GCC-13"
    elif command -v g++-12 &> /dev/null; then
        CXX=g++-12
        echo "Используется GCC-12"
    elif command -v g++-11 &> /dev/null; then
        CXX=g++-11
        echo "Используется GCC-11"
    else
        # Попытка использовать Clang с libomp
        if [ -d "/opt/homebrew/opt/libomp" ]; then
            CXX=clang++
            EXTRA_FLAGS="-Xpreprocessor -fopenmp -I/opt/homebrew/opt/libomp/include -L/opt/homebrew/opt/libomp/lib -lomp"
            echo "Используется Clang с libomp (Homebrew ARM)"
        elif [ -d "/usr/local/opt/libomp" ]; then
            CXX=clang++
            EXTRA_FLAGS="-Xpreprocessor -fopenmp -I/usr/local/opt/libomp/include -L/usr/local/opt/libomp/lib -lomp"
            echo "Используется Clang с libomp (Homebrew Intel)"
        else
            echo "ОШИБКА: Не найден компилятор с поддержкой OpenMP"
            echo "Установите GCC: brew install gcc"
            echo "Или libomp: brew install libomp"
            exit 1
        fi
    fi
else
    # Linux
    echo "Настройка для Linux..."
    CXX=g++
    EXTRA_FLAGS=""
fi

# Флаги компиляции
if [ "$CXX" = "clang++" ] && [[ "$EXTRA_FLAGS" == *"-Xpreprocessor"* ]]; then
    # Для Clang с libomp флаг -fopenmp уже в EXTRA_FLAGS
    CXXFLAGS="-std=c++17 -O3 -Wall -Wextra"
else
    # Для GCC используем обычный -fopenmp
    CXXFLAGS="-std=c++17 -O3 -fopenmp -Wall -Wextra"
fi

echo "Компилятор: $CXX"
echo "Флаги: $CXXFLAGS $EXTRA_FLAGS"

# Компиляция
echo ""
echo "Компиляция vector_dot_products.cpp..."
$CXX $CXXFLAGS $EXTRA_FLAGS src/vector_dot_products.cpp -o bin/vector_dot_products

if [ $? -eq 0 ]; then
    echo "✓ Компиляция успешна!"
    echo ""
    
    # Проверка OpenMP
    echo "Проверка поддержки OpenMP..."
    export OMP_NUM_THREADS=2
    
    # Генерация тестовых данных
    echo "Генерация тестовых данных..."
    ./bin/vector_dot_products generate 10 100 data/test_vectors.txt
    
    # Проверка корректности
    echo ""
    echo "Проверка корректности..."
    ./bin/vector_dot_products verify data/test_vectors.txt
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ OpenMP работает корректно!"
        echo ""
        echo "=== Компиляция завершена успешно ==="
        echo ""
        echo "Для запуска программы:"
        echo "  ./bin/vector_dot_products <command> [options]"
        echo ""
        echo "Примеры:"
        echo "  ./bin/vector_dot_products generate 100 1000 data/vectors.txt"
        echo "  ./bin/vector_dot_products benchmark data/vectors.txt 2 sections 10"
        echo "  ./bin/vector_dot_products verify data/vectors.txt"
        echo ""
        echo "Для запуска бенчмарков:"
        echo "  cd scripts && ./run_benchmarks.sh"
    else
        echo "✗ Ошибка при проверке корректности"
        exit 1
    fi
else
    echo "✗ Ошибка компиляции"
    exit 1
fi