# Task 8: Vector Dot Products with OpenMP Sections

## Описание задачи (Task Description)

Разработка программы для вычисления скалярного произведения для последовательного набора векторов. Ввод векторов и вычисление их произведения организованы как две раздельные задачи, для распараллеливания которых используется директива `sections`.

**Implementation of dot product computation for a sequence of vector pairs using OpenMP sections directive:**
- Input task: Reading vectors from file
- Computation task: Computing dot products
- Parallelization using `#pragma omp parallel sections`

## Структура проекта (Project Structure)

```
task8_vector_dot_products/
├── src/                          # Source code
│   └── vector_dot_products.cpp   # Main program with sections
├── scripts/                      # Automation scripts
│   ├── compile.sh                # Compilation script
│   ├── run_benchmarks.sh         # Benchmark runner
│   └── test_pipeline.sh          # Full test pipeline
├── data/                         # Vector data files
│   └── *.txt                     # Generated vector pairs
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
cd task8_vector_dot_products/scripts
chmod +x *.sh
./compile.sh
```

Скрипт автоматически:
- Определит вашу ОС (macOS/Linux)
- Найдет подходящий компилятор с поддержкой OpenMP
- Скомпилирует программу с оптимизациями
- Сгенерирует тестовые данные
- Проверит корректность работы

### 2. Быстрый тест (Quick Test)

```bash
./test_pipeline.sh
```

Выполнит:
- Компиляцию программы
- Генерацию тестовых данных
- Проверку корректности вычислений
- Быстрый бенчмарк
- Проверку зависимостей Python

### 3. Полный бенчмарк (Full Benchmark)

```bash
./run_benchmarks.sh
```

Запустит полный набор тестов:
- Количество пар векторов: 50, 100, 200, 500
- Размер векторов: 1000, 5000, 10000 элементов
- Количество потоков: 1, 2, 4, 8, 16, 32, 64, 128
- По 10 запусков каждой конфигурации

⏱️ **Время выполнения:** ~15-30 минут в зависимости от системы

### 4. Анализ результатов (Analysis)

```bash
cd ../analysis

# Обработка данных
python3 analyze.py ../results/benchmark_YYYYMMDD_HHMMSS.csv

# Генерация графиков
python3 plot_graphs.py
```

## Использование программы (Program Usage)

### Генерация тестовых данных

```bash
./bin/vector_dot_products generate <num_pairs> <vector_size> <output_file>
```

Пример:
```bash
./bin/vector_dot_products generate 100 1000 data/vectors.txt
```

### Запуск бенчмарка

```bash
./bin/vector_dot_products benchmark <data_file> <num_threads> <method> <runs> [output_file]
```

Параметры:
- `data_file` - файл с векторами
- `num_threads` - количество потоков OpenMP
- `method` - метод: `sequential` или `sections`
- `runs` - количество запусков для усреднения
- `output_file` - (опционально) CSV файл для сохранения результатов

Примеры:
```bash
# Последовательное выполнение (baseline)
./bin/vector_dot_products benchmark data/vectors.txt 1 sequential 10

# Параллельное выполнение с sections, 4 потока
./bin/vector_dot_products benchmark data/vectors.txt 4 sections 10

# С сохранением результатов
./bin/vector_dot_products benchmark data/vectors.txt 8 sections 10 results/test.csv
```

### Проверка корректности

```bash
./bin/vector_dot_products verify <data_file>
```

## Реализация (Implementation)

### Формат данных

Файл с векторами имеет следующий формат:
```
<num_pairs> <vector_size>
<vec1_elem1> <vec1_elem2> ... <vec1_elemN>
<vec2_elem1> <vec2_elem2> ... <vec2_elemN>
<vec3_elem1> <vec3_elem2> ... <vec3_elemN>
<vec4_elem1> <vec4_elem2> ... <vec4_elemN>
...
```

Каждая пара векторов занимает две строки.

### Последовательная реализация (Sequential)

```cpp
// 1. Чтение всех векторов из файла
for (int p = 0; p < num_pairs; ++p) {
    read_vector_pair(file, pairs[p]);
}

// 2. Вычисление всех скалярных произведений
for (int p = 0; p < num_pairs; ++p) {
    results[p] = compute_dot_product(pairs[p].vec1, pairs[p].vec2);
}
```

### Параллельная реализация с sections

```cpp
#pragma omp parallel sections
{
    // Section 1: Задача ввода - чтение векторов из файла
    #pragma omp section
    {
        for (int p = 0; p < num_pairs; ++p) {
            VectorPair pair = read_vector_pair(file, p);
            
            #pragma omp critical
            {
                compute_buffer.push_back(pair);
            }
        }
        input_done = true;
    }
    
    // Section 2: Задача вычисления - вычисление скалярных произведений
    #pragma omp section
    {
        while (processed < num_pairs) {
            VectorPair pair;
            
            #pragma omp critical
            {
                if (!compute_buffer.empty()) {
                    pair = compute_buffer.front();
                    compute_buffer.erase(compute_buffer.begin());
                }
            }
            
            if (has_work) {
                results[pair.id] = compute_dot_product(pair.vec1, pair.vec2);
                processed++;
            }
        }
    }
}
```

