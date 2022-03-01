import numpy as np

data1=np.genfromtxt("IceIh/histo")
data2=np.genfromtxt("Liquid/histo")
print(np.trapz(np.minimum(data1[:,1],data2[:,1]),x=data1[:,0]))

