# Task 4: Matrix Game (Maximin Problem) with OpenMP

## Описание задачи (Task Description)

Разработка программы решения задачи поиска максимального значения среди минимальных элементов строк матрицы. Такая задача имеет место для решения матричных игр (поиск нижней цены игры).

**Формула:**
```
y = max(min(a_ij)) для i=1..N, j=1..N
```

где `a_ij` - элементы матрицы NxN.

Implementation of parallel maximin problem solver using OpenMP with multiple synchronization methods for performance comparison.

## Структура проекта (Project Structure)

```
task4_matrix_game/
├── src/                    # Source code
│   └── matrix_game.cpp     # Main program with OpenMP
├── scripts/                # Automation scripts
│   ├── compile.sh          # Compilation script
│   ├── run_benchmarks.sh   # Benchmark runner
│   └── test_pipeline.sh    # Full test pipeline
├── data/                   # Configuration files
│   └── test_configs.json   # Test parameters
├── analysis/               # Analysis scripts
│   ├── analyze.py          # Results processing
│   └── plot_graphs.py      # Graph generation
├── bin/                    # Compiled binaries
├── results/                # Benchmark results (CSV)
├── graphs/                 # Generated graphs
├── .gitignore             # Git ignore file
└── README.md              # This file
```

## Быстрый старт (Quick Start)

### 1. Компиляция (Compilation)

```bash
cd task4_matrix_game/scripts
chmod +x *.sh
./compile.sh
```

Скрипт автоматически:
- Определит вашу ОС (macOS/Linux)
- Найдет подходящий компилятор с поддержкой OpenMP
- Скомпилирует программу с оптимизациями
- Проверит работу OpenMP

### 2. Быстрый тест (Quick Test)

```bash
./test_pipeline.sh
```

Выполнит:
- Компиляцию программы
- Проверку корректности вычислений
- Быстрый бенчмарк
- Проверку зависимостей Python

### 3. Полный бенчмарк (Full Benchmark)

```bash
./run_benchmarks.sh
```

Запустит полный набор тестов:
- Размеры матриц: 100×100, 500×500, 1000×1000, 2000×2000, 3000×3000
- Количество потоков: 1, 2, 4, 8, 16, 32, 64, 128
- Метод: OpenMP reduction
- По 10 запусков каждой конфигурации

### 4. Анализ результатов (Analysis)

```bash
cd ../analysis

# Обработка данных
python3 analyze.py ../results/benchmark_YYYYMMDD_HHMMSS.csv

# Генерация графиков
python3 plot_graphs.py
```

## Использование программы (Program Usage)

### Формат команды

```bash
./bin/matrix_game <N> <num_threads> <method> <iterations> [output_file]
```

### Параметры

- `N` - размер матрицы (NxN)
- `num_threads` - количество потоков OpenMP
- `method` - метод вычисления:
  - `sequential` - последовательное выполнение
  - `reduction` - с использованием OpenMP reduction (рекомендуется)
- `iterations` - количество запусков для усреднения
- `output_file` - (опционально) файл для сохранения результатов

### Примеры

```bash
# Матрица 1000×1000, 4 потока, метод reduction
./bin/matrix_game 1000 4 reduction 10

# Матрица 2000×2000, 8 потоков, метод reduction
./bin/matrix_game 2000 8 reduction 5

# Матрица 3000×3000, 16 потоков, с сохранением в файл
./bin/matrix_game 3000 16 reduction 10 results/test.csv
```

## Реализация (Implementation)

### Алгоритм

1. **Генерация матрицы**: случайные числа в диапазоне [-100, 100]
2. **Для каждой строки**: найти минимальный элемент
3. **Среди минимумов**: найти максимальное значение

### Метод параллелизации с OpenMP Reduction

```cpp
double maximin_reduction(const Matrix& matrix, int num_threads) {
    int N = matrix.size();
    double max_of_mins = std::numeric_limits<double>::lowest();
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel for reduction(max:max_of_mins)
    for (int i = 0; i < N; ++i) {
        double row_min = matrix[i][0];
        for (int j = 1; j < N; ++j) {
            row_min = std::min(row_min, matrix[i][j]);
        }
        max_of_mins = std::max(max_of_mins, row_min);
    }
    
    return max_of_mins;
}
```

**Преимущества OpenMP Reduction:**
- Автоматическая оптимизация компилятором
- Минимальные накладные расходы на синхронизацию
- Эффективное распределение работы между потоками
- Встроенная поддержка операции max в OpenMP
- Оптимальная производительность для данной задачи

