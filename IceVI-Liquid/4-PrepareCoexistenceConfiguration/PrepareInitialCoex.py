#!/usr/bin/env python
# coding: utf-8

# # Preparation of initial box for coexsistence simulations

# In[1]:


import numpy as np, sys, os, glob
import matplotlib.pylab as plt
import MDAnalysis
from MDAnalysis import transformations
import json


# In[ ]:





# ## Setup half-melted simulation box

# In[2]:


with open('halfMeltedSettings.json','r') as fp:
    meltSettings = json.load(fp,strict=False)
print(meltSettings)


# In[5]:


os.system('cp -r HalfMeltedTemplate HalfMeltedEquilibrated')
os.system('cp -r InitialIce/ice.data HalfMeltedEquilibrated/')
os.system('cp -r HalfMeltedEquilibrated/melt.lmp HalfMeltedEquilibrated/start.lmp')


# In[4]:


for key in meltSettings.keys():
    with open('HalfMeltedEquilibrated/{}'.format(key),'r') as fp:
        lines=fp.read()
    lines=lines.format(**meltSettings[key])
    with open('HalfMeltedEquilibrated/{}'.format(key),'w') as fp:
        fp.write(lines)


# Run simulation to equilibrate structure.

# ## Setup pressures and temperatures 

# In[76]:


with open('coexIceSettings.json','r') as fp:
    coexSettings = json.load(fp,strict=False)
print(coexSettings)


# In[77]:


os.system('mkdir -p EquilIce')
for P in coexSettings['PT'].keys():
    for T in coexSettings['PT'][P]:
        new_fold='EquilIce/{}_{}/'.format(P,T)
        os.system('mkdir -p {}'.format(new_fold))
        os.system('cp -r HalfMeltedTemplate/* {}'.format(new_fold))
        os.system('cp -r InitialIce/ice.data {}'.format(new_fold))
        os.system('cp -r {}/equil.lmp {}/start.lmp'.format(new_fold,new_fold))
        
        with open('{}/in.pressure'.format(new_fold),'r') as fp:
            lines=fp.read()
        lines=lines.format(P=P)
        with open('{}/in.pressure'.format(new_fold),'w') as fp:
            fp.write(lines)
            
        with open('{}/in.temp'.format(new_fold),'r') as fp:
            lines=fp.read()
        lines=lines.format(T=T)
        with open('{}/in.temp'.format(new_fold),'w') as fp:
            fp.write(lines)
            
        with open('{}/start.lmp'.format(new_fold),'r') as fp:
            lines=fp.read()
        lines=lines.format(**coexSettings['start.lmp'])
        with open('{}/start.lmp'.format(new_fold),'w') as fp:
            fp.write(lines)
            
        with open('{}/in.box'.format(new_fold),'r') as fp:
            lines=fp.read()
        lines=lines.format(**coexSettings['in.box'])
        with open('{}/in.box'.format(new_fold),'w') as fp:
            fp.write(lines)
        
    


# In[ ]:


get_ipython().system('jupyter nbconvert --to script PrepareInitialCoex.ipynb')


# ### Gather 

# ### First step: equilibrate ice box

# In[21]:


sims = dict()
for a in press_box[:]:
    fold='BOX_EQUIL_{}atm/'.format(a)
    if single_pressure==None or single_pressure in fold:
        #sims[fold] = dict()
        #sims[fold]['p']=a[0]
        os.system('mkdir -p {}'.format(fold))
        os.system('cp -r {}/* {}'.format(standard_sim,fold))
        cmd='sed -i "" "s#variable .* pressure .*#variable        pressure equal {}#g" {}/in.pressure'.format(a,fold)
        os.system(cmd)


# ### Second step: Determine average box dimensions

# In[22]:


