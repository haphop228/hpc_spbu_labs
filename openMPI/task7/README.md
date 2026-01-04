# MPI Task 7: Non-Blocking Communication

## Description

Implementation of non-blocking MPI operations (MPI_Isend/MPI_Irecv) to overlap communication with computation. Comparison with blocking operations (MPI_Sendrecv) to evaluate performance improvements.

## Key Differences

**Blocking (Task 5):**
```cpp
emulate_computation(compute_us);
MPI_Sendrecv(...);  // Sequential
```

**Non-Blocking (Task 7):**
```cpp
MPI_Irecv(...);     // Start receive
MPI_Isend(...);     // Start send
emulate_computation(compute_us);  // Overlap!
MPI_Waitall(...);   // Wait for completion
```

## Files

- `main.cpp` - Benchmark program comparing blocking vs non-blocking
- `Makefile` - Build configuration
- `job.sh` - SLURM script for 2 nodes (fixed placement)
- `job_auto.sh` - SLURM script with automatic placement
- `plot_graphs.py` - Visualization
- `README.md` - Documentation

## Running

```bash
make
sbatch job.sh
sbatch job_auto.sh
python3 plot_graphs.py
```

## Test Matrix

- Data sizes: 1KB, 10KB, 100KB, 1MB
- Compute times: 10μs, 100μs, 1ms, 10ms
- 16 processes total

## Expected Results

Non-blocking operations show improvement when:
- T_compute >= T_communication
- Compute-bound workloads benefit most
- Network-bound workloads show minimal improvement