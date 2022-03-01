#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=10              # total number of tasks across all nodes
#SBATCH --cpus-per-task=1      # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --time=2:00:00         # total run time limit (HH:MM:SS)
#SBATCH --partition=shared
#SBATCH --job-name="1-Bulk" 
#SBATCH -A SLC103

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export PLUMED_NUM_THREADS=$SLURM_CPUS_PER_TASK

pwd; hostname; date

#module purge
module load fftw openmpi

source /home/sbore/software/mbx_lammps_plumed/plumed2/sourceme.sh

for j in 3500bar #4000bar 5000bar 6000bar 7000bar
do

    rm -rf IceV_$j Liquid_$j
    cp -r IceV IceV_$j
    cp ../1-Bulk/IceV_$j/dump.dcd IceV_$j/
    cp -r Liquid Liquid_$j
    cp ../1-Bulk/Liquid_$j/dump.dcd Liquid_$j/
    rm -rf overlap_$j.dat
    for i in `seq 0.04 0.0025 0.10` #for i in `seq 0.06 0.005 0.08`
    do
        for phase in IceV_$j Liquid_$j
        do
            cd $phase
            sed "s/replace/$i/g" plumed-base.dat > plumed.dat
            srun plumed driver --plumed plumed.dat --mf_dcd dump.dcd > /dev/null
            cd ../
        done
        result=`python script.py $j`
        echo $i $result >>overlap_$j.dat
        for phase in IceV_$j Liquid_$j
        do
            cd $phase
	    cp histo Histo_$i
	    rm COLVAR *histo*
	    
            cd ../
        done
    done
done
