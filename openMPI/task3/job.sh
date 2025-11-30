#!/bin/bash
#SBATCH --job-name=mpi_pingpong
#SBATCH --output=result_%j.out
#SBATCH --error=error_%j.txt
#SBATCH --nodes=2
#SBATCH --ntasks=2
#SBATCH --time=00:10:00

module load openmpi
module load gcc/9
module load make

cd $SLURM_SUBMIT_DIR

make clean
make

# Записываем результат сразу в data.csv
mpirun -np 2 ./program > data.csv