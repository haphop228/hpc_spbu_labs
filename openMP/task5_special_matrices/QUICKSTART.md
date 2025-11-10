# Quick Start Guide - Task 5: Special Matrices with OpenMP Scheduling

## Быстрый старт (Quick Start)

### 1. Компиляция программы (Compile the program)

```bash
cd task5_special_matrices/scripts
chmod +x *.sh
./compile.sh
```

Скрипт автоматически:
- Определит вашу ОС (macOS/Linux)
- Установит необходимые зависимости (libomp для macOS)
- Скомпилирует программу с оптимизациями
- Проверит работу OpenMP

### 2. Быстрый тест (Quick test)

```bash
./test_pipeline.sh
```

Это выполнит:
- Компиляцию
- Проверку корректности
- Быстрый бенчмарк
- Проверку Python зависимостей

### 3. Запуск полных бенчмарков (Run full benchmarks)

```bash
./run_benchmarks.sh
```

Это запустит полный набор тестов:
- Размеры матриц: 500×500, 1000×1000, 2000×2000, 3000×3000
- Типы матриц: banded, lower, upper
- Количество потоков: 1, 2, 4, 8, 16, 32, 64, 128
- Стратегии: static, dynamic, guided
- Размеры chunk: 0 (default), 10, 50
- По 10 запусков каждой конфигурации

⏱️ **Время выполнения:** ~20-40 минут в зависимости от системы

### 4. Анализ результатов (Analyze results)

```bash
cd ../analysis
python3 analyze.py ../results/benchmark_YYYYMMDD_HHMMSS.csv
```

Замените `YYYYMMDD_HHMMSS` на имя файла, созданного в шаге 3.

Скрипт выведет:
- Таблицу с временем выполнения
- Ускорение (speedup)
- Эффективность (efficiency)
- Сравнение стратегий планирования
- Сравнение типов матриц

### 5. Построение графиков (Generate graphs)

```bash
python3 plot_graphs.py
```

Графики будут сохранены в `../graphs/`:
- `execution_time_[type]_size_*.png` - время выполнения vs потоки
- `speedup_[type]_size_*.png` - ускорение vs потоки (с идеальной линией)
- `efficiency_[type]_size_*.png` - эффективность vs потоки
- `schedule_comparison.png` - сравнение стратегий планирования
- `matrix_type_comparison.png` - сравнение типов матриц
- `summary_table.txt` - сводная таблица

## Быстрый тест вручную (Quick Manual Test)

Для быстрой проверки работы программы:

```bash
cd task5_special_matrices

# Ленточная матрица 1000×1000, bandwidth=10, 4 потока, static
./bin/special_matrices 1000 banded 10 4 static 0 5

# Нижнетреугольная матрица 2000×2000, 8 потоков, dynamic
./bin/special_matrices 2000 lower 0 8 dynamic 10 3

# Верхнетреугольная матрица 3000×3000, 16 потоков, guided
./bin/special_matrices 3000 upper 0 16 guided 0 3
```

## Структура результатов (Results Structure)

```
results/
├── benchmark_YYYYMMDD_HHMMSS.csv          # Сырые данные
└── benchmark_YYYYMMDD_HHMMSS_processed.csv # Обработанные данные

graphs/
├── execution_time_banded_size_500.png
├── execution_time_banded_size_1000.png
├── execution_time_banded_size_2000.png
├── execution_time_banded_size_3000.png
├── execution_time_lower_size_*.png
├── execution_time_upper_size_*.png
├── speedup_banded_size_*.png
├── speedup_lower_size_*.png
├── speedup_upper_size_*.png
├── efficiency_banded_size_*.png
├── efficiency_lower_size_*.png
├── efficiency_upper_size_*.png
├── schedule_comparison.png
├── matrix_type_comparison.png
└── summary_table.txt
```

## Параметры программы (Program Parameters)

```bash
./bin/special_matrices <N> <matrix_type> <bandwidth> <num_threads> <schedule> <chunk_size> <iterations> [output_file]
```

- `N` - размер матрицы (NxN)
- `matrix_type` - тип матрицы: dense, banded, lower, upper
- `bandwidth` - ширина ленты для banded (игнорируется для других)
- `num_threads` - количество потоков OpenMP
- `schedule` - стратегия: static, dynamic, guided
- `chunk_size` - размер chunk (0 = default)
- `iterations` - количество запусков для усреднения
- `output_file` - (опционально) файл для сохранения результатов

## Типы матриц (Matrix Types)

### Banded (Ленточная)
```
[x x x 0 0 0]
[x x x x 0 0]
[x x x x x 0]
[0 x x x x x]
[0 0 x x x x]
[0 0 0 x x x]
```
- Неравномерная нагрузка по строкам
- Хороший тест для разных стратегий

### Lower Triangular (Нижнетреугольная)
```
[x 0 0 0 0 0]
[x x 0 0 0 0]
[x x x 0 0 0]
[x x x x 0 0]
[x x x x x 0]
[x x x x x x]
```
- Сильно неравномерная нагрузка
- Первые строки быстрые, последние медленные

### Upper Triangular (Верхнетреугольная)
```
[x x x x x x]
[0 x x x x x]
[0 0 x x x x]
[0 0 0 x x x]
[0 0 0 0 x x]
[0 0 0 0 0 x]
```
- Обратная неравномерность
- Первые строки медленные, последние быстрые

## Стратегии планирования (Scheduling Strategies)

### Static
- Равномерное распределение при запуске
- Минимальные накладные расходы
- Лучше для равномерной нагрузки

### Dynamic
- Динамическое распределение во время выполнения
- Автоматическая балансировка
- Лучше для неравномерной нагрузки

### Guided
- Размер chunk уменьшается экспоненциально
- Компромисс между static и dynamic
- Хорошо для постепенно меняющейся нагрузки

## Требования (Requirements)

### Система (System)
- macOS или Linux
- Компилятор с поддержкой OpenMP (gcc или clang+libomp)
- Python 3.6+

### Python библиотеки (Python packages)
```bash
pip3 install pandas matplotlib numpy
```

## Устранение проблем (Troubleshooting)

### Ошибка компиляции на macOS
```bash
# Установите GCC с OpenMP
brew install gcc

# Или libomp для Clang
brew install libomp
```

### Python библиотеки не найдены
```bash
pip3 install --user pandas matplotlib numpy
```

### Программа работает медленно
- Уменьшите размеры матриц в `scripts/run_benchmarks.sh`
- Уменьшите количество запусков (RUNS=3 вместо 10)
- Используйте меньше потоков

## Что дальше? (Next Steps)

1. Изучите сгенерированные графики в `graphs/`
2. Проанализируйте `summary_table.txt`
3. Обратите внимание на:
   - Как разные стратегии планирования влияют на производительность
   - Различия между типами матриц
   - Влияние chunk_size на балансировку нагрузки
   - Эффективность при разном количестве потоков
   - Масштабируемость решения

## Для отчета (For Report)

Используйте следующие графики:
1. **Speedup graphs** - показывают эффективность разных стратегий
2. **Efficiency graphs** - показывают качество масштабирования
3. **Schedule comparison** - сравнение static/dynamic/guided
4. **Matrix type comparison** - влияние структуры матрицы
5. **Summary table** - числовые данные для таблиц в отчете

Ключевые выводы для отчета:
- Какая стратегия лучше для каждого типа матрицы?
- Как неравномерность нагрузки влияет на выбор стратегии?
- Какое влияние оказывает chunk_size?
- Достигается ли линейное ускорение?
- Какие накладные расходы на разные стратегии?

## Примеры результатов (Example Results)

### Ожидаемое поведение:

**Ленточные матрицы:**
- Static: хорошо, но может быть дисбаланс
- Dynamic: отличная балансировка
- Guided: оптимальный компромисс

**Треугольные матрицы:**
- Static: плохая балансировка, низкая эффективность
- Dynamic: значительно лучше
- Guided: хорошая производительность

**Влияние chunk_size:**
- Малый (10): лучшая балансировка, больше overhead
- Большой (50): меньше overhead, хуже балансировка
- Default (0): OpenMP выбирает оптимальный

## Проверка корректности (Correctness Verification)

Программа автоматически проверяет точность вычислений:

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

✅ Все стратегии дают корректные и согласованные результаты!

## Дополнительная информация (Additional Information)

Полная документация: см. [README.md](README.md)

Формула задачи:
```
y = max(min(a_ij)) для i=1..N, j=1..N
```

Применение: поиск нижней цены игры в теории матричных игр.

## Математическая интерпретация (Mathematical Interpretation)

**Задача maximin** (максимин):
1. Для каждой строки матрицы находим минимальный элемент
2. Среди всех минимумов находим максимальный

**Применение в теории игр:**
- Игрок выбирает стратегию, максимизирующую минимальный выигрыш
- Гарантирует защиту от худшего случая
- Используется для поиска оптимальных стратегий

**Пример:**
```
Матрица:  [5  3  7]
          [2  8  1]
          [6  4  9]

Минимумы строк: [3, 1, 4]
Максимум из минимумов: 4
```

## Особенности Task 5 (Task 5 Features)

**Отличия от Task 4:**
1. ✅ Специальные типы матриц (banded, triangular)
2. ✅ Неравномерная вычислительная нагрузка
3. ✅ Сравнение стратегий планирования (static, dynamic, guided)
4. ✅ Анализ влияния chunk_size
5. ✅ Демонстрация важности балансировки нагрузки

**Ключевые инсайты:**
- Правильный выбор стратегии критичен для производительности
- Структура данных определяет оптимальную стратегию
- Балансировка нагрузки важнее минимизации overhead