**Ключевые особенности:**
- Две независимые секции выполняются параллельно
- Секция ввода читает векторы и помещает их в буфер
- Секция вычисления берет векторы из буфера и вычисляет скалярные произведения
- Синхронизация через критические секции для доступа к общему буферу
- Конвейерная обработка: вычисления начинаются до завершения ввода

## Проверка корректности (Correctness Verification)

Программа автоматически проверяет корректность:

```
=== Correctness Verification ===
Sequential results:
  Pair 0: 123456.789012
  Pair 1: 234567.890123
  ...

Parallel (sections) results:
  Pair 0: 123456.789012
  Pair 1: 234567.890123
  ...

✓ PASSED: All results match!
```

## Метрики производительности (Performance Metrics)

### 1. Время выполнения (Execution Time)
- **Total time** - общее время выполнения
- **Input time** - время чтения векторов
- **Computation time** - время вычисления скалярных произведений

### 2. Ускорение (Speedup)
```
Speedup = T(sequential) / T(parallel)
```

### 3. Эффективность (Efficiency)
```
Efficiency = Speedup / n
```
где n - количество потоков.

## Генерируемые графики (Generated Graphs)

После запуска анализа в директории `graphs/` создаются:

1. **execution_time_<config>.png** - Время выполнения vs потоки
2. **speedup_<config>.png** - Ускорение vs потоки (с идеальной линией)
3. **efficiency_<config>.png** - Эффективность vs потоки
4. **comparison_all.png** - Сравнение всех конфигураций
5. **summary_table.txt** - Сводная таблица результатов

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

### Последовательное выполнение (Sequential)
- Полная сериализация: сначала весь ввод, затем все вычисления
- Используется как baseline для сравнения

### Параллельное выполнение с sections
- **Малое количество потоков (2-4)**: Умеренное ускорение
  - Две секции могут выполняться параллельно
  - Ввод и вычисления перекрываются
  
- **Среднее количество потоков (8-16)**: Хорошее ускорение
  - Эффективное использование конвейера
  - Минимальное время простоя
  
- **Большое количество потоков (32+)**: Ограниченное ускорение
  - Только две секции могут выполняться параллельно
  - Накладные расходы на синхронизацию растут

### Влияние размера задачи

**Малые векторы (1000 элементов):**
- Накладные расходы на синхронизацию более заметны
- Ограниченное ускорение

**Средние векторы (5000 элементов):**
- Баланс между вычислениями и синхронизацией
- Хорошее ускорение

**Большие векторы (10000 элементов):**
- Вычисления доминируют
- Максимальное ускорение от параллелизма

## Для отчета (For Report)

Используйте следующие материалы:

1. **Графики ускорения** - показывают эффективность sections
2. **Графики эффективности** - демонстрируют масштабируемость
3. **Анализ времени** - разделение на ввод и вычисления
4. **Сравнение конфигураций** - влияние размера задачи
5. **Таблица summary_table.txt** - числовые данные для отчета

## Ключевые выводы (Key Findings)

1. ✅ **Директива sections позволяет параллелизовать разнородные задачи**
   - Ввод и вычисления выполняются одновременно
   - Конвейерная обработка данных
   - Эффективное использование ресурсов

2. ✅ **Ограничение масштабируемости**
   - Только две секции могут выполняться параллельно
   - Ускорение ограничено количеством секций
   - Дополнительные потоки не дают преимущества

3. ✅ **Важность синхронизации**
   - Критические секции необходимы для общего буфера
   - Накладные расходы на синхронизацию растут с потоками
   - Баланс между параллелизмом и overhead

4. ✅ **Размер задачи влияет на эффективность**
   - Большие векторы: лучшее ускорение
   - Малые векторы: накладные расходы доминируют
   - Оптимальный размер зависит от системы

5. ✅ **Sections vs другие подходы**
   - Sections: для разнородных задач
   - For: для однородных циклов
   - Tasks: для динамического параллелизма

## Применение в реальных задачах (Real-world Applications)

### Конвейерная обработка данных
- Чтение данных из файла/сети
- Обработка данных
- Запись результатов

### Научные вычисления
- Загрузка данных эксперимента
- Вычисление метрик
- Визуализация результатов

### Обработка потоков данных
- Получение данных от датчиков
- Фильтрация и обработка
- Сохранение результатов

### Когда использовать sections:
- Есть несколько независимых задач
- Задачи имеют разную природу (ввод/вывод, вычисления)
- Количество задач известно заранее
- Нужна простая параллелизация без сложной логики

## Автор (Author)

Задание выполнено в рамках курса "Введение в суперкомпьютерные вычисления"

## Лицензия (License)

Учебный проект