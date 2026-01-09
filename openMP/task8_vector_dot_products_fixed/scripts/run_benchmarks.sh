#!/bin/bash

# Скрипт для запуска полных бенчмарков задачи 8

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BIN_DIR="$PROJECT_DIR/bin"
DATA_DIR="$PROJECT_DIR/data"
RESULTS_DIR="$PROJECT_DIR/results"

# Создаем необходимые директории
mkdir -p "$DATA_DIR"
mkdir -p "$RESULTS_DIR"

# Проверяем наличие исполняемого файла
if [ ! -f "$BIN_DIR/vector_dot_products" ]; then
    echo "Error: Binary not found. Please run compile.sh first."
    exit 1
fi

# Параметры бенчмарка
VECTOR_SIZES=(1000 5000 10000)
NUM_PAIRS_LIST=(10 50 100)
THREAD_COUNTS=(1 2 4 8)
RUNS=10

# Создаем файл результатов с временной меткой
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_FILE="$RESULTS_DIR/benchmark_${TIMESTAMP}.csv"

echo "=== Task 8: Vector Dot Products Benchmark ===" 
echo "Results will be saved to: $RESULTS_FILE"
echo ""

# Заголовок CSV
echo "num_pairs,vector_size,num_threads,method,total_time_ms,input_time_ms,computation_time_ms" > "$RESULTS_FILE"

# Счетчик прогресса
TOTAL_TESTS=$((${#VECTOR_SIZES[@]} * ${#NUM_PAIRS_LIST[@]} * ${#THREAD_COUNTS[@]} * 2))
CURRENT_TEST=0

echo "Total tests to run: $TOTAL_TESTS"
echo ""

# Основной цикл бенчмарков
for VECTOR_SIZE in "${VECTOR_SIZES[@]}"; do
    for NUM_PAIRS in "${NUM_PAIRS_LIST[@]}"; do
        DATA_FILE="$DATA_DIR/vectors_${NUM_PAIRS}_${VECTOR_SIZE}.txt"
        
        # Генерируем данные если их нет
        if [ ! -f "$DATA_FILE" ]; then
            echo "Generating data: $NUM_PAIRS pairs, vector size $VECTOR_SIZE..."
            "$BIN_DIR/vector_dot_products" generate "$NUM_PAIRS" "$VECTOR_SIZE" "$DATA_FILE"
        fi
        
        for THREADS in "${THREAD_COUNTS[@]}"; do
            # Sequential method (только для 1 потока)
            if [ "$THREADS" -eq 1 ]; then
                CURRENT_TEST=$((CURRENT_TEST + 1))
                echo "[$CURRENT_TEST/$TOTAL_TESTS] Sequential: pairs=$NUM_PAIRS, vec_size=$VECTOR_SIZE"
                
                OUTPUT=$("$BIN_DIR/vector_dot_products" benchmark "$DATA_FILE" 1 sequential "$RUNS" 2>&1)
                
                # Извлекаем времена из вывода
                TOTAL_TIME=$(echo "$OUTPUT" | grep "Total time:" | awk '{print $3}')
                INPUT_TIME=$(echo "$OUTPUT" | grep "Input time:" | awk '{print $3}')
                COMPUTE_TIME=$(echo "$OUTPUT" | grep "Compute time:" | awk '{print $3}')
                
                echo "$NUM_PAIRS,$VECTOR_SIZE,1,sequential,$TOTAL_TIME,$INPUT_TIME,$COMPUTE_TIME" >> "$RESULTS_FILE"
            fi
            
            # Sections method
            CURRENT_TEST=$((CURRENT_TEST + 1))
            echo "[$CURRENT_TEST/$TOTAL_TESTS] Sections: pairs=$NUM_PAIRS, vec_size=$VECTOR_SIZE, threads=$THREADS"
            
            OUTPUT=$("$BIN_DIR/vector_dot_products" benchmark "$DATA_FILE" "$THREADS" sections "$RUNS" 2>&1)
            
            # Извлекаем времена из вывода
            TOTAL_TIME=$(echo "$OUTPUT" | grep "Total time:" | awk '{print $3}')
            INPUT_TIME=$(echo "$OUTPUT" | grep "Input time:" | awk '{print $3}')
            COMPUTE_TIME=$(echo "$OUTPUT" | grep "Compute time:" | awk '{print $3}')
            
            echo "$NUM_PAIRS,$VECTOR_SIZE,$THREADS,sections,$TOTAL_TIME,$INPUT_TIME,$COMPUTE_TIME" >> "$RESULTS_FILE"
        done
        
        echo ""
    done
done

echo "=== Benchmark Complete ===" 
echo "Results saved to: $RESULTS_FILE"
echo ""
echo "Next steps:"
echo "1. Analyze results:"
echo "   cd $PROJECT_DIR/analysis"
echo "   python3 analyze.py $RESULTS_FILE"
echo ""
echo "2. Generate graphs:"
echo "   python3 plot_graphs.py"
echo ""