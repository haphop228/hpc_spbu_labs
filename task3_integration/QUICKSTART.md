# Quick Start Guide - Task 3: Numerical Integration with OpenMP

## Быстрый старт (Quick Start)

### 1. Компиляция программы (Compile the program)

```bash
cd task3_integration/scripts
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
- Размеры задач: 10⁶, 10⁷, 10⁸ разбиений
- Количество потоков: 1, 2, 4, 8, 16, 32, 64, 128
- Метод: OpenMP reduction
- Функции: x², sin(x), 1/(1+x²)
- По 10 запусков каждой конфигурации

⏱️ **Время выполнения:** ~10-20 минут в зависимости от системы

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

### 5. Построение графиков (Generate graphs)

```bash
python3 plot_graphs.py
```

Графики будут сохранены в `../graphs/`:
- `execution_time_*.png` - время выполнения vs потоки
- `speedup_*.png` - ускорение vs потоки (с идеальной линией)
- `efficiency_*.png` - эффективность vs потоки
- `size_comparison_*.png` - сравнение размеров задач
- `scalability_analysis_*.png` - анализ масштабируемости
- `summary_table.txt` - сводная таблица

## Быстрый тест вручную (Quick Manual Test)

Для быстрой проверки работы программы:

```bash
cd task3_integration

# Интеграл x² от 0 до 1, 4 потока, метод reduction, 5 запусков
./bin/integration x2 0 1 1000000 4 reduction 5

# Интеграл sin(x) от 0 до π, 8 потоков
./bin/integration sin 0 3.14159 10000000 8 reduction 3

# Интеграл 1/(1+x²) от 0 до 1, 16 потоков
./bin/integration arctan 0 1 100000000 16 reduction 3
```

## Структура результатов (Results Structure)

```
results/
├── benchmark_YYYYMMDD_HHMMSS.csv          # Сырые данные
└── benchmark_YYYYMMDD_HHMMSS_processed.csv # Обработанные данные

graphs/
├── execution_time_x2_size_1000000.png
├── execution_time_x2_size_10000000.png
├── execution_time_x2_size_100000000.png
├── speedup_x2_size_1000000.png
├── speedup_x2_size_10000000.png
├── speedup_x2_size_100000000.png
├── efficiency_x2_size_1000000.png
├── efficiency_x2_size_10000000.png
├── efficiency_x2_size_100000000.png
├── size_comparison_x2.png
├── scalability_analysis_x2.png
└── summary_table.txt
```

## Параметры программы (Program Parameters)

```bash
./bin/integration <function> <a> <b> <N> <threads> <method> <runs> [output]
```

- `function` - функция: x2, sin, exp, arctan, circle
- `a` - нижняя граница интегрирования
- `b` - верхняя граница интегрирования
- `N` - количество разбиений (шагов)
- `threads` - количество потоков OpenMP
- `method` - метод: sequential, reduction
- `runs` - количество запусков для усреднения
- `output` - (опционально) файл для сохранения результатов

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
- Уменьшите размеры задач в `scripts/run_benchmarks.sh`
- Уменьшите количество запусков (RUNS=3 вместо 10)
- Используйте меньше потоков

## Что дальше? (Next Steps)

1. Изучите сгенерированные графики в `graphs/`
2. Проанализируйте `summary_table.txt`
3. Обратите внимание на:
   - Ускорение при увеличении потоков
   - Эффективность параллелизации
   - Влияние размера задачи на производительность
   - Масштабируемость решения

## Для отчета (For Report)

Используйте следующие графики:
1. **Speedup graphs** - показывают эффективность параллелизации
2. **Efficiency graphs** - показывают качество масштабирования
3. **Size comparison** - влияние размера задачи
4. **Summary table** - числовые данные для таблиц в отчете

Ключевые выводы для отчета:
- Как масштабируется производительность с ростом потоков?
- Достигается ли линейное ускорение?
- Как размер задачи влияет на эффективность?
- Какие накладные расходы на параллелизацию?

## Примеры результатов (Example Results)

### Ожидаемое ускорение:
- **N = 10⁶**: 4-6x при 8 потоках
- **N = 10⁷**: 6-8x при 16 потоках
- **N = 10⁸**: 8-12x при 32-64 потоках

### Производительность OpenMP Reduction:
- Оптимальная производительность благодаря встроенным оптимизациям
- Минимальные накладные расходы на синхронизацию
- Хорошая масштабируемость на больших задачах

## Дополнительная информация (Additional Information)

Полная документация: см. [README.md](README.md)

Формула метода прямоугольников:
```
y = ∫ₐᵇ f(x)dx ≈ h ∑ᵢ₌₀ᴺ⁻¹ fᵢ
где: fᵢ = f(xᵢ), xᵢ = ih, h = (b-a)/N
```

## Проверка корректности (Correctness Verification)

Программа автоматически проверяет точность вычислений:

```
Test 1: ∫₀¹ x² dx (exact = 0.333333)
  Sequential: 0.3333328333 (error: 0.0000005000)
  Reduction:  0.3333328333 (error: 0.0000005000)

Test 2: ∫₀^π sin(x) dx (exact = 2.0)
  Sequential: 2.0000000000 (error: 0.0000000000)
  Reduction:  2.0000000000 (error: 0.0000000000)

Test 3: ∫₀¹ 1/(1+x²) dx (exact = π/4 = 0.7853981634)
  Sequential: 0.7853984134 (error: 0.0000002500)
  Reduction:  0.7853984134 (error: 0.0000002500)
```

✅ Все методы дают корректные результаты с высокой точностью!