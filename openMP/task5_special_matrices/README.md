# Task 5: Special Matrices with OpenMP Scheduling Strategies

## Описание задачи (Task Description)

Разработка программы для задачи 4 (поиск максимального значения среди минимальных элементов строк матрицы) при использовании матриц специального типа (ленточных, треугольных). Выполнение вычислительных экспериментов при разных правилах распределения итераций между потоками (static, dynamic, guided) и сравнение эффективности параллельных вычислений.

**Формула:**
```
y = max(min(a_ij)) для i=1..N, j=1..N
```

Implementation of parallel maximin problem solver for special matrix types (banded, triangular) using OpenMP with different scheduling strategies (static, dynamic, guided) for performance comparison.

## Структура проекта (Project Structure)

```
task5_special_matrices/
├── src/                          # Source code
│   └── special_matrices.cpp      # Main program with special matrices
├── scripts/                      # Automation scripts
│   ├── compile.sh                # Compilation script
│   ├── run_benchmarks.sh         # Benchmark runner
│   └── test_pipeline.sh          # Full test pipeline
├── data/                         # Configuration files
│   └── test_configs.json         # Test parameters
├── analysis/                     # Analysis scripts
│   ├── analyze.py                # Results processing
│   └── plot_graphs.py            # Graph generation
├── bin/                          # Compiled binaries
├── results/                      # Benchmark results (CSV)
├── graphs/                       # Generated graphs
├── .gitignore                    # Git ignore file
├── README.md                     # This file
└── QUICKSTART.md                 # Quick start guide
```

## Быстрый старт (Quick Start)

### 1. Компиляция (Compilation)

```bash
cd task5_special_matrices/scripts
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
- Размеры матриц: 500×500, 1000×1000, 2000×2000, 3000×3000
- Типы матриц: banded (ленточные), lower (нижнетреугольные), upper (верхнетреугольные)
- Количество потоков: 1, 2, 4, 8, 16, 32, 64, 128
- Стратегии планирования: static, dynamic, guided
- Размеры chunk: 0 (default), 10, 50
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
./bin/special_matrices <N> <matrix_type> <bandwidth> <num_threads> <schedule> <chunk_size> <iterations> [output_file]
```

### Параметры

- `N` - размер матрицы (NxN)
- `matrix_type` - тип матрицы:
  - `dense` - полная матрица (для сравнения)
  - `banded` - ленточная матрица
  - `lower` - нижнетреугольная матрица
  - `upper` - верхнетреугольная матрица
- `bandwidth` - ширина ленты для banded матриц (игнорируется для других типов)
- `num_threads` - количество потоков OpenMP
- `schedule` - стратегия планирования:
  - `static` - статическое распределение
  - `dynamic` - динамическое распределение
  - `guided` - управляемое распределение
- `chunk_size` - размер chunk для планирования (0 = default)
- `iterations` - количество запусков для усреднения
- `output_file` - (опционально) файл для сохранения результатов

### Примеры

```bash
# Ленточная матрица 1000×1000, bandwidth=10, 4 потока, static
./bin/special_matrices 1000 banded 10 4 static 0 10

# Нижнетреугольная матрица 2000×2000, 8 потоков, dynamic, chunk=10
./bin/special_matrices 2000 lower 0 8 dynamic 10 5

# Верхнетреугольная матрица 3000×3000, 16 потоков, guided
./bin/special_matrices 3000 upper 0 16 guided 0 10
```

## Реализация (Implementation)

### Типы матриц (Matrix Types)

#### 1. Ленточная матрица (Banded Matrix)
Ненулевые элементы только в пределах bandwidth от диагонали:
```
[x x x 0 0 0]
[x x x x 0 0]
[x x x x x 0]
[0 x x x x x]
[0 0 x x x x]
[0 0 0 x x x]
```

**Особенности:**
- Неравномерная вычислительная нагрузка по строкам
- Строки у краев матрицы имеют меньше элементов
- Идеальный случай для тестирования разных стратегий планирования

#### 2. Нижнетреугольная матрица (Lower Triangular)
Ненулевые элементы только когда i >= j:
```
[x 0 0 0 0 0]
[x x 0 0 0 0]
[x x x 0 0 0]
[x x x x 0 0]
[x x x x x 0]
[x x x x x x]
```

**Особенности:**
- Сильно неравномерная нагрузка
- Первые строки обрабатываются быстро, последние - медленно
- Демонстрирует важность балансировки нагрузки

#### 3. Верхнетреугольная матрица (Upper Triangular)
Ненулевые элементы только когда i <= j:
```
[x x x x x x]
[0 x x x x x]
[0 0 x x x x]
[0 0 0 x x x]
[0 0 0 0 x x]
[0 0 0 0 0 x]
```

**Особенности:**
- Обратная неравномерность относительно нижнетреугольной
- Первые строки обрабатываются медленно, последние - быстро
- Показывает влияние порядка обработки

