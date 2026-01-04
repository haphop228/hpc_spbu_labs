#!/bin/bash
#SBATCH --job-name=mpi_sendrecv_fixed
#SBATCH --output=result_%j.out
#SBATCH --error=error_%j.txt
#SBATCH --nodes=2
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:10:00

module load openmpi
module load gcc/9
module load make

cd $SLURM_SUBMIT_DIR

make clean
make

# Run with MPI_Sendrecv on 2 fixed nodes
mpirun -np 2 ./program > data.csv

ls -lh data.csv