#!/usr/bin/env python
# coding: utf-8

# # Prepare simulations

# In[ ]:


import numpy as np
import matplotlib.pylab as plt
import os, sys


# In[1]:


sims={}
#sims['1000']=[230,235,240,245,250]
sims['2000']=[235,240,245,250,275]
#sims['5000']=[230,235,240,245,250,255,260]


# ### Make simulation folders

# In[ ]:


for p in sims.keys():
   # pbar=P_bar[i]
    for t in sims[p]:
        fold='IceII_{}atm_{}K'.format(p,t)
        os.system('cp -r IceII {}'.format(fold))
        cmd='sed -i  "s#variable .* pressure .*#variable        pressure equal {}#g" {}/in.pressure\n'.format(p,fold)
        cmd+='sed -i  "s#variable.*temperature equal.*#variable        temperature equal {}#g" {}/in.temp'.format(t,fold)
        os.system(cmd)


# In[1]:


get_ipython().system('jupyter nbconvert --to script prep_sims.ipynb')

