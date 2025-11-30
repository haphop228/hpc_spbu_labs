#!/bin/bash
#SBATCH --job-name=mpi_matmul
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

mpirun -np 1 ./matrix_mul header 0 > data.csv

# Размеры матриц: 576, 1152, 2304 (кратны 1, 2, 3, 4 - чтобы делилось нацело)
# 2304^3 операций ~ 12 млрд, на 1 ядре это несколько секунд.
SIZES=(576 1152 2304)

# Процессы (Только квадраты: 1, 4, 9, 16)
PROCS=(1 4 9 16)

for N in "${SIZES[@]}"; do
    for P in "${PROCS[@]}"; do
        mpirun -np $P ./matrix_mul striped $N >> data.csv
        mpirun -np $P ./matrix_mul cannon $N >> data.csv
    done
done