#!/bin/bash
#SBATCH --job-name=mpi_min_bench
#SBATCH --output=result_mpi_%j.csv
#SBATCH --error=error_mpi_%j.txt
#SBATCH --nodes=2                # Запрашиваем 2 узла (для тестов меж-узловой связи)
#SBATCH --ntasks-per-node=16     # Максимум 16 процессов на узел
#SBATCH --time=00:10:00          # Лимит времени 10 минут

module load openmpi
module load gcc/9
module load make

cd $SLURM_SUBMIT_DIR

make clean
make

echo "Processes;Elements;Time;GlobalMin"

SIZES=(1000000 10000000 100000000 500000000)

PROCS=(1 2 4 8 16 32)

for N in "${SIZES[@]}"; do
    for P in "${PROCS[@]}"; do
        mpirun -np $P ./vec_min $N
    done
done