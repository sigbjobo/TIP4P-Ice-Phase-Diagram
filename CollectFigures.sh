# Collect figures used in article
cp AdditionalFigures/Interfaces/Systems.pdf Figures/
cp AdditionalFigures/Distributions/Overlap.png Figures/
cp IceIh-Liquid/4-BiasedCoexistence/figures/summary0.0atm.png Figures/IceIh_Liquid_summary0.0atm.png
cp IceVI-Liquid/5-BiasedCoexistence/figures/free_energy_single.png Figures/IceVI_free_energy.png
cp FullPhaseDiagram/figures/phase_diagrams.png Figures/


# Collect figures for SI
mkdir -p SiFigures
rm SiFigures/*
list="IceIII-Liquid/5-BiasedCoexistence/figures IceIII_Liquid
IceII-Liquid/5-BiasedCoexistence/figures IceII_Liquid
IceIh-Liquid/4-BiasedCoexistence/figures IceIh_Liquid
IceVI-Liquid/5-BiasedCoexistence/figures IceVI_Liquid
IceV-Liquid/4-BiasedCoexistence/figures  IceV_Liquid" 
echo $list | xargs -n2 bash -c 'for file in $(find  $0/*.png)
do
	echo $file
        new_name=$(basename $file)
	
 	new_name=$1_$new_name
 	echo $new_name	
	cp $file SiFigures/$new_name
done
'
cp FullPhaseDiagram/figures/GibbsLines.png SiFigures/
cp AdditionalFigures/Distributions/Overlap.png SiFigures/

rm SiFigures/*unbiased*
rm SiFigures/*phase_diagram*
rm SiFigures/*summary*
rm SiFigures/*thermodynamics*
rm SiFigures/*atm*
rm SiFigures/*single*