### Стратегии планирования OpenMP (Scheduling Strategies)

#### 1. Static Schedule
```cpp
#pragma omp parallel for schedule(static) reduction(max:max_of_mins)
```

**Характеристики:**
- Итерации распределяются равномерно между потоками при запуске
- Минимальные накладные расходы
- Эффективно для равномерной нагрузки
- Неэффективно для неравномерной нагрузки (треугольные матрицы)

**Применение:**
- Полные матрицы
- Задачи с предсказуемой нагрузкой

#### 2. Dynamic Schedule
```cpp
#pragma omp parallel for schedule(dynamic, chunk_size) reduction(max:max_of_mins)
```

**Характеристики:**
- Итерации распределяются динамически во время выполнения
- Потоки получают новые chunk'и по мере завершения предыдущих
- Автоматическая балансировка нагрузки
- Больше накладных расходов на синхронизацию

**Применение:**
- Треугольные матрицы
- Задачи с непредсказуемой нагрузкой

#### 3. Guided Schedule
```cpp
#pragma omp parallel for schedule(guided, chunk_size) reduction(max:max_of_mins)
```

**Характеристики:**
- Размер chunk'а уменьшается экспоненциально
- Начинает с больших chunk'ов, заканчивает маленькими
- Компромисс между static и dynamic
- Хорошая балансировка с меньшими накладными расходами

**Применение:**
- Ленточные матрицы
- Задачи с постепенно меняющейся нагрузкой

### Влияние chunk_size

- **chunk_size = 0 (default)**: OpenMP выбирает оптимальный размер
- **Малый chunk_size (10)**: Лучшая балансировка, больше накладных расходов
- **Большой chunk_size (50)**: Меньше накладных расходов, хуже балансировка

## Проверка корректности (Correctness Verification)

Программа автоматически проверяет корректность:

```
Test 1: 3x3 dense matrix
  Sequential: 4.000000
  Static:     4.000000
  Dynamic:    4.000000
  Guided:     4.000000
  ✓ PASSED

Test 2: 100x100 banded matrix (bandwidth=5)
  Sequential: -95.234567
  Static:     -95.234567
  Dynamic:    -95.234567
  Guided:     -95.234567
  ✓ PASSED
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

1. **execution_time_[type]_size_*.png** - Время выполнения vs потоки для каждого типа матрицы
2. **speedup_[type]_size_*.png** - Ускорение vs потоки (с идеальной линией)
3. **efficiency_[type]_size_*.png** - Эффективность vs потоки
4. **schedule_comparison.png** - Сравнение стратегий планирования
5. **matrix_type_comparison.png** - Сравнение типов матриц
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

### Ленточные матрицы (Banded)
- **Static**: Хорошая производительность, но может быть дисбаланс
- **Dynamic**: Лучшая балансировка, небольшие накладные расходы
- **Guided**: Оптимальный компромисс для большинства случаев

### Нижнетреугольные матрицы (Lower Triangular)
- **Static**: Плохая балансировка, низкая эффективность
- **Dynamic**: Значительно лучше, хорошая балансировка
- **Guided**: Хорошая производительность, меньше накладных расходов чем dynamic

### Верхнетреугольные матрицы (Upper Triangular)
- Аналогично нижнетреугольным
- Dynamic и guided показывают лучшие результаты

## Для отчета (For Report)

Используйте следующие материалы:

1. **Графики ускорения** - показывают эффективность разных стратегий
2. **Графики эффективности** - демонстрируют качество масштабирования
3. **Сравнение стратегий** - влияние scheduling на производительность
4. **Сравнение типов матриц** - как структура данных влияет на параллелизацию
5. **Таблица summary_table.txt** - числовые данные для отчета

## Ключевые выводы (Key Findings)

1. ✅ Стратегия планирования критически важна для неравномерной нагрузки
2. ✅ Dynamic и guided эффективны для треугольных матриц
3. ✅ Static оптимален для равномерной нагрузки (полные матрицы)
4. ✅ Chunk size влияет на баланс между балансировкой и накладными расходами
5. ✅ Тип матрицы определяет оптимальную стратегию планирования
6. ✅ Для больших матриц различия между стратегиями более заметны

## Применение в реальных задачах (Real-world Applications)

### Матричные игры (Game Theory)
- Поиск нижней цены игры (maximin strategy)
- Оптимальные стратегии в условиях неопределенности

### Разреженные матрицы (Sparse Matrices)
- Ленточные матрицы часто встречаются в численных методах
- Треугольные матрицы в факторизации и решении систем

### Оптимизация производительности
- Выбор правильной стратегии планирования для конкретной задачи
- Балансировка нагрузки в неравномерных вычислениях

## Автор (Author)

Задание выполнено в рамках курса "Введение в суперкомпьютерные вычисления"

## Лицензия (License)

Учебный проект