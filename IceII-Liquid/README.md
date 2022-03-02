# Melting point for IceII-Liquid coexistence

* ```1-CreateIceVI```: Create ice II lammps data file. 
* ```2-Bulk```: Simulation of bulk liquid and bulk ice II. Used to determine parameters for environment similiarity index. 
* ```3-CalculateDistributions```: Calculation, and choice for parameters for envioronment similarity index and collective variable number of ice-like molecules. 
* ```4-PrepareCoexistenceConfiguration```: Sets up correct initial box for coexistence simulations. Uses bulk simulations to determine average interface area. 
* ```5-BiasedCoexistence```: Biased coexistence simulations and analsysis script for determining melting points.
