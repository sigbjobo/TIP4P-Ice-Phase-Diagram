# This script creates an ice VI configuration using GenIce.
for i in `seq 1 1`
do
	echo $i
	genice --rep 4 4 4 II --format g --seed $RANDOM > iceII.gro
	vmd -dispdev none -e script-vmd.tcl
done