## Проверка корректности (Correctness Verification)

Программа автоматически проверяет корректность:

```
Test 1: 3x3 matrix (expected = 4.0)
  Sequential: 4.000000 (error: 0.000000)
  Reduction:  4.000000 (error: 0.000000)
  ✓ PASSED

Test 2: 100x100 random matrix
  Sequential: -95.234567
  Reduction:  -95.234567
  ✓ PASSED - Both methods agree
```

## Метрики производительности (Performance Metrics)

### 1. Время выполнения (Execution Time)
Абсолютное время выполнения операции в миллисекундах.

### 2. Ускорение (Speedup)
```
Speedup = T(1) / T(n)
```
где T(1) - время на 1 потоке, T(n) - время на n потоках.

### 3. Эффективность (Efficiency)
```
Efficiency = Speedup / n
```
где n - количество потоков.

Идеальная эффективность = 1.0 (100%)

## Генерируемые графики (Generated Graphs)

После запуска анализа в директории `graphs/` создаются:

1. **execution_time_size_*.png** - Время выполнения vs количество потоков
2. **speedup_size_*.png** - Ускорение vs количество потоков (с идеальной линией)
3. **efficiency_size_*.png** - Эффективность vs количество потоков
4. **size_comparison.png** - Сравнение производительности для разных размеров матриц
5. **scalability_analysis.png** - Анализ масштабируемости (strong scaling)
6. **summary_table.txt** - Сводная таблица результатов

## Требования (Requirements)

### Система (System)
- macOS или Linux
- Компилятор с поддержкой OpenMP:
  - GCC 11+ (рекомендуется для macOS)
  - Clang с libomp
  - GCC на Linux
- Минимум 4 ядра CPU (рекомендуется 8+)

### Python (для анализа)
```bash
pip3 install pandas matplotlib numpy
```

## Установка зависимостей (Dependencies Installation)

### macOS

```bash
# Установка GCC с OpenMP (рекомендуется)
brew install gcc

# Или установка libomp для Clang
brew install libomp

# Python пакеты
pip3 install pandas matplotlib numpy
```

### Linux

```bash
# GCC обычно уже установлен
sudo apt-get update
sudo apt-get install g++

# Python пакеты
pip3 install pandas matplotlib numpy
```

## Ожидаемые результаты (Expected Results)

### Малые матрицы (100×100)
- Ускорение: 2-4x при 4-8 потоках
- Накладные расходы заметны
- Эффективность снижается при >8 потоках

### Средние матрицы (1000×1000)
- Ускорение: 4-8x при 8-16 потоках
- Хорошая масштабируемость
- Оптимальный баланс вычислений/синхронизации

### Большие матрицы (3000×3000)
- Ускорение: 8-16x при 16-32 потоках
- Наилучшая масштабируемость
- Минимальные относительные накладные расходы

### Производительность OpenMP Reduction
- Оптимальная производительность благодаря встроенным оптимизациям OpenMP
- Эффективное распределение работы между потоками
- Минимальные накладные расходы на синхронизацию

## Для отчета (For Report)

Используйте следующие материалы:

1. **Графики ускорения** - показывают эффективность параллелизации
2. **Графики эффективности** - демонстрируют качество масштабирования
3. **Сравнение размеров** - влияние размера матрицы на производительность
4. **Таблица summary_table.txt** - числовые данные для отчета
5. **Анализ масштабируемости** - strong scaling analysis

## Ключевые выводы (Key Findings)

1. Задача maximin отлично параллелится с помощью OpenMP reduction
2. Размер матрицы существенно влияет на эффективность параллелизации
3. OpenMP reduction обеспечивает оптимальную производительность
4. Накладные расходы на синхронизацию минимальны благодаря встроенным оптимизациям
5. Оптимальное количество потоков зависит от размера матрицы
6. Для малых матриц параллелизация может быть неэффективна из-за overhead

## Применение в матричных играх (Application in Game Theory)

Эта задача решает поиск **нижней цены игры** (maximin strategy):
- Игрок выбирает стратегию, максимизирующую свой минимальный выигрыш
- Гарантирует минимальный выигрыш независимо от действий противника
- Используется в теории игр для поиска оптимальных стратегий

## Автор (Author)

Задание выполнено в рамках курса "Введение в суперкомпьютерные вычисления"

## Лицензия (License)

Учебный проект