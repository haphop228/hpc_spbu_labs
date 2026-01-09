# OpenMPI Tasks

This directory contains MPI programming tasks

## Structure

- task1: Min/Max search with MPI_Reduce
- task2: Dot product calculation
- task3: Ping-pong latency and bandwidth test
- task4: Matrix multiplication (Striped and Cannon algorithms)
- task5: Computation vs communication balance
- task6: MPI send modes comparison
- task7: Blocking vs non-blocking communication
- task8: MPI_Sendrecv performance
- task9: Custom collective operations

## Running

Each task contains:
- main.cpp: Source code
- Makefile: Build configuration
- job.sh: SLURM batch script
- plot_graphs.py: Visualization script

Build and run:
```bash
cd taskN
make
sbatch job.sh
python3 plot_graphs.py
```

## Requirements

- OpenMPI
- GCC/G++
- Python 3 with pandas, matplotlib, seaborn
