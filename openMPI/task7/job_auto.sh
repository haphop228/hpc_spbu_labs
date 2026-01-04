#!/bin/bash
#SBATCH --job-name=mpi_nonblock_auto
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

echo "Label;Processes;DataSize;ComputeUS;BlockingTime;NonBlockingTime;Speedup" > data_auto.csv

for NP in 2 4 8 16; do
    mpirun -np $NP ./nonblock_bench >> data_auto.csv
done

ls -lh data_auto.csv
