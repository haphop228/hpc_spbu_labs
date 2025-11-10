# Task 9: Nested Parallelism with OpenMP

## Описание задачи (Task Description)

Исследование поддержки вложенного параллелизма компилятором и разработка программы с использованием и без использования вложенного параллелизма на основе задачи 4 (поиск максимального значения среди минимальных элементов строк матрицы).

**Implementation of nested parallelism support investigation:**
- Check compiler support for nested parallel regions
- Implement flat parallelism (single-level, outer loop only)
- Implement nested parallelism (two-level, both outer and inner loops)
- Compare performance and efficiency of both approaches

## Структура проекта (Project Structure)

```
task9_nested_parallelism/
├── src/                          # Source code
│   └── nested_parallelism.cpp    # Main program with flat and nested parallelism
├── scripts/                      # Automation scripts
│   ├── compile.sh                # Compilation script
│   ├── run_benchmarks.sh         # Benchmark runner
│   └── test_pipeline.sh          # Full test pipeline
├── analysis/                     # Analysis scripts
│   ├── analyze.py                # Results processing
│   └── plot_graphs.py            # Graph generation
├── bin/                          # Compiled binaries
├── results/                      # Benchmark results (CSV)
├── graphs/                       # Generated graphs
├── .gitignore                    # Git ignore file
└── README.md                     # This file
```

## Быстрый старт (Quick Start)

### 1. Компиляция (Compilation)

```bash
cd task9_nested_parallelism/scripts
chmod +x *.sh
./compile.sh
```

Скрипт автоматически:
- Определит вашу ОС (macOS/Linux)
- Найдет подходящий компилятор с поддержкой OpenMP
- Проверит поддержку вложенного параллелизма
- Скомпилирует программу с оптимизациями

### 2. Быстрый тест (Quick Test)

```bash
./test_pipeline.sh
```

Выполнит:
- Компиляцию программы
- Проверку поддержки вложенного параллелизма
- Проверку корректности вычислений
- Быстрый бенчмарк
- Проверку зависимостей Python

### 3. Полный бенчмарк (Full Benchmark)

```bash
./run_benchmarks.sh
```

Запустит полный набор тестов:
- Размеры матриц: 500×500, 1000×1000, 2000×2000
- Количество потоков: 1, 2, 4, 8, 16, 32, 64, 128
- Методы: sequential, flat, nested
- По 10 запусков каждой конфигурации

⏱️ **Время выполнения:** ~20-40 минут в зависимости от системы

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
./bin/nested_parallelism <N> <num_threads> <method> <iterations> [output_file]
```

### Параметры

- `N` - размер матрицы (NxN)
- `num_threads` - количество потоков:
  - Для `flat`: просто число (например, `4`)
  - Для `nested`: формат `outer:inner` (например, `2:2` для 2×2=4 потока)
- `method` - метод вычисления:
  - `sequential` - последовательное выполнение
  - `flat` - плоский параллелизм (только внешний цикл)
  - `nested` - вложенный параллелизм (оба цикла)
- `iterations` - количество запусков для усреднения
- `output_file` - (опционально) файл для сохранения результатов

### Примеры

```bash
# Последовательное выполнение (baseline)
./bin/nested_parallelism 1000 1 sequential 10

# Плоский параллелизм, 4 потока
./bin/nested_parallelism 1000 4 flat 10

# Вложенный параллелизм, 2×2=4 потока
./bin/nested_parallelism 1000 2:2 nested 10

# Вложенный параллелизм, 4×2=8 потоков
./bin/nested_parallelism 1000 4:2 nested 10

