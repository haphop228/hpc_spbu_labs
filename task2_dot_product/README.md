# Task 2: Dot Product Calculation with OpenMP

## Описание задачи (Task Description)

Разработка программы для вычисления скалярного произведения двух векторов с использованием OpenMP. Программа реализует два подхода:
1. С использованием встроенной редукции OpenMP (`reduction`)
2. С ручной аккумуляцией без редукции (`no-reduction`)

Implementation of parallel dot product calculation for two vectors using OpenMP with two approaches:
1. Using built-in OpenMP reduction
2. Manual accumulation without reduction

## Структура проекта (Project Structure)

```
task2_dot_product_v2/
├── src/                    # Исходный код
│   └── dot_product.cpp     # Основная программа с OpenMP
├── scripts/                # Скрипты автоматизации
│   ├── compile.sh          # Компиляция программы
│   ├── run_benchmarks.sh   # Запуск бенчмарков
│   └── test_pipeline.sh    # Полный тестовый пайплайн
├── data/                   # Конфигурации
│   └── test_configs.json   # Параметры тестирования
├── analysis/               # Скрипты анализа
│   ├── analyze.py          # Обработка результатов
│   └── plot_graphs.py      # Генерация графиков
├── bin/                    # Скомпилированные бинарники
├── results/                # Результаты бенчмарков (CSV)
├── graphs/                 # Сгенерированные графики
├── .gitignore             # Git ignore файл
└── README.md              # Этот файл
```

## Быстрый старт (Quick Start)

### 1. Компиляция (Compilation)

```bash
cd task2_dot_product_v2
./scripts/compile.sh
```

Скрипт автоматически:
- Определит вашу ОС (macOS/Linux)
- Найдет подходящий компилятор с поддержкой OpenMP
- Скомпилирует программу с оптимизациями
- Проверит работу OpenMP

### 2. Быстрый тест (Quick Test)

```bash
./scripts/test_pipeline.sh
```

Выполнит:
- Компиляцию программы
- Проверку корректности
- Быстрый бенчмарк
- Проверку зависимостей Python

### 3. Полный бенчмарк (Full Benchmark)

```bash
./scripts/run_benchmarks.sh
```

Запустит полный набор тестов:
- Размеры векторов: 10^6, 10^7, 10^8 элементов
- Количество потоков: 1, 2, 4, 8, 16, 32, 64, 128
- Методы: reduction и no-reduction
- По 10 запусков каждой конфигурации

### 4. Анализ результатов (Analysis)

```bash
# Обработка данных
python3 analysis/analyze.py results/benchmark_YYYYMMDD_HHMMSS.csv

# Генерация графиков
python3 analysis/plot_graphs.py
```

## Использование программы (Program Usage)

### Формат команды

```bash
./bin/dot_product <vector_size> <num_threads> <method> <iterations> [output_file]
```

### Параметры

- `vector_size` - размер векторов (количество элементов)
- `num_threads` - количество потоков OpenMP
- `method` - метод вычисления:
  - `reduction` - с использованием OpenMP reduction
  - `no-reduction` - с ручной аккумуляцией
- `iterations` - количество запусков для усреднения
- `output_file` - (опционально) файл для сохранения результатов

### Примеры

```bash
# Тест с редукцией, 4 потока, 1M элементов, 10 запусков
./bin/dot_product 1000000 4 reduction 10

# Тест без редукции, 8 потоков, 10M элементов, 5 запусков
./bin/dot_product 10000000 8 no-reduction 5

# С сохранением результатов в файл
./bin/dot_product 1000000 4 reduction 10 results/test.csv
```

## Реализация (Implementation)

### Метод с редукцией (Reduction Method)

```cpp
double dot_product_reduction(const std::vector<double>& a, 
                             const std::vector<double>& b, 
                             int num_threads) {
    double result = 0.0;
    size_t n = a.size();
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel for reduction(+:result)
    for (size_t i = 0; i < n; ++i) {
        result += a[i] * b[i];
    }
    
    return result;
}
```

**Преимущества:**
- Простая реализация
- Автоматическая оптимизация компилятором
- Меньше кода

### Метод без редукции (No-Reduction Method)

```cpp
double dot_product_no_reduction(const std::vector<double>& a, 
                                const std::vector<double>& b, 
                                int num_threads) {
    double result = 0.0;
    size_t n = a.size();
    
    omp_set_num_threads(num_threads);
    
    #pragma omp parallel
    {
        double local_sum = 0.0;
        
        #pragma omp for nowait
        for (size_t i = 0; i < n; ++i) {
            local_sum += a[i] * b[i];
        }
        
        #pragma omp critical
        {
            result += local_sum;
        }
    }
    
    return result;
}
```

**Преимущества:**
- Больше контроля над процессом
- Явное управление локальными суммами
- Возможность оптимизации критической секции

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
4. **comparison_methods.png** - Сравнение методов
5. **summary_table.txt** - Сводная таблица результатов

## Требования (Requirements)

### Система (System)
- macOS или Linux
- Компилятор с поддержкой OpenMP:
  - GCC 11+ (рекомендуется для macOS)
  - Clang с libomp
  - GCC на Linux

### Python (для анализа)
```bash
pip3 install pandas matplotlib numpy seaborn
```

## Установка зависимостей (Dependencies Installation)

### macOS

```bash
# Установка GCC с OpenMP (рекомендуется)
brew install gcc

# Или установка libomp для Clang
brew install libomp

# Python пакеты
pip3 install pandas matplotlib numpy seaborn
```

### Linux

```bash
# GCC обычно уже установлен
sudo apt-get update
sudo apt-get install g++

# Python пакеты
pip3 install pandas matplotlib numpy seaborn
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
pip3 install --user pandas matplotlib numpy seaborn
```

### Программа работает медленно

- Уменьшите размеры векторов в `scripts/run_benchmarks.sh`
- Уменьшите количество запусков (RUNS=3 вместо 10)
- Используйте меньше потоков

## Ожидаемые результаты (Expected Results)

### Для малых размеров (10^6 элементов)
- Максимальное ускорение: 4-6x при 4-8 потоках
- Эффективность снижается при >8 потоках

### Для средних размеров (10^7 элементов)
- Максимальное ускорение: 6-8x при 8-16 потоках
- Лучшая масштабируемость

### Для больших размеров (10^8 элементов)
- Максимальное ускорение: 7-10x при 16-64 потоках
- Наилучшая масштабируемость

## Для отчета (For Report)

Используйте следующие материалы:

1. **Графики ускорения** - показывают эффективность параллелизации
2. **График сравнения методов** - демонстрирует разницу подходов
3. **Таблица summary_table.txt** - числовые данные для отчета
4. **Графики эффективности** - показывают качество масштабирования

## Ключевые выводы (Key Findings)

1. Оба метода показывают хорошую масштабируемость
2. Размер задачи существенно влияет на эффективность
3. Метод с редукцией обычно быстрее благодаря оптимизациям компилятора
4. Накладные расходы растут с увеличением количества потоков
5. Оптимальное количество потоков зависит от размера задачи

## Автор (Author)

Задание выполнено в рамках курса "Введение в суперкомпьютерные вычисления"

## Лицензия (License)

Учебный проект