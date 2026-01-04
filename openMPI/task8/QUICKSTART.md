# Quick Start Guide - MPI Task 8

## Быстрый запуск на кластере

### Запуск экспериментов
```bash
cd openMPI/task8

# Эксперимент 1: Fixed (2 ноды фиксированно)
sbatch job.sh

# Эксперимент 2: Auto (автоматическое размещение)
sbatch job_auto.sh
```

### После завершения заданий
```bash
# Визуализация результатов
python3 plot_graphs.py
```

## Локальный запуск (для тестирования)

```bash
cd openMPI/task8

# Компиляция
make clean
make

# Запуск с 2 процессами
mpirun -np 2 ./program > data.csv

# Визуализация
python3 plot_graphs.py
```

## Что делает программа?

Измеряет производительность операции `MPI_Sendrecv` (одновременная отправка и прием) для различных размеров сообщений от 0 байт до 16 МБ.

## Две конфигурации запуска

| Конфигурация | Скрипт | Размещение | Коммуникация | Файл результатов |
|--------------|--------|------------|--------------|------------------|
| **Fixed** | job.sh | 2 ноды фиксированно | Через сеть | data.csv |
| **Auto** | job_auto.sh | Планировщик решает | Зависит от размещения | data_auto.csv |

### Зачем две конфигурации?

- **Fixed**: Реалистичный сценарий (процессы на разных узлах, коммуникация через сеть)
- **Auto**: Оптимальное размещение (может быть на одном узле с shared memory)

Сравнение показывает влияние типа коммуникации на производительность.

## Структура файлов

```
openMPI/task8/
├── main.cpp                    # Программа с MPI_Sendrecv
├── Makefile                    # Сборка
├── job.sh                      # SLURM скрипт (Fixed)
├── job_auto.sh                 # SLURM скрипт (Auto)
├── plot_graphs.py              # Визуализация
├── README.md                   # Полная документация
├── QUICKSTART.md               # Этот файл
├── SUMMARY.md                  # Итоговая сводка
├── data.csv                    # Результаты Fixed
├── data_auto.csv               # Результаты Auto
└── graphs/                     # Графики
    ├── time_vs_size_fixed.png
    ├── bandwidth_vs_size_fixed.png
    ├── time_vs_size_auto.png
    ├── bandwidth_vs_size_auto.png
    ├── comparison_time.png
    ├── comparison_bandwidth.png
    ├── comparison_latency.png
    └── comparison_speedup.png
```

## Создаваемые графики

### Отдельные для каждой конфигурации:
1. **time_vs_size_fixed.png** - время передачи (Fixed)
2. **bandwidth_vs_size_fixed.png** - пропускная способность (Fixed)
3. **time_vs_size_auto.png** - время передачи (Auto)
4. **bandwidth_vs_size_auto.png** - пропускная способность (Auto)

### Сравнительные:
5. **comparison_time.png** - сравнение времени
6. **comparison_bandwidth.png** - сравнение пропускной способности
7. **comparison_latency.png** - латентность для малых сообщений
8. **comparison_speedup.png** - относительная производительность

## Проверка результатов

После выполнения `sbatch job.sh` и `sbatch job_auto.sh` проверьте:

1. **Лог-файлы**:
   - `result_<job_id>.out` - стандартный вывод (Fixed)
   - `result_auto_<job_id>.out` - стандартный вывод (Auto)
   - `error_<job_id>.txt` - ошибки (должны быть пустыми)

2. **Данные**:
   - `data.csv` - результаты Fixed
   - `data_auto.csv` - результаты Auto

3. **Графики** (после `python3 plot_graphs.py`):
   - 8 графиков в папке `graphs/`

## Ожидаемые результаты

### Fixed (2 ноды):
- Латентность: ~100-200 мкс (сетевая коммуникация)
- Пропускная способность: ~100-110 МБ/сек (ограничена сетью)

### Auto (планировщик):
- Латентность: может быть меньше (если на одном узле)
- Пропускная способность: может быть выше (shared memory)

### Сравнение:
- Speedup близок к 1.0 или Auto может быть быстрее
- Зависит от размещения процессов планировщиком

## Устранение проблем

### Ошибка компиляции
```bash
module load openmpi
module load gcc/9
make clean
make
```

### Нет данных в CSV
Проверьте `error_<job_id>.txt` на наличие ошибок выполнения.

### Графики не создаются
Убедитесь, что установлены необходимые пакеты:
```bash
pip3 install pandas matplotlib seaborn
```

### Только один эксперимент выполнен
Скрипт `plot_graphs.py` работает и с одним файлом данных, но для полного сравнения нужны оба:
```bash
sbatch job.sh       # Если еще не запущен
sbatch job_auto.sh  # Если еще не запущен
```

## Дополнительная информация

Полная документация: [`README.md`](README.md)