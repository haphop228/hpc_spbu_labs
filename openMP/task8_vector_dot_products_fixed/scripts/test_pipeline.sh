#!/bin/bash

# Полный тестовый пайплайн для задачи 8

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Task 8: Vector Dot Products - Test Pipeline ===" 
echo ""

# Шаг 1: Компиляция
echo "Step 1: Compiling..."
"$SCRIPT_DIR/compile.sh"
echo ""

# Шаг 2: Генерация тестовых данных
echo "Step 2: Generating test data..."
mkdir -p "$PROJECT_DIR/data"
TEST_DATA="$PROJECT_DIR/data/test_vectors.txt"
"$PROJECT_DIR/bin/vector_dot_products" generate 20 5000 "$TEST_DATA"
echo ""

# Шаг 3: Проверка корректности
echo "Step 3: Verifying correctness..."
"$PROJECT_DIR/bin/vector_dot_products" verify "$TEST_DATA"
echo ""

# Шаг 4: Быстрый бенчмарк
echo "Step 4: Running quick benchmark..."
"$PROJECT_DIR/bin/vector_dot_products" full "$TEST_DATA" 5
echo ""

# Шаг 5: Проверка Python зависимостей
echo "Step 5: Checking Python dependencies..."
python3 -c "import pandas, matplotlib, numpy" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ All Python dependencies are installed"
else
    echo "⚠ Warning: Some Python dependencies are missing"
    echo "  Install with: pip3 install pandas matplotlib numpy"
fi
echo ""

echo "=== Test Pipeline Complete ===" 
echo ""
echo "Next steps:"
echo "1. Run full benchmarks:"
echo "   cd $SCRIPT_DIR"
echo "   ./run_benchmarks.sh"
echo ""
echo "2. Analyze results:"
echo "   cd $PROJECT_DIR/analysis"
echo "   python3 analyze.py ../results/benchmark_YYYYMMDD_HHMMSS.csv"
echo "   python3 plot_graphs.py"
echo ""