#!/bin/bash
#SBATCH --job-name=mpi_sendrecv_auto
#SBATCH --output=result_auto_%j.out
#SBATCH --error=error_auto_%j.txt
#SBATCH --ntasks=2
#SBATCH --time=00:10:00

module load openmpi
module load gcc/9
module load make

cd $SLURM_SUBMIT_DIR

make clean
make

# Run with MPI_Sendrecv with automatic node placement
mpirun -np 2 ./program > data_auto.csv

ls -lh data_auto.csv