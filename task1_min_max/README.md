# Task 1: Finding Minimum/Maximum in Vector using OpenMP

## Project Structure

```
task1_min_max/
├── src/
│   ├── min_max.c           # Main OpenMP program
│   └── utils.h             # Helper functions
├── data/
│   ├── generate_tests.py   # Test data generator
│   └── test_configs.json   # Test configurations
├── results/
│   └── (benchmark results will be stored here)
├── analysis/
│   ├── analyze.py          # Data analysis script
│   └── plot_graphs.py      # Graph generation
├── scripts/
│   ├── run_benchmarks.sh   # Automated benchmark runner
│   └── compile.sh          # Compilation script
└── report/
    └── (generated graphs and tables)
```

## Pipeline Stages

### Stage 1: Input/Test Data Generation
- `data/generate_tests.py`: Generates test vectors of various sizes
- `data/test_configs.json`: Configuration for test parameters

### Stage 2: Main Program
- `src/min_max.c`: OpenMP implementation with/without reduction
- Measures execution time for core computation only
- Outputs results in JSON format for analysis

### Stage 3: Analysis & Visualization
- `analysis/analyze.py`: Processes benchmark results
- `analysis/plot_graphs.py`: Generates graphs for report
  - Execution time vs thread count
  - Speedup vs thread count
  - Comparison: reduction vs non-reduction

## Usage

1. Compile the program:
   ```bash
   cd scripts
   chmod +x *.sh
   ./compile.sh
   ```

2. Run benchmarks:
   ```bash
   ./run_benchmarks.sh
   ```

3. Analyze results:
   ```bash
   cd ../analysis
   python3 analyze.py ../results/benchmark_YYYYMMDD_HHMMSS.json
   ```

4. Generate graphs:
   ```bash
   python3 plot_graphs.py
   ```

## Test Configuration

- Vector sizes: 10^6, 10^7, 10^8 elements
- Thread counts: 1, 2, 4, 8, 16
- Repetitions: 10 runs per configuration
- Variants: with reduction, without reduction

## Implementation Details

### With Reduction
Uses OpenMP's built-in `reduction(min:var)` and `reduction(max:var)` clauses:
```c
#pragma omp parallel for reduction(min:min_val)
for (long long i = 0; i < n; i++) {
    if (arr[i] < min_val) {
        min_val = arr[i];
    }
}
```

### Without Reduction
Manual implementation using thread-local variables:
```c
#pragma omp parallel
{
    int tid = omp_get_thread_num();
    double local_min = DBL_MAX;
    
    #pragma omp for
    for (long long i = 0; i < n; i++) {
        if (arr[i] < local_min) {
            local_min = arr[i];
        }
    }
    
    thread_mins[tid] = local_min;
}
// Then combine thread_mins to find global minimum
```

## Expected Results

The benchmarks will show:
1. **Speedup**: Both methods should show good speedup up to the number of physical cores
2. **Efficiency**: Efficiency typically decreases as thread count increases
3. **Comparison**: Reduction method is usually slightly faster due to compiler optimizations
4. **Scalability**: Performance scales well with problem size

## Notes

- The program measures only the core computation time (excluding data generation)
- Results are output in JSON format for easy parsing
- Multiple runs allow for statistical analysis (median values are used)
- Graphs include ideal speedup lines for comparison