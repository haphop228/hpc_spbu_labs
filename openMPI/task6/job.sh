#!/bin/bash
#SBATCH --job-name=mpi_modes
#SBATCH --output=result_%j.out
#SBATCH --error=error_%j.txt
#SBATCH --nodes=2
#SBATCH --ntasks=16
#SBATCH --time=00:20:00

module load openmpi
module load gcc/9
module load make

cd $SLURM_SUBMIT_DIR

make clean
make

# Запись заголовка
mpirun -np 1 ./matrix_modes header 0 > data.csv

# Режимы передачи
MODES=("Standard" "Synchronous" "Buffered" "Ready")

# Размеры матриц
SIZES=(576 1152 2304)

# Используем 16 процессов (4x4 решетка)
P=16

for N in "${SIZES[@]}"; do
    for M in "${MODES[@]}"; do
        mpirun -np $P ./matrix_modes $M $N >> data.csv
    done
done