# С сохранением результатов
./bin/nested_parallelism 2000 8 flat 10 results/test.csv
```

## Реализация (Implementation)

### Алгоритм Maximin

Формула: `y = max(min(a_ij))` для `i=1..N, j=1..N`

**Алгоритм:**
1. Для каждой строки матрицы найти минимальный элемент
2. Среди всех минимумов найти максимальное значение

### 1. Плоский параллелизм (Flat Parallelism)

Параллелизуется только внешний цикл (по строкам):

```cpp
double maximin_flat(const Matrix& matrix, int num_threads) {
    int N = matrix.size();
    double max_of_mins = std::numeric_limits<double>::lowest();
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel for reduction(max:max_of_mins)
    for (int i = 0; i < N; ++i) {
        // Внутренний цикл выполняется последовательно
        double row_min = matrix[i][0];
        for (int j = 1; j < N; ++j) {
            row_min = std::min(row_min, matrix[i][j]);
        }
        max_of_mins = std::max(max_of_mins, row_min);
    }
    
    return max_of_mins;
}
```

**Характеристики:**
- Один уровень параллелизма
- Простая реализация
- Хорошая масштабируемость для больших матриц
- Стандартный подход для большинства задач

### 2. Вложенный параллелизм (Nested Parallelism)

Параллелизуются оба цикла (внешний и внутренний):

```cpp
double maximin_nested(const Matrix& matrix, int outer_threads, int inner_threads) {
    int N = matrix.size();
    double max_of_mins = std::numeric_limits<double>::lowest();
    
    // Включение вложенного параллелизма
    omp_set_nested(1);
    omp_set_max_active_levels(2);
    
    omp_set_num_threads(outer_threads);
    
    // Внешний параллельный регион (по строкам)
    #pragma omp parallel for reduction(max:max_of_mins)
    for (int i = 0; i < N; ++i) {
        double row_min = std::numeric_limits<double>::max();
        
        // Внутренний параллельный регион (по столбцам в строке)
        #pragma omp parallel for num_threads(inner_threads) reduction(min:row_min)
        for (int j = 0; j < N; ++j) {
            row_min = std::min(row_min, matrix[i][j]);
        }
        
        max_of_mins = std::max(max_of_mins, row_min);
    }
    
    return max_of_mins;
}
```

**Характеристики:**
- Два уровня параллелизма
- Более сложная реализация
- Дополнительные накладные расходы на создание вложенных регионов
- Может быть эффективна для очень больших матриц

## Проверка поддержки вложенного параллелизма

Программа автоматически проверяет поддержку:

```
=== Checking Nested Parallelism Support ===
Max active levels: 2
Nested parallelism enabled: YES

Testing nested parallelism:
  Outer thread 0/2 -> Inner thread 0/2
  Outer thread 0/2 -> Inner thread 1/2
  Outer thread 1/2 -> Inner thread 0/2
  Outer thread 1/2 -> Inner thread 1/2

✓ Nested parallelism is SUPPORTED
```

## Проверка корректности (Correctness Verification)

Программа автоматически проверяет корректность:

```
=== Correctness Verification ===

Test 1: 3x3 matrix (expected = 4.0)
  Sequential: 4.000000 (error: 0.000000)
  Flat:       4.000000 (error: 0.000000)
  Nested:     4.000000 (error: 0.000000)
  ✓ PASSED

Test 2: 100x100 random matrix
  Sequential: -95.234567
  Flat:       -95.234567
  Nested:     -95.234567
  ✓ PASSED - All methods agree
