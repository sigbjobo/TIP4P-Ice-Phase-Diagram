rm list.txt

find -name COLVAR* | grep Bias > list.txt
find -name plumed* >> list.txt
find -name env* >> list.txt


