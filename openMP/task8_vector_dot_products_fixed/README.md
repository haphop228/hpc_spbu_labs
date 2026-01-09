# Task 8: Vector Dot Products with OpenMP Sections

## Описание задачи (Task Description)

Разработка программы для вычисления скалярного произведения для последовательного набора векторов. Ввод векторов и вычисление их произведения организованы как две раздельные задачи, для распараллеливания которых используется директива `sections`.

**Формула скалярного произведения:**
```
dot_product(a, b) = Σ(a[i] * b[i]) для i=0..n-1
```

Implementation of parallel vector dot product computation using OpenMP sections directive. Input and computation are organized as two separate parallel tasks using producer-consumer pattern.

## Структура проекта (Project Structure)

```
task8_vector_dot_products_fixed/
├── src/                          # Source code
│   └── vector_dot_products.cpp   # Main program with sections
├── scripts/                      # Automation scripts
│   ├── compile.sh                # Compilation script
│   ├── run_benchmarks.sh         # Benchmark runner
│   └── test_pipeline.sh          # Full test pipeline
├── data/                         # Test data files
├── analysis/                     # Analysis scripts
│   ├── analyze.py                # Results processing
│   └── plot_graphs.py            # Graph generation
├── bin/                          # Compiled binaries
├── results/                      # Benchmark results (CSV)
├── graphs/                       # Generated graphs
├── .gitignore                    # Git ignore file
├── README.md                     # This file
└── QUICKSTART.md                 # Quick start guide
```

## Ключевые особенности (Key Features)

### 1. OpenMP Sections Directive
Программа использует `#pragma omp parallel sections` для создания двух параллельных задач:

```cpp
#pragma omp parallel sections
{
    #pragma omp section  // СЕКЦИЯ 1: Чтение векторов из файла
    {
        // Producer: читает векторы и добавляет в очередь
    }
    
    #pragma omp section  // СЕКЦИЯ 2: Вычисление скалярных произведений
    {
        // Consumer: берет векторы из очереди и вычисляет
    }
}
```

### 2. Producer-Consumer Pattern
- **Producer (Section 1)**: Читает пары векторов из файла и помещает в потокобезопасную очередь
- **Consumer (Section 2)**: Извлекает пары из очереди и вычисляет скалярные произведения
- **Синхронизация**: Использует атомарные переменные и OpenMP locks

### 3. Thread-Safe Queue
Реализована потокобезопасная очередь с использованием `omp_lock_t`:

```cpp
class ThreadSafeQueue {
    queue<VectorPair> q;
    omp_lock_t lock;
    
    void push(const VectorPair& item);
    bool try_pop(VectorPair& item);
};
```

### 4. Ограничение Sections
**Важно**: Директива `sections` создает ровно столько параллельных задач, сколько указано секций (в нашем случае 2). Поэтому:
- Оптимальное количество потоков: **2**
- Дополнительные потоки (4, 8, и т.д.) дают минимальное улучшение
- Теоретический максимум ускорения: **~2x**

## Быстрый старт (Quick Start)

### 1. Компиляция (Compilation)

```bash
cd task8_vector_dot_products_fixed/scripts
chmod +x *.sh
./compile.sh
```

### 2. Быстрый тест (Quick Test)

```bash
./test_pipeline.sh
```

Выполнит:
- Компиляцию программы
- Генерацию тестовых данных
- Проверку корректности
- Быстрый бенчмарк

### 3. Полный бенчмарк (Full Benchmark)

```bash
./run_benchmarks.sh
```

Запустит тесты для:
- Размеры векторов: 1000, 5000, 10000
- Количество пар: 10, 50, 100
- Количество потоков: 1, 2, 4, 8
- Методы: sequential, sections

### 4. Анализ результатов (Analysis)

```bash
cd ../analysis

# Обработка данных
python3 analyze.py ../results/benchmark_YYYYMMDD_HHMMSS.csv

# Генерация графиков
python3 plot_graphs.py
```

## Использование программы (Program Usage)

### Команды

```bash
# Генерация тестовых данных
./bin/vector_dot_products generate <num_pairs> <vector_size> <output_file>

# Запуск бенчмарка
./bin/vector_dot_products benchmark <data_file> <num_threads> <method> <runs>

# Полный бенчмарк с анализом
./bin/vector_dot_products full <data_file> <runs>

# Проверка корректности
./bin/vector_dot_products verify <data_file>
```

### Примеры

```bash
# Генерация 50 пар векторов размером 10000
./bin/vector_dot_products generate 50 10000 vectors.txt

# Полный бенчмарк (5 запусков)
./bin/vector_dot_products full vectors.txt 5

# Бенчмарк sections с 2 потоками (10 запусков)
./bin/vector_dot_products benchmark vectors.txt 2 sections 10

# Проверка корректности
./bin/vector_dot_products verify vectors.txt
```

## Реализация (Implementation)

### Последовательный метод (Sequential)

```cpp
BenchmarkResult sequential_method(const string& filename, int runs) {
    // Фаза 1: Чтение всех векторов
    for (int p = 0; p < num_pairs; ++p) {
        // Читаем vec1 и vec2
    }
    
    // Фаза 2: Вычисление всех скалярных произведений
    for (int p = 0; p < num_pairs; ++p) {
        result = compute_dot_product(vec1, vec2);
    }
}
```

### Параллельный метод с Sections

