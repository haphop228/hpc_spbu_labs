#!/bin/bash
#SBATCH --job-name=mpi_nonblock
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

echo "Label;Processes;DataSize;ComputeUS;BlockingTime;NonBlockingTime;Speedup" > data.csv

for NP in 2 4 8 16; do
    mpirun -np $NP ./nonblock_bench >> data.csv
done

ls -lh data.csv
