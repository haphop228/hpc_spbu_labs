# Task 3: Numerical Integration with OpenMP

## Описание задачи (Task Description)

Разработка программы для вычисления определенного интеграла с использованием метода прямоугольников (Rectangle Method) и OpenMP для параллелизации.

**Формула метода прямоугольников:**
```
y = ∫ₐᵇ f(x)dx ≈ h ∑ᵢ₌₀ᴺ⁻¹ fᵢ
где: fᵢ = f(xᵢ), xᵢ = ih, h = (b-a)/N
```

Implementation of parallel numerical integration using the Rectangle Method with OpenMP reduction for efficient parallelization.

## Структура проекта (Project Structure)

```
task3_integration/
├── src/                    # Source code
│   └── integration.cpp     # Main program with OpenMP
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
cd task3_integration/scripts
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
- Размеры задач (N): 10⁶, 10⁷, 10⁸
- Количество потоков: 1, 2, 4, 8, 16, 32, 64, 128
- Функции: x², sin(x), 1/(1+x²)
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
./bin/integration <function> <a> <b> <N> <num_threads> <method> <iterations> [output_file]
```

### Параметры

- `function` - тестовая функция:
  - `x2` - f(x) = x²
  - `sin` - f(x) = sin(x)
  - `exp` - f(x) = eˣ
  - `arctan` - f(x) = 1/(1+x²)
  - `circle` - f(x) = √(1-x²)
- `a` - нижняя граница интегрирования
- `b` - верхняя граница интегрирования
- `N` - количество разбиений (шагов)
- `num_threads` - количество потоков OpenMP
- `method` - метод вычисления:
  - `sequential` - последовательное выполнение
  - `reduction` - с использованием OpenMP reduction
- `iterations` - количество запусков для усреднения
- `output_file` - (опционально) файл для сохранения результатов

### Примеры

```bash
# Интеграл x² от 0 до 1, 4 потока, метод reduction
./bin/integration x2 0 1 1000000 4 reduction 10

# Интеграл sin(x) от 0 до π, 8 потоков
./bin/integration sin 0 3.14159 10000000 8 reduction 5

# Интеграл 1/(1+x²) от 0 до 1 (π/4), с сохранением в файл
./bin/integration arctan 0 1 100000000 16 reduction 10 results/test.csv
```

## Реализация (Implementation)

### Метод с редукцией (Reduction Method)

```cpp
double integrate_reduction(FunctionPtr f, double a, double b, long long N, int num_threads) {
    double h = (b - a) / N;
    double sum = 0.0;
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel for reduction(+:sum)
    for (long long i = 0; i < N; ++i) {
        double x_i = a + i * h;
        sum += f(x_i);
    }
    
    return h * sum;
}
```

**Преимущества:**
- Простая и элегантная реализация
- Автоматическая оптимизация компилятором
- Минимальные накладные расходы на синхронизацию
- Эффективное распределение работы между потоками

## Тестовые функции (Test Functions)

### 1. f(x) = x² на [0, 1]
- Точное значение: 1/3 ≈ 0.333333
- Простая полиномиальная функция

### 2. f(x) = sin(x) на [0, π]
- Точное значение: 2.0
- Тригонометрическая функция

### 3. f(x) = 1/(1+x²) на [0, 1]
- Точное значение: π/4 ≈ 0.785398
- Производная arctangent

### 4. f(x) = eˣ на [0, 1]
- Точное значение: e - 1 ≈ 1.718282
- Экспоненциальная функция

### 5. f(x) = √(1-x²) на [0, 1]
- Точное значение: π/4 ≈ 0.785398
- Четверть окружности

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

1. **execution_time_*.png** - Время выполнения vs количество потоков
2. **speedup_*.png** - Ускорение vs количество потоков (с идеальной линией)
3. **efficiency_*.png** - Эффективность vs количество потоков
4. **size_comparison_*.png** - Сравнение производительности для разных размеров
5. **scalability_analysis_*.png** - Анализ масштабируемости
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

## Устранение проблем (Troubleshooting)

### Ошибка компиляции на macOS

```bash
# Установите GCC
brew install gcc

# Или libomp для Clang
brew install libomp
```

### Python библиотеки не найдены

```bash
pip3 install --user pandas matplotlib numpy
```

### Программа работает медленно

- Уменьшите размеры задач в `scripts/run_benchmarks.sh`
- Уменьшите количество запусков (RUNS=3 вместо 10)
- Используйте меньше потоков

### Неточные результаты интегрирования

- Увеличьте N (количество разбиений)
- Проверьте границы интегрирования
- Используйте double precision

## Ожидаемые результаты (Expected Results)

### Для малых размеров (N = 10⁶)
- Максимальное ускорение: 4-6x при 4-8 потоках
- Эффективность снижается при >8 потоках
- Накладные расходы на синхронизацию заметны

### Для средних размеров (N = 10⁷)
- Максимальное ускорение: 6-8x при 8-16 потоках
- Лучшая масштабируемость
- Оптимальный баланс вычислений/синхронизации

### Для больших размеров (N = 10⁸)
- Максимальное ускорение: 8-12x при 16-64 потоках
- Наилучшая масштабируемость
- Минимальные относительные накладные расходы

## Для отчета (For Report)

Используйте следующие материалы:

1. **Графики ускорения** - показывают эффективность параллелизации
2. **Графики эффективности** - демонстрируют качество масштабирования
3. **Сравнение размеров задач** - влияние размера на производительность
4. **Таблица summary_table.txt** - числовые данные для отчета
5. **Анализ масштабируемости** - strong scaling analysis

## Ключевые выводы (Key Findings)

1. Метод прямоугольников отлично параллелится с помощью OpenMP reduction
2. Размер задачи существенно влияет на эффективность параллелизации
3. OpenMP reduction обеспечивает оптимальную производительность
4. Накладные расходы растут с увеличением количества потоков
5. Оптимальное количество потоков зависит от размера задачи
6. Для малых задач параллелизация может быть неэффективна

## Математическая точность (Mathematical Accuracy)

Программа включает проверку корректности:
- Сравнение с точными значениями интегралов
- Относительная погрешность < 10⁻⁶
- Проверка параллельного метода против последовательного

## Автор (Author)

Задание выполнено в рамках курса "Введение в суперкомпьютерные вычисления"

## Лицензия (License)

Учебный проект