# Task 3: MPI Message Exchange Performance Analysis

## Описание задачи (Task Description)

Разработка программы для исследования производительности обмена сообщениями между двумя MPI процессами. Программа многократно обменивается сообщениями различной длины и измеряет время передачи данных.

Implementation of a program to study the performance of message exchange between two MPI processes. The program repeatedly exchanges messages of various lengths and measures data transmission time.

## Структура проекта (Project Structure)

```
task3_mpi_message_exchange/
├── src/                          # Исходный код
│   └── message_exchange.cpp      # Основная программа с MPI
├── scripts/                      # Скрипты автоматизации
│   ├── compile.sh                # Компиляция программы
│   └── run_benchmarks.sh         # Запуск бенчмарков
├── analysis/                     # Скрипты анализа
│   ├── analyze.py                # Обработка результатов
│   └── plot_graphs.py            # Генерация графиков
├── data/                         # Конфигурации (опционально)
├── bin/                          # Скомпилированные бинарники
├── results/                      # Результаты бенчмарков (CSV)
├── graphs/                       # Сгенерированные графики
├── .gitignore                    # Git ignore файл
└── README.md                     # Этот файл
```

## Быстрый старт (Quick Start)

### 1. Компиляция (Compilation)

```bash
cd task3_mpi_message_exchange
chmod +x scripts/*.sh
./scripts/compile.sh
```

Скрипт автоматически:
- Определит вашу ОС (macOS/Linux)
- Найдет подходящий MPI компилятор (mpic++/mpicxx)
- Скомпилирует программу с оптимизациями
- Проверит работу MPI

### 2. Быстрый тест (Quick Test)

```bash
# Тест с сообщением 1 KB, 100 итераций
mpirun -np 2 bin/message_exchange 1024 100

# Тест с сообщением 1 MB, 50 итераций
mpirun -np 2 bin/message_exchange 1048576 50
```

### 3. Полный бенчмарк (Full Benchmark)

```bash
./scripts/run_benchmarks.sh
```

Запустит полный набор тестов:
- Размеры сообщений: от 1 байта до 16 MB
- 11 различных размеров сообщений
- 100 итераций для каждого размера
- Автоматическое сохранение результатов

⏱️ **Время выполнения:** ~5-15 минут в зависимости от системы

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
mpirun -np 2 bin/message_exchange <message_size> <iterations> [output_file]
```

**ВАЖНО:** Программа требует ровно 2 MPI процесса!

### Параметры

- `message_size` - размер сообщения в байтах
- `iterations` - количество обменов для усреднения
- `output_file` - (опционально) файл для сохранения результатов в CSV

### Примеры

```bash
# Базовый тест с 1 KB сообщением
mpirun -np 2 bin/message_exchange 1024 100

# Тест с большим сообщением (10 MB)
mpirun -np 2 bin/message_exchange 10485760 50

# С сохранением результатов
mpirun -np 2 bin/message_exchange 1048576 100 results/test.csv

# Тест различных размеров
for size in 1024 10240 102400 1048576; do
    mpirun -np 2 bin/message_exchange $size 100 results/my_benchmark.csv
done
```

## Реализация (Implementation)

### Алгоритм обмена сообщениями

Программа реализует простой протокол обмена между двумя процессами:

```
Процесс 0:                    Процесс 1:
  Send(data) ──────────────>  Recv(data)
  Recv(data) <──────────────  Send(data)
```

1. **Процесс 0** отправляет сообщение процессу 1, затем получает ответ
2. **Процесс 1** получает сообщение от процесса 0, затем отправляет ответ
3. Измеряется полное время цикла (round-trip time)

### Ключевые особенности

```cpp
// Warm-up: один обмен для прогрева кэша и сети
MPI_Send(...);
MPI_Recv(...);

MPI_Barrier(MPI_COMM_WORLD);

// Основные измерения
for (int iter = 0; iter < iterations; ++iter) {
    double start_time = MPI_Wtime();
    
    // Обмен сообщениями
    if (rank == 0) {
        MPI_Send(...);
        MPI_Recv(...);
    } else {
        MPI_Recv(...);
        MPI_Send(...);
    }
    
    double end_time = MPI_Wtime();
    times.push_back((end_time - start_time) * 1000.0);
    
    MPI_Barrier(MPI_COMM_WORLD);
}
```

## Метрики производительности (Performance Metrics)

### 1. Время передачи (Transmission Time)
Полное время цикла обмена сообщениями (туда и обратно) в миллисекундах.

### 2. Пропускная способность (Bandwidth)
```
Bandwidth (MB/s) = (2 × message_size) / (time_seconds × 1024²)
```
Учитывается передача данных в обе стороны.

### 3. Латентность (Latency)
Оценивается по времени передачи малых сообщений (≤ 1 KB).

### 4. Статистические метрики
- **Average time** - среднее время
- **Median time** - медианное время
- **Min/Max time** - минимальное/максимальное время
- **Standard deviation** - стандартное отклонение

## Генерируемые графики (Generated Graphs)

После запуска анализа в директории `graphs/` создаются:

1. **time_vs_message_size.png**
   - Зависимость времени от размера сообщения
   - Логарифмическая шкала
   - Показывает среднее, медиану и диапазон min-max

2. **bandwidth_vs_message_size.png**
   - Зависимость пропускной способности от размера
   - Показывает пиковую пропускную способность

3. **latency_analysis.png**
   - Анализ латентности для малых сообщений
   - Время на байт

4. **combined_time_bandwidth.png**
   - Комбинированный график с двумя осями Y
   - Одновременное отображение времени и пропускной способности

5. **performance_heatmap.png**
   - Тепловая карта производительности
   - Визуализация времени и пропускной способности

6. **summary_table.txt**
   - Текстовая таблица с результатами
   - Ключевые выводы

## Требования (Requirements)

### Система (System)
- macOS или Linux
- MPI реализация:
  - **OpenMPI** (рекомендуется)
  - **MPICH**
  - Другие совместимые реализации

### Python (для анализа)
```bash
pip3 install pandas matplotlib numpy
```

## Установка зависимостей (Dependencies Installation)

### macOS

```bash
# Установка OpenMPI
brew install open-mpi

