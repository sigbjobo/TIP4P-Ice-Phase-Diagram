#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128              # total number of tasks across all nodes
#SBATCH --cpus-per-task=1      # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --time=0:30:00         # total run time limit (HH:MM:SS)
#SBATCH --partition=debug
#SBATCH --job-name="COEX-ICEII" 
#SBATCH -A SLC103
set -e


export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export PLUMED_NUM_THREADS=$SLURM_CPUS_PER_TASK

pwd; hostname; date
module load fftw openmpi


############################################################################
# Variables definition
############################################################################
export LAMMPS_EXE=/home/sbore/software/mbx_lammps_plumed/lammps/src/lmp_mpi_mbx


for NMPI in 1 2 4 8 16 32
do
    let OMP=32/$NMPI
    export OMP_NUM_THREADS=$OMP
    export PLUMED_NUM_THREADS=$OMP
    let NMPI_TOT=4*$NMPI
    srun -n $NMPI_TOT $LAMMPS_EXE -sf omp -partition 4x$NMPI -in start.lmp
    cp log.lammps.0 log_${NMPI}_${OMP}
done
