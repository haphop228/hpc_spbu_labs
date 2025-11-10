# Quick Start Guide - Task 8: Vector Dot Products with OpenMP Sections

## Быстрый старт за 3 шага

### Шаг 1: Компиляция
```bash
cd task8_vector_dot_products/scripts
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
# Генерация тестовых данных
./bin/vector_dot_products generate 100 1000 data/vectors.txt

# Последовательное выполнение
./bin/vector_dot_products benchmark data/vectors.txt 1 sequential 10

# Параллельное выполнение с sections (4 потока)
./bin/vector_dot_products benchmark data/vectors.txt 4 sections 10

# Проверка корректности
./bin/vector_dot_products verify data/vectors.txt
```

## Что тестируется

- **Методы**: sequential, sections
- **Конфигурации**: 50, 100, 200, 500 пар векторов
- **Размеры векторов**: 1000, 5000, 10000 элементов
- **Потоки**: 1, 2, 4, 8, 16, 32, 64, 128

## Ожидаемые результаты

- **Sequential** - baseline для сравнения
- **Sections (2 потока)** - умеренное ускорение (~1.5-1.8x)
- **Sections (4-8 потоков)** - хорошее ускорение (~1.8-2.0x)
- **Sections (16+ потоков)** - ограниченное ускорение (только 2 секции)

## Время выполнения

- Быстрый тест: ~1 минута
- Полный бенчмарк: ~15-30 минут

## Требования

- GCC с OpenMP или Clang с libomp
- Python 3 с pandas, matplotlib, numpy
- Минимум 4 ядра CPU

## Особенности Task 8

**Ключевые аспекты:**
1. ✅ Использование директивы `#pragma omp parallel sections`
2. ✅ Две раздельные задачи: ввод и вычисление
3. ✅ Конвейерная обработка данных
4. ✅ Синхронизация через критические секции
5. ✅ Демонстрация ограничений sections (только 2 секции)

**Ключевые инсайты:**
- Sections подходит для разнородных задач
- Ускорение ограничено количеством секций
- Конвейерная обработка эффективна для больших данных
- Синхронизация критична для корректности