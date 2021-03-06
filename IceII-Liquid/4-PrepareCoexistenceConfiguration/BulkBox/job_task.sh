#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=128              # total number of tasks across all nodes
#SBATCH --cpus-per-task=1      # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --time=8:00:00         # total run time limit (HH:MM:SS)
#SBATCH --partition=compute
#SBATCH --job-name="1-Bulk" 
#SBATCH -A SLC103


export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export PLUMED_NUM_THREADS=$SLURM_CPUS_PER_TASK

pwd; hostname; date

cycles=2
threads_per_partition=1


module load fftw openmpi
cat $task_file | xargs -l -P 3  bash -c 'cd $0; pwd; mpirun -np 42 /home/sbore/software/mbx_lammps_plumed/lammps/src/lmp_mpi_mbx -sf omp -in start.lmp'
