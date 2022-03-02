#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1              # total number of tasks across all nodes
#SBATCH --cpus-per-task=32        # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --time=48:00:00          # total run time limit (HH:MM:SS)
#SBATCH --mem-per-cpu=1G
#SBATCH --partition=shared
#SBATCH --job-name="16-ves" 
#SBATCH -A SLC103


export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export PLUMED_NUM_THREADS=$SLURM_CPUS_PER_TASK

pwd; hostname; date
module load fftw openmpi


############################################################################
# Variables definition
############################################################################
LAMMPS_EXE=/home/sbore/software/mbx_lammps_plumed/lammps/src/lmp_mpi_mbx

cycles=2
threads_per_partition=1
############################################################################

############################################################################
# Run
############################################################################
#if [ -e runno ] ; then
   #########################################################################
   # Restart runs
   #########################################################################
#   nn=`tail -n 1 runno | awk '{print $1}'`
#      srun $LAMMPS_EXE -partition 1x1  -sf omp -in start.lmp
   #########################################################################
#else
   #########################################################################
   # First run
   #########################################################################
nn=1
# Number of partitions
srun $LAMMPS_EXE -partition 1x1  -sf omp -in start.lmp
   #########################################################################
#fi
############################################################################


############################################################################
# Prepare next run
############################################################################
# Back up
for j in $(seq 0 3)
do
        cp log.lammps.${j} log.lammps.${j}.${nn}
        cp restart2.lmp.${j} restart2.lmp.${j}.${nn}
        cp restart.lmp.${j} restart.lmp.${j}.${nn}
        cp data.final.${j} data.final.${j}.${nn}
done
############################################################################

############################################################################
# Check number of cycles
############################################################################
mm=$((nn+1))
echo ${mm} > runno
#cheking number of cycles
if [ ${nn} -ge ${cycles} ]; then
  exit
fi
############################################################################

############################################################################
# Resubmitting again
############################################################################
#sbatch < ../job.sh
############################################################################

date