```

## Метрики производительности (Performance Metrics)

### 1. Время выполнения (Execution Time)
Абсолютное время выполнения операции в миллисекундах.

### 2. Ускорение (Speedup)
```
Speedup = T(sequential) / T(parallel)
```

### 3. Эффективность (Efficiency)
```
Efficiency = Speedup / num_threads
```

Идеальная эффективность = 1.0 (100%)

## Генерируемые графики (Generated Graphs)

После запуска анализа в директории `graphs/` создаются:

1. **execution_time_size_*.png** - Время выполнения vs потоки
2. **speedup_size_*.png** - Ускорение vs потоки (с идеальной линией)
3. **efficiency_size_*.png** - Эффективность vs потоки
4. **comparison_flat_vs_nested.png** - Прямое сравнение методов
5. **speedup_comparison_all.png** - Сравнение ускорения для всех размеров
6. **summary_table.txt** - Сводная таблица результатов

## Требования (Requirements)

### Система (System)
- macOS или Linux
- Компилятор с поддержкой OpenMP и nested parallelism:
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

### Плоский параллелизм (Flat)

**Преимущества:**
- Простая реализация
- Низкие накладные расходы
- Хорошая масштабируемость
- Стандартный подход

**Производительность:**
- Малые матрицы (500×500): 2-4x ускорение
- Средние матрицы (1000×1000): 4-8x ускорение
- Большие матрицы (2000×2000): 8-16x ускорение

### Вложенный параллелизм (Nested)

**Преимущества:**
- Два уровня параллелизма
- Потенциально лучшее использование ресурсов
- Гибкость в распределении потоков

**Недостатки:**
- Дополнительные накладные расходы
- Сложность управления потоками
- Может быть медленнее для малых задач

**Производительность:**
- Обычно сопоставима или немного хуже flat
- Может быть эффективна для очень больших матриц
- Зависит от соотношения outer:inner потоков

### Сравнение

**Когда flat лучше:**
- Малые и средние матрицы
- Ограниченное количество ядер
- Простота важнее гибкости

**Когда nested может быть лучше:**
- Очень большие матрицы
- Много доступных ядер (64+)
- Неравномерная нагрузка по строкам

## Для отчета (For Report)

Используйте следующие материалы:

1. **Проверка поддержки** - демонстрация работы nested parallelism
2. **Графики ускорения** - сравнение flat vs nested
3. **Графики эффективности** - анализ масштабируемости
4. **Прямое сравнение** - bar charts для разных размеров
5. **Таблица summary_table.txt** - числовые данные для отчета

## Ключевые выводы (Key Findings)

1. ✅ **Компилятор поддерживает вложенный параллелизм**
   - OpenMP позволяет создавать вложенные параллельные регионы
   - Требуется явное включение через `omp_set_nested(1)`
   - Необходимо установить `omp_set_max_active_levels(2)`

2. ✅ **Плоский параллелизм обычно эффективнее**
   - Меньше накладных расходов
   - Проще в реализации и отладке
   - Лучшая производительность для большинства случаев

3. ✅ **Вложенный параллелизм имеет ограничения**
   - Дополнительные накладные расходы на создание регионов
   - Сложность управления потоками
   - Может быть полезен для специфических задач

4. ✅ **Выбор подхода зависит от задачи**
   - Размер матрицы
   - Количество доступных ядер
   - Характер вычислений
   - Требования к производительности

5. ✅ **Практические рекомендации**
   - Для большинства задач используйте flat parallelism
   - Nested parallelism для очень больших данных и специфических случаев
   - Всегда измеряйте производительность обоих подходов
   - Учитывайте накладные расходы

## Применение вложенного параллелизма (Use Cases)

### Когда использовать nested parallelism:

1. **Многомерные данные**
   - Обработка 3D/4D массивов
   - Тензорные операции
   - Научные симуляции

2. **Иерархические алгоритмы**
   - Рекурсивные задачи
   - Divide-and-conquer алгоритмы
   - Древовидные структуры

3. **Гетерогенные вычисления**
   - Разные типы операций на разных уровнях
   - Комбинация CPU и GPU
   - Распределенные системы

### Когда НЕ использовать nested parallelism:

1. **Малые задачи** - накладные расходы превышают выгоду
2. **Ограниченные ресурсы** - недостаточно ядер для эффективного использования
3. **Простые циклы** - flat parallelism достаточен и эффективнее

## Автор (Author)

Задание выполнено в рамках курса "Введение в суперкомпьютерные вычисления"

## Лицензия (License)

Учебный проект