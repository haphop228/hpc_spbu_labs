# Quick Start Guide - Task 1: Min/Max with OpenMP

## Быстрый старт (Quick Start)

### 1. Компиляция программы (Compile the program)

```bash
cd HPC_korhov/task1_min_max/scripts
./compile.sh
```

Скрипт автоматически:
- Определит вашу ОС (macOS/Linux)
- Установит необходимые зависимости (libomp для macOS)
- Скомпилирует программу с оптимизациями
- Проверит работу OpenMP

### 2. Запуск бенчмарков (Run benchmarks)

```bash
./run_benchmarks.sh
```

Это запустит полный набор тестов:
- Размеры векторов: 10^6, 10^7, 10^8 элементов
- Количество потоков: 1, 2, 4, 8, 16, 32, 64, 128
- Методы: с редукцией и без редукции
- По 10 запусков каждой конфигурации

### 3. Анализ результатов (Analyze results)

```bash
cd ../analysis
python3 analyze.py ../results/benchmark_YYYYMMDD_HHMMSS.json
```

Замените `YYYYMMDD_HHMMSS` на имя файла, созданного в шаге 2.

Скрипт выведет:
- Таблицу с временем выполнения
- Ускорение (speedup)
- Эффективность (efficiency)

### 4. Построение графиков (Generate graphs)

```bash
python3 plot_graphs.py
```

Графики будут сохранены в `../report/`:
- `execution_time_size_*.png` - время выполнения vs количество потоков
- `speedup_size_*.png` - ускорение vs количество потоков (с идеальной линией)
- `efficiency_size_*.png` - эффективность vs количество потоков
- `comparison_reduction_methods.png` - сравнение методов
- `summary_table.txt` - сводная таблица

## Быстрый тест (Quick Test)

Для быстрой проверки работы программы:

```bash
cd HPC_korhov/task1_min_max

# Тест с редукцией, 4 потока, 100K элементов, 3 запуска
./bin/min_max 100000 4 reduction 3

# Тест без редукции, 2 потока, 100K элементов, 3 запуска
./bin/min_max 100000 2 no-reduction 3
```

## Структура результатов (Results Structure)

```
results/
├── benchmark_YYYYMMDD_HHMMSS.json          # Сырые данные
└── benchmark_YYYYMMDD_HHMMSS_processed.json # Обработанные данные

report/
├── execution_time_size_1000000.png
├── execution_time_size_10000000.png
├── execution_time_size_100000000.png
├── speedup_size_1000000.png
├── speedup_size_10000000.png
├── speedup_size_100000000.png
├── efficiency_size_1000000.png
├── efficiency_size_10000000.png
├── efficiency_size_100000000.png
├── comparison_reduction_methods.png
└── summary_table.txt
```

## Параметры программы (Program Parameters)

```bash
./bin/min_max <size> <threads> <method> <runs>
```

- `size` - размер вектора (количество элементов)
- `threads` - количество потоков OpenMP
- `method` - метод: `reduction` или `no-reduction`
- `runs` - количество запусков для усреднения

## Требования (Requirements)

### Система (System)
- macOS или Linux
- Компилятор с поддержкой OpenMP (gcc или clang+libomp)
- Python 3.6+

### Python библиотеки (Python packages)
```bash
pip3 install numpy matplotlib
```

## Устранение проблем (Troubleshooting)

### Ошибка компиляции на macOS
```bash
# Установите libomp вручную
brew install libomp
```

### Python библиотеки не найдены
```bash
pip3 install --user numpy matplotlib
```

### Программа работает медленно
- Уменьшите размеры векторов в `scripts/run_benchmarks.sh`
- Уменьшите количество запусков (RUNS=3 вместо 10)

## Что дальше? (Next Steps)

1. Изучите сгенерированные графики в `report/`
2. Проанализируйте `summary_table.txt`
3. Сравните результаты с редукцией и без
4. Обратите внимание на:
   - Ускорение при увеличении потоков
   - Эффективность параллелизации
   - Разницу между методами

## Для отчета (For Report)

Используйте следующие графики:
1. **Speedup graphs** - показывают эффективность параллелизации
2. **Comparison graph** - сравнение методов с/без редукции
3. **Summary table** - числовые данные для таблиц в отчете

Ключевые выводы для отчета:
- Как масштабируется производительность с ростом потоков?
- Достигается ли линейное ускорение?
- Какой метод эффективнее и почему?
- Как размер задачи влияет на эффективность?