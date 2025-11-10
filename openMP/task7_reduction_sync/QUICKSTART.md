# Quick Start Guide - Task 7: Reduction Synchronization

## Быстрый запуск за 3 шага

### Шаг 1: Компиляция
```bash
cd task7_reduction_sync/scripts
chmod +x *.sh
./compile.sh
```

### Шаг 2: Быстрый тест
```bash
./test_pipeline.sh
```

### Шаг 3: Полный бенчмарк
```bash
./run_benchmarks.sh
```

## Анализ результатов

```bash
cd ../analysis
python3 analyze.py ../results/benchmark_*.csv
python3 plot_graphs.py
```

Графики будут в директории `graphs/`

## Примеры запуска

```bash
# Последовательное выполнение
./bin/reduction_sync 10000000 1 sequential 10

# Встроенная редукция (самый быстрый)
./bin/reduction_sync 10000000 8 builtin 10

# Атомарные операции
./bin/reduction_sync 10000000 8 atomic 10

# Критические секции
./bin/reduction_sync 10000000 8 critical 10

# Замки
./bin/reduction_sync 10000000 8 lock 10
```

## Что тестируется

- **4 метода синхронизации**: builtin, atomic, critical, lock
- **3 размера массивов**: 1M, 10M, 100M элементов
- **8 конфигураций потоков**: 1, 2, 4, 8, 16, 32, 64, 128

## Ожидаемые результаты

- **builtin** - самый быстрый (baseline)
- **atomic** - 2-5x медленнее
- **critical** - 5-20x медленнее
- **lock** - 5-20x медленнее

## Время выполнения

- Быстрый тест: ~1 минута
- Полный бенчмарк: ~20-40 минут

## Требования

- GCC с OpenMP или Clang с libomp
- Python 3 с pandas, matplotlib, numpy
- Минимум 4 ядра CPU