#!/bin/bash
#SBATCH --job-name=mpi_collective
#SBATCH --output=result_%j.out
#SBATCH --error=error_%j.txt
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=8
#SBATCH --time=00:20:00

module load openmpi
module load gcc/9
module load make

cd $SLURM_SUBMIT_DIR

make clean
make

mpirun -np 16 ./program > data.csv
ls -lh data.csv
