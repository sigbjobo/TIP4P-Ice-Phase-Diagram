#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=4              # total number of tasks across all nodes
#SBATCH --cpus-per-task=8      # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --time=48:00:00         # total run time limit (HH:MM:SS)
#SBATCH --partition=compute
#SBATCH --job-name="2-Bulk" 
#SBATCH -A SLC103


export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export PLUMED_NUM_THREADS=$SLURM_CPUS_PER_TASK

pwd; hostname; date
module load fftw openmpi


############################################################################
# Variables definition
############################################################################
export LAMMPS_EXE=/home/sbore/software/mbx_lammps_plumed/lammps/src/lmp_mpi_mbx

cycles=2
threads_per_partition=1
############################################################################

############################################################################
# Run
############################################################################
ls *EQUIL_*/ -d| xargs -l -P 4 bash -c 'cd $0; pwd; srun -n 4 $LAMMPS_EXE -sf omp -in equil.lmp'

date
