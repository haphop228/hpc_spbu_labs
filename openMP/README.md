# OpenMP Tasks

## Quick Start

### Prerequisites
- macOS or Linux
- Compiler with OpenMP support (gcc or clang+libomp)
- Python 3.6+
- Python packages: `pip3 install numpy matplotlib pandas`

### Compilation

Navigate to any task directory and compile:

```bash
cd openMP/task1_min_max/scripts
./compile.sh
```

The script will automatically detect your OS and install necessary dependencies.

### Running Benchmarks

```bash
./run_benchmarks.sh
```

This will run the full benchmark suite with various configurations.

### Analysis

```bash
cd ../analysis
python3 analyze.py ../results/benchmark_*.csv
python3 plot_graphs.py
```

Results will be saved in the `graphs/` directory.

## Task Structure

Each task follows the same structure:
- `src/` - Source code
- `scripts/` - Compilation and benchmark scripts
- `analysis/` - Python analysis scripts
- `data/` - Configuration files (gitignored after generation)
- `results/` - Benchmark results (gitignored)
- `graphs/` - Generated plots
- `bin/` - Compiled binaries (gitignored)

## Tasks Overview

1. **task1_min_max** - Finding minimum and maximum values
2. **task2_dot_product** - Vector dot product computation
3. **task3_integration** - Numerical integration
4. **task4_matrix_game** - Matrix operations
5. **task5_special_matrices** - Special matrix computations
6. **task6_loop_scheduling** - Loop scheduling strategies
7. **task7_reduction_sync** - Reduction and synchronization
8. **task8_vector_dot_products** - Multiple vector operations
9. **task9_nested_parallelism** - Nested parallel regions

## Common Parameters

Most programs accept similar parameters:
```bash
./bin/program <size> <threads> <method> <iterations>
```

- `size` - Problem size
- `threads` - Number of OpenMP threads
- `method` - Algorithm variant
- `iterations` - Number of runs for averaging

## Troubleshooting

### macOS Compilation Issues
```bash
brew install libomp
```

### Python Package Issues
```bash
pip3 install --user numpy matplotlib pandas