# Python пакеты
pip3 install pandas matplotlib numpy
```

### Linux (Ubuntu/Debian)

```bash
# Установка OpenMPI
sudo apt-get update
sudo apt-get install libopenmpi-dev openmpi-bin

# Или MPICH
sudo apt-get install mpich

# Python пакеты
pip3 install pandas matplotlib numpy
```

### Linux (CentOS/RHEL)

```bash
# Установка OpenMPI
sudo yum install openmpi openmpi-devel
module load mpi/openmpi-x86_64

# Python пакеты
pip3 install pandas matplotlib numpy
```

## Устранение проблем (Troubleshooting)

### Ошибка: MPI compiler not found

```bash
# macOS
brew install open-mpi

# Linux
sudo apt-get install libopenmpi-dev
```

### Ошибка: This program requires exactly 2 MPI processes

Убедитесь, что используете `-np 2`:
```bash
mpirun -np 2 bin/message_exchange 1024 100
```

### Python библиотеки не найдены

```bash
pip3 install --user pandas matplotlib numpy
```

### Программа работает медленно

- Уменьшите количество итераций в `scripts/run_benchmarks.sh`
- Уменьшите максимальный размер сообщения
- Проверьте, что процессы запускаются на разных ядрах

## Ожидаемые результаты (Expected Results)

### Типичные характеристики

#### Латентность (малые сообщения)
- **1 byte - 1 KB:** 0.001 - 0.1 ms
- Зависит от реализации MPI и сетевого оборудования

#### Пропускная способность (большие сообщения)
- **Локальная машина:** 1000 - 10000 MB/s
- **Сеть Ethernet (1 Gbps):** 100 - 120 MB/s
- **Сеть Ethernet (10 Gbps):** 1000 - 1200 MB/s
- **InfiniBand:** 5000 - 12000 MB/s

### Зависимость от размера сообщения

1. **Малые сообщения (< 1 KB)**
   - Доминирует латентность
   - Низкая пропускная способность
   - Время почти не зависит от размера

2. **Средние сообщения (1 KB - 1 MB)**
   - Переходная область
   - Растущая пропускная способность

3. **Большие сообщения (> 1 MB)**
   - Доминирует пропускная способность
   - Линейная зависимость времени от размера
   - Достигается пиковая пропускная способность

## Для отчета (For Report)

Используйте следующие материалы:

1. **График time_vs_message_size.png**
   - Показывает зависимость времени от размера
   - Демонстрирует логарифмический рост

2. **График bandwidth_vs_message_size.png**
   - Показывает достижение пиковой пропускной способности
   - Важен для анализа эффективности

3. **График combined_time_bandwidth.png**
   - Комплексный анализ производительности
   - Показывает обе метрики одновременно

4. **Таблица summary_table.txt**
   - Числовые данные для отчета
   - Точные значения метрик

## Ключевые выводы (Key Findings)

1. **Латентность vs Пропускная способность**
   - Для малых сообщений критична латентность
   - Для больших сообщений критична пропускная способность

2. **Масштабируемость**
   - Время растет логарифмически для малых сообщений
   - Время растет линейно для больших сообщений

3. **Оптимальный размер сообщения**
   - Существует оптимальный размер для максимальной эффективности
   - Зависит от конкретной системы и сети

4. **Накладные расходы MPI**
   - Фиксированные накладные расходы на каждую операцию
   - Становятся незначительными для больших сообщений

## Соответствие заданию (Task Compliance)

### Требования из HPC-tasks-2025.pdf

✅ **Задание 3 (MPI):** Разработайте программу, в которой два процесса многократно обмениваются сообщениями длиной n байт. Выполните эксперименты и оцените зависимость времени выполнения операции передачи данных от длины сообщения.

**Выполнено:**
- ✅ Реализован обмен сообщениями между двумя процессами
- ✅ Многократный обмен для статистической достоверности
- ✅ Переменная длина сообщений (от 1 байта до 16 MB)
- ✅ Измерение времени передачи данных
- ✅ Вычислительные эксперименты с различными размерами
- ✅ Построены графики зависимости времени от длины сообщения
- ✅ Анализ пропускной способности и латентности
- ✅ Подробная документация и отчет

## Автор (Author)

Задание выполнено в рамках курса "Введение в суперкомпьютерные вычисления"

## Лицензия (License)

Учебный проект