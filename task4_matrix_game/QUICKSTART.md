# Quick Start Guide - Task 4: Matrix Game (Maximin Problem)

## Быстрый старт (Quick Start)

### 1. Компиляция программы (Compile the program)

```bash
cd task4_matrix_game/scripts
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
- Размеры матриц: 100×100, 500×500, 1000×1000, 2000×2000, 3000×3000
- Количество потоков: 1, 2, 4, 8, 16, 32, 64, 128
- Метод: OpenMP reduction
- По 10 запусков каждой конфигурации

⏱️ **Время выполнения:** ~15-30 минут в зависимости от системы

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
- Сравнение методов

### 5. Построение графиков (Generate graphs)

```bash
python3 plot_graphs.py
```

Графики будут сохранены в `../graphs/`:
- `execution_time_size_*.png` - время выполнения vs потоки
- `speedup_size_*.png` - ускорение vs потоки (с идеальной линией)
- `efficiency_size_*.png` - эффективность vs потоки
- `method_comparison.png` - сравнение методов
- `scalability_analysis.png` - анализ масштабируемости
- `summary_table.txt` - сводная таблица

## Быстрый тест вручную (Quick Manual Test)

Для быстрой проверки работы программы:

```bash
cd task4_matrix_game

# Матрица 1000×1000, 4 потока, метод reduction, 5 запусков
./bin/matrix_game 1000 4 reduction 5

# Матрица 2000×2000, 8 потоков, reduction
./bin/matrix_game 2000 8 reduction 3

# Матрица 3000×3000, 16 потоков, reduction
./bin/matrix_game 3000 16 reduction 3
```

## Структура результатов (Results Structure)

```
results/
├── benchmark_YYYYMMDD_HHMMSS.csv          # Сырые данные
└── benchmark_YYYYMMDD_HHMMSS_processed.csv # Обработанные данные

graphs/
├── execution_time_size_100.png
├── execution_time_size_500.png
├── execution_time_size_1000.png
├── execution_time_size_2000.png
├── execution_time_size_3000.png
├── speedup_size_100.png
├── speedup_size_500.png
├── speedup_size_1000.png
├── speedup_size_2000.png
├── speedup_size_3000.png
├── efficiency_size_100.png
├── efficiency_size_500.png
├── efficiency_size_1000.png
├── efficiency_size_2000.png
├── efficiency_size_3000.png
├── size_comparison.png
├── scalability_analysis.png
└── summary_table.txt
```

## Параметры программы (Program Parameters)

```bash
./bin/matrix_game <N> <num_threads> <method> <iterations> [output_file]
```

- `N` - размер матрицы (NxN)
- `num_threads` - количество потоков OpenMP
- `method` - метод: sequential, reduction, critical, atomic
- `iterations` - количество запусков для усреднения
- `output_file` - (опционально) файл для сохранения результатов

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
   - Ускорение при увеличении потоков
   - Эффективность параллелизации
   - Влияние размера матрицы на производительность
   - Масштабируемость решения
   - Эффективность OpenMP reduction

## Для отчета (For Report)

Используйте следующие графики:
1. **Speedup graphs** - показывают эффективность параллелизации
2. **Efficiency graphs** - показывают качество масштабирования
3. **Size comparison** - сравнение производительности для разных размеров
4. **Scalability analysis** - анализ масштабируемости
5. **Summary table** - числовые данные для таблиц в отчете

Ключевые выводы для отчета:
- Как масштабируется производительность с ростом потоков?
- Достигается ли линейное ускорение?
- Как размер матрицы влияет на эффективность?
- Какие накладные расходы на параллелизацию?
- Насколько эффективна OpenMP reduction для данной задачи?

## Примеры результатов (Example Results)

### Ожидаемое ускорение:
- **100×100**: 2-4x при 4-8 потоках
- **1000×1000**: 4-8x при 8-16 потоках
- **3000×3000**: 8-16x при 16-32 потоках

### Производительность OpenMP Reduction:
- Оптимальная производительность благодаря встроенным оптимизациям
- Минимальные накладные расходы на синхронизацию
- Эффективное распределение работы между потоками

## Проверка корректности (Correctness Verification)

Программа автоматически проверяет точность вычислений:

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

✅ Оба метода дают корректные и согласованные результаты!

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