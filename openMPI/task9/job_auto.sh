#!/bin/bash
#SBATCH --job-name=mpi_collective_auto
#SBATCH --output=result_auto_%j.out
#SBATCH --error=error_auto_%j.txt
#SBATCH --ntasks=16
#SBATCH --time=00:20:00

module load openmpi
module load gcc/9
module load make

cd $SLURM_SUBMIT_DIR

make clean
make

mpirun -np 16 ./program > data_auto.csv

ls -lh data_auto.csv
