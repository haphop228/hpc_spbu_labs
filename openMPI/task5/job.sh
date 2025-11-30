#!/bin/bash
#SBATCH --job-name=mpi_synthetic
#SBATCH --output=result_%j.out
#SBATCH --error=error_%j.txt
#SBATCH --nodes=2
#SBATCH --ntasks=16
#SBATCH --time=00:10:00

module load openmpi
module load gcc/9
module load make

cd $SLURM_SUBMIT_DIR

make clean
make

DATA_FILE="data.csv"
echo "Label;Procs;ComputeUS;Bytes;Time" > $DATA_FILE

PROCS=(1 2 4 8 16)

for P in "${PROCS[@]}"; do
    mpirun -np $P ./syn_bench ComputeBound 10000 1024 >> $DATA_FILE
done

for P in "${PROCS[@]}"; do
    mpirun -np $P ./syn_bench NetworkBound 10 4194304 >> $DATA_FILE
done

for P in "${PROCS[@]}"; do
    mpirun -np $P ./syn_bench Balanced 1000 102400 >> $DATA_FILE
done

echo "Tests finished. Data saved to $DATA_FILE"