```cpp
BenchmarkResult sections_method(const string& filename, int num_threads, int runs) {
    ThreadSafeQueue work_queue;
    atomic<bool> input_done(false);
    
    #pragma omp parallel sections
    {
        #pragma omp section  // Producer
        {
            // Читаем векторы из файла
            for (int p = 0; p < num_pairs; ++p) {
                VectorPair pair = read_pair();
                work_queue.push(pair);
            }
            input_done = true;
        }
        
        #pragma omp section  // Consumer
        {
            while (true) {
                VectorPair pair;
                if (work_queue.try_pop(pair)) {
                    result = compute_dot_product(pair.vec1, pair.vec2);
                } else if (input_done && work_queue.empty()) {
                    break;
                }
            }
        }
    }
}
```

### Утяжеление вычислений

Для демонстрации эффекта параллелизма используется искусственное утяжеление:

```cpp
double compute_dot_product(const vector<double>& vec1, const vector<double>& vec2) {
    double result = 0.0;
    
    // 100 повторений для утяжеления
    for (int repeat = 0; repeat < 100; ++repeat) {
        double temp = 0.0;
        for (size_t i = 0; i < vec1.size(); ++i) {
            temp += vec1[i] * vec2[i];
        }
        result = temp;
    }
    
    return result;
}
```

## Метрики производительности (Performance Metrics)

### 1. Время выполнения (Execution Time)
- **Total time**: Общее время выполнения
- **Input time**: Время чтения данных (Section 1)
- **Computation time**: Время вычислений (Section 2)

### 2. Ускорение (Speedup)
```
Speedup = T_sequential / T_parallel
```

### 3. Эффективность (Efficiency)
```
Efficiency = Speedup / num_threads * 100%
```

### 4. Теоретическое ускорение (Theoretical Speedup)
```
Theoretical_Speedup = (T_input + T_compute) / max(T_input, T_compute)
```

Для pipeline-параллелизма максимальное ускорение достигается когда обе секции работают одновременно.

## Ожидаемые результаты (Expected Results)

### С 2 потоками (оптимально)
- **Speedup**: ~1.2-1.5x
- **Efficiency**: ~60-75%
- Обе секции выполняются параллельно

### С 4+ потоками
- **Speedup**: ~1.3-1.6x (незначительное улучшение)
- **Efficiency**: ~30-40% (снижается)
- Дополнительные потоки простаивают

### Почему ограничение?
- Только **2 секции** могут выполняться параллельно
- Дополнительные потоки не могут быть использованы
- Это фундаментальное ограничение директивы `sections`

## Генерируемые графики (Generated Graphs)

После запуска анализа в директории `graphs/` создаются:

1. **execution_time_*.png** - Время выполнения vs потоки
2. **speedup_*.png** - Ускорение vs потоки (с идеальной линией)
3. **efficiency_*.png** - Эффективность vs потоки
4. **time_breakdown.png** - Разбивка времени на ввод и вычисления
5. **sections_limitation.png** - Демонстрация ограничения 2 секций
6. **summary_table.txt** - Сводная таблица результатов

## Требования (Requirements)

### Система (System)
- macOS или Linux
- Компилятор с поддержкой OpenMP:
  - GCC 11+ (рекомендуется для macOS)
  - Clang с libomp
  - GCC на Linux
- Минимум 2 ядра CPU

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

## Ключевые выводы (Key Findings)

1. ✅ **Sections directive** создает фиксированное количество параллельных задач
2. ✅ **Producer-Consumer pattern** эффективен для pipeline-параллелизма
3. ✅ **Оптимальное количество потоков = количество секций** (в нашем случае 2)
4. ✅ **Thread-safe queue** необходима для безопасной передачи данных
5. ✅ **Atomic variables** обеспечивают корректную синхронизацию
6. ✅ **Дополнительные потоки** не дают значительного улучшения

## Применение в реальных задачах (Real-world Applications)

### Pipeline Processing
- Чтение данных из файла/сети + обработка
- Декодирование + рендеринг видео
- Парсинг + анализ данных

### Producer-Consumer Tasks
- Веб-сервер: прием запросов + обработка
- Обработка изображений: загрузка + фильтрация
- Научные вычисления: ввод данных + расчеты

### Ограничения Sections
- Подходит для **фиксированного числа** параллельных задач
- Для динамического параллелизма лучше использовать `task` или `parallel for`
- Эффективно когда задачи имеют **разную природу** (I/O vs CPU)

## Сравнение с другими подходами (Comparison)

### Sections vs Parallel For
- **Sections**: Фиксированное число разнородных задач
- **Parallel For**: Динамическое распределение однородных итераций

### Sections vs Tasks
- **Sections**: Статическое распределение при запуске
- **Tasks**: Динамическое создание задач во время выполнения

### Когда использовать Sections?
- ✅ Небольшое фиксированное число задач (2-4)
- ✅ Задачи имеют разную природу (I/O, CPU, GPU)
- ✅ Нужен простой pipeline-параллелизм
- ❌ Не подходит для большого числа задач
- ❌ Не подходит для динамического параллелизма

## Для отчета (For Report)

Используйте следующие материалы:

1. **Графики ускорения** - показывают ограничение 2 секций
2. **Графики эффективности** - демонстрируют падение при >2 потоках
3. **Time breakdown** - показывает параллельное выполнение секций
4. **Sections limitation** - ключевой график для понимания ограничений
5. **Summary table** - числовые данные для таблиц в отчете

### Ключевые пункты для отчета:
- Директива `sections` создает фиксированное число параллельных задач
- Оптимальное количество потоков равно количеству секций
- Producer-Consumer pattern эффективен для pipeline-обработки
- Дополнительные потоки не улучшают производительность значительно
- Sections подходит для небольшого числа разнородных задач

## Автор (Author)

Задание выполнено в рамках курса "Введение в суперкомпьютерные вычисления"

## Лицензия (License)

Учебный проект