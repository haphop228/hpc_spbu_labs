# Quick Start Guide - Task 8: Vector Dot Products with OpenMP Sections

## Быстрый старт (Quick Start)

### 1. Компиляция программы (Compile the program)

```bash
cd task8_vector_dot_products_fixed/scripts
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
- Генерацию тестовых данных
- Проверку корректности
- Быстрый бенчмарк с анализом

### 3. Запуск полных бенчмарков (Run full benchmarks)

```bash
./run_benchmarks.sh
```

Это запустит полный набор тестов:
- Размеры векторов: 1000, 5000, 10000
- Количество пар: 10, 50, 100
- Количество потоков: 1, 2, 4, 8
- Методы: sequential, sections
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
- Анализ времени ввода vs вычислений
- Ключевые выводы

### 5. Построение графиков (Generate graphs)

```bash
python3 plot_graphs.py
```

Графики будут сохранены в `../graphs/`:
- `execution_time_*.png` - время выполнения vs потоки
- `speedup_*.png` - ускорение vs потоки (с идеальной линией)
- `efficiency_*.png` - эффективность vs потоки
- `time_breakdown.png` - разбивка времени на ввод и вычисления
- `sections_limitation.png` - демонстрация ограничения 2 секций
- `summary_table.txt` - сводная таблица

## Быстрый тест вручную (Quick Manual Test)

Для быстрой проверки работы программы:

```bash
cd task8_vector_dot_products_fixed

# Генерация тестовых данных: 50 пар векторов размером 10000
./bin/vector_dot_products generate 50 10000 data/test.txt

# Проверка корректности
./bin/vector_dot_products verify data/test.txt

# Полный бенчмарк (5 запусков)
./bin/vector_dot_products full data/test.txt 5

# Бенчмарк только sections с 2 потоками
./bin/vector_dot_products benchmark data/test.txt 2 sections 10
```

## Структура результатов (Results Structure)

```
results/
├── benchmark_YYYYMMDD_HHMMSS.csv          # Сырые данные
└── benchmark_YYYYMMDD_HHMMSS_processed.csv # Обработанные данные

graphs/
├── execution_time_pairs_10_size_1000.png
├── execution_time_pairs_50_size_5000.png
├── execution_time_pairs_100_size_10000.png
├── speedup_*.png
├── efficiency_*.png
├── time_breakdown.png
├── sections_limitation.png
└── summary_table.txt
```

## Команды программы (Program Commands)

```bash
./bin/vector_dot_products <command> [options]
```

### Доступные команды:

#### 1. generate - Генерация тестовых данных
```bash
./bin/vector_dot_products generate <num_pairs> <vector_size> <output_file>
```
Пример:
```bash
./bin/vector_dot_products generate 100 5000 vectors.txt
```

#### 2. benchmark - Запуск бенчмарка
```bash
./bin/vector_dot_products benchmark <data_file> <num_threads> <method> <runs>
```
- `method`: sequential или sections
- `runs`: количество запусков для усреднения

Пример:
```bash
./bin/vector_dot_products benchmark vectors.txt 2 sections 10
```

#### 3. full - Полный бенчмарк с анализом
```bash
./bin/vector_dot_products full <data_file> <runs>
```
Сравнивает sequential и sections (2 потока), выводит детальный анализ.

Пример:
```bash
./bin/vector_dot_products full vectors.txt 5
```

#### 4. verify - Проверка корректности
```bash
./bin/vector_dot_products verify <data_file>
```
Проверяет, что параллельная версия дает те же результаты, что и последовательная.

Пример:
```bash
./bin/vector_dot_products verify vectors.txt
```

## Понимание результатов (Understanding Results)

### Пример вывода команды `full`:

```
============================================================
FULL BENCHMARK COMPARISON
============================================================

Dataset: 50 pairs, vector size 10000

Method               Total (ms)      Input (ms)      Compute (ms)
------------------------------------------------------------
Sequential           2450.23         125.45          2324.78
Sections (2 thr)     1850.67         125.45          1725.22

------------------------------------------------------------
SPEEDUP ANALYSIS
------------------------------------------------------------
Speedup:    1.32x
Efficiency: 66.2%

Theoretical maximum speedup (pipeline): 1.95x
(Based on overlapping I/O and computation)
```

### Интерпретация:

- **Speedup 1.32x**: Программа работает в 1.32 раза быстрее с 2 потоками
- **Efficiency 66.2%**: Эффективность использования потоков 66%
- **Theoretical max 1.95x**: Теоретический максимум при идеальном перекрытии I/O и вычислений

### Почему не 2x speedup?

1. **Синхронизация**: Накладные расходы на locks и atomic операции
2. **Дисбаланс нагрузки**: Одна секция может работать быстрее другой
3. **Busy-waiting**: Consumer ждет данных от Producer
4. **Memory contention**: Конкуренция за доступ к памяти

## Ключевые концепции (Key Concepts)

### OpenMP Sections

```cpp
#pragma omp parallel sections
{
    #pragma omp section  // Секция 1
    {
        // Задача 1: Чтение данных
    }
    
    #pragma omp section  // Секция 2
    {
        // Задача 2: Вычисления
    }
}
```

**Важно**: 
- Создается ровно **2 параллельные задачи**
- Оптимальное количество потоков = **2**
- Дополнительные потоки (4, 8) дают минимальное улучшение

### Producer-Consumer Pattern

- **Producer (Section 1)**: Читает векторы → помещает в очередь
- **Consumer (Section 2)**: Берет из очереди → вычисляет
- **Синхронизация**: Thread-safe queue + atomic flags

### Thread-Safe Queue

```cpp
class ThreadSafeQueue {
    queue<VectorPair> q;
    omp_lock_t lock;  // OpenMP lock для синхронизации
    
    void push(const VectorPair& item);
    bool try_pop(VectorPair& item);
};
```

## Требования (Requirements)

### Система (System)
- macOS или Linux
- Компилятор с поддержкой OpenMP (gcc или clang+libomp)
- Минимум 2 ядра CPU
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
- Уменьшите размеры векторов в `scripts/run_benchmarks.sh`
- Уменьшите количество запусков (RUNS=3 вместо 10)
- Используйте меньше конфигураций

### Нет ускорения
Это нормально! Ускорение ограничено:
- Максимум ~1.3-1.5x с 2 потоками
- Минимальное улучшение с 4+ потоками
- Это демонстрирует ограничение директивы `sections`

## Что дальше? (Next Steps)

1. Изучите сгенерированные графики в `graphs/`
2. Проанализируйте `summary_table.txt`
3. Обратите внимание на:
   - Ограничение 2 секций (график `sections_limitation.png`)
   - Разбивку времени на I/O и вычисления
   - Эффективность при разном количестве потоков
   - Почему дополнительные потоки не помогают

## Для отчета (For Report)

Используйте следующие графики:

1. **sections_limitation.png** - ключевой график, показывающий ограничение
2. **speedup_*.png** - демонстрирует реальное vs идеальное ускорение
3. **efficiency_*.png** - показывает падение эффективности при >2 потоках
4. **time_breakdown.png** - показывает параллельное выполнение секций
5. **summary_table.txt** - числовые данные для таблиц

### Ключевые выводы для отчета:

1. ✅ Директива `sections` создает фиксированное число параллельных задач
2. ✅ Оптимальное количество потоков = количество секций (2 в нашем случае)
3. ✅ Producer-Consumer pattern эффективен для pipeline-обработки
4. ✅ Дополнительные потоки не улучшают производительность значительно
5. ✅ Thread-safe синхронизация критична для корректности

### Сравнение с другими подходами:

| Подход | Количество задач | Когда использовать |
|--------|------------------|-------------------|
| `sections` | Фиксированное (2-4) | Разнородные задачи, pipeline |
| `parallel for` | Динамическое | Однородные итерации |
| `task` | Динамическое | Рекурсивные алгоритмы |

## Примеры результатов (Example Results)

### Ожидаемое поведение:

**С 2 потоками (оптимально):**
- Speedup: ~1.2-1.5x
- Efficiency: ~60-75%
- Обе секции работают параллельно

**С 4 потоками:**
- Speedup: ~1.3-1.6x (незначительное улучшение)
- Efficiency: ~30-40% (падает)
- 2 потока простаивают

**С 8 потоками:**
- Speedup: ~1.3-1.7x (минимальное улучшение)
- Efficiency: ~15-20% (сильно падает)
- 6 потоков простаивают

## Проверка корректности (Correctness Verification)

Программа автоматически проверяет точность вычислений:

```
=== Correctness Verification ===
Sequential results (first 5):
  Pair 0: 249875000.000000
  Pair 1: 249875000.000000
  ...

Parallel (sections) results (first 5):
  Pair 0: 249875000.000000
  Pair 1: 249875000.000000
  ...

✓ PASSED: All results match!
```

✅ Обе версии дают идентичные результаты!

## Дополнительная информация (Additional Information)

Полная документация: см. [README.md](README.md)

### Математическая формула:
```
dot_product(a, b) = Σ(a[i] * b[i]) для i=0..n-1
```

### Применение:
- Линейная алгебра
- Машинное обучение (нейронные сети)
- Компьютерная графика (освещение)
- Обработка сигналов

### Особенности Task 8:

1. ✅ Использование директивы `sections` для параллелизма
2. ✅ Producer-Consumer pattern с thread-safe queue
3. ✅ Демонстрация ограничений sections (фиксированное число задач)
4. ✅ Анализ pipeline-параллелизма
5. ✅ Сравнение с последовательной версией

## Контакты и поддержка (Support)

Если возникли проблемы:
1. Проверьте `QUICKSTART.md` и `README.md`
2. Убедитесь, что все зависимости установлены
3. Проверьте вывод `./compile.sh` на ошибки
4. Попробуйте запустить `./test_pipeline.sh` для диагностики