def extract_form_log(fn):
    lines=open(fn,'r').readlines()
    start=np.where([('Step' in l) for l in lines])[-1][0]
    data={keyi.lower(): []  for keyi in lines[start].split()}
    for l in lines[start+1:]:
        ls=l.split()
        try:
            if ls[0].isdigit():
                for i, key in enumerate(data.keys()):
                    data[key].append(float(ls[i]))
        
            else:
                break
        except:
            break
    for key in data.keys():
        data[key]=np.array(data[key])
    return data


# In[23]:


box_equil=dict()
for f in glob.glob('BOX_EQUIL_*/log.lammps'): 
    box_equil[f.replace('/log.lammps','')]=extract_form_log(f)


with open('box_size.pickle', 'wb') as handle:
    pickle.dump(box_equil, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open('box_size.pickle', 'rb') as handle:
    box_equil = pickle.load(handle)
print(box_equil.keys())


# In[24]:


for key in box_equil.keys():
    plt.plot(box_equil[key]['step'],box_equil[key]['lx'])
    plt.plot(box_equil[key]['step'],box_equil[key]['lz'])
    plt.plot(box_equil[key]['step'],box_equil[key]['ly'])
plt.xlabel('steps')
plt.ylabel(r'v/Å$^3$')


# In[ ]:





# In[30]:


for fold in box_equil.keys():
    sim=box_equil[fold]
                                                                                                                                                                             
    u = MDAnalysis.Universe(fold+'/ice_equil.data', in_memory=True)
    NIGNORE=int(0.25*len(box_equil[key]['step']))
    print(u.dimensions)

    lx=np.mean(sim['lx'][NIGNORE:])
    xy=np.mean(sim['xy'][NIGNORE:])
    xz=np.mean(sim['xz'][NIGNORE:])
    ly=np.mean(sim['ly'][NIGNORE:])
    yz=np.mean(sim['yz'][NIGNORE:])
    lz=np.mean(sim['lz'][NIGNORE:])
    A=np.array([[lx,0,0],
                 [xy,ly,0],
                 [xz,yz,lz]])
    dimensions_new=MDAnalysis.lib.mdamath.triclinic_box(A[0], A[1], A[2])
    print(dimensions_new)
    u.atoms.positions[:,0] = u.coord.positions[:,0]*lx/u.dimensions[0]
    u.atoms.positions[:,1] = u.coord.positions[:,1]*ly/u.dimensions[1]
    u.atoms.positions[:,2] = u.coord.positions[:,2]*lz/u.dimensions[2]

    u.dimensions[0]=dimensions_new[0]
    u.dimensions[1]=dimensions_new[1]
    u.dimensions[2]=dimensions_new[2]
    u.dimensions[3]=dimensions_new[3]
    u.dimensions[4]=dimensions_new[4]
    u.dimensions[5]=dimensions_new[5]
    for ts in u.trajectory:
        u.atoms.wrap()
    u.atoms.write(fold+'/ice_avg_equil.data')


# ### Third step: Melt half the box

# In[31]:


for a in press_box[:]:
    fold='BOX_MELT_{}atm/'.format(a)
    os.system('mkdir -p {}'.format(fold))
    os.system('cp -r {}/ice_avg_equil.data {}'.format(fold.replace('MELT','EQUIL'),fold))
    os.system('cp -r {}/* {}'.format(standard_sim,fold))
    cmd='sed -i "" "s#variable .* pressure .*#variable        pressure equal {}#g" {}/in.pressure'.format(a,fold)
    os.system(cmd)


# ### Fourth step: collect data files

# In[5]:


fold_out='COEX_BOXES/'
os.system('mkdir -p {}'.format(fold_out))
for a in press_box[:]:
    fold='BOX_MELT_{}atm/'.format(a)
    os.system('cp {}/water.data.equil {}/{}'.format(fold,fold_out,'water_{}atm.data'.format(a)))


# ### Convert notebook to python script

# In[1]:


get_ipython().system('jupyter nbconvert --to script Prepare_coexsistence.ipynb')


# In[ ]:




