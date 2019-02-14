
# coding: utf-8

# In[2]:


import os
import glob
import pyart 
from tint.tracks import Cell_tracks
from tint.visualization import animate
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from metpy.plots import colortables
import numpy as np


# In[8]:


# Obtain sorted list of pyart grid files
data_dir = './grids/*'
grid_files = glob.glob(data_dir, recursive=True)

print(len(grid_files))
grid_files = [os.path.join(base_dir, file_name) for file_name in grid_files[:]]
grid_files.sort()


# In[9]:


# Create generator of pyart grid objects

grid_gen = (pyart.io.read_grid(file_name) for file_name in grid_files)


# %%  
# Instantiate tracks object and view parameter defaults
tracks_obj = Cell_tracks(field='c13')

# Adjust size parameter
tracks_obj.params['FIELD_THRESH'] = -250 #
tracks_obj.params['FLOW_MARGIN'] = 10000
tracks_obj.params['GS_ALT'] = 0
tracks_obj.params['ISO_SMOOTH'] = 3
tracks_obj.params['ISO_THRESH'] = 8
tracks_obj.params['MAX_DISPARITY'] = 999
tracks_obj.params['MAX_FLOW_MAG'] = 50
tracks_obj.params['MAX_SHIFT_DISP'] = 15
tracks_obj.params['MIN_SIZE'] = 32 #
tracks_obj.params['SEARCH_MARGIN'] = 4000


# Get tracks from grid generator
print(tracks_obj.params)
tracks_obj.get_tracks(grid_gen)

# Inspect tracks
print(tracks_obj.tracks)
# %%
# Create generator of the same grids for animator
anim_gen = (pyart.io.read_grid(file_name) for file_name in grid_files)


#vmin = 320
#vmax = -198
#lcl = -269.5

vmin = 198
vmax = 320
lcl = 269.5


colormap = pyart.graph.cm_colorblind.HomeyerRainbow
colors2 = colormap(np.linspace(0, 1, int(((250-vmin)/(vmax-vmin))*1000)))
colors3 = plt.cm.Greys_r(np.linspace(.3, .5, int(((lcl-250)/(vmax-vmin))*1000)))
colors4 = plt.cm.Greys_r(np.linspace(.15, .2, int(((vmax-lcl)/(vmax-vmin))*1000)))
colors = np.vstack((colors4, colors3, colors2))
mymap = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors)

#colormap = pyart.graph.cm_colorblind.HomeyerRainbow
#colors2 = colormap(np.linspace(0, 1, 450))
#colors3 = plt.cm.Greys(np.linspace(.5, .7, 135))
#colors4 = plt.cm.Greys(np.linspace(.8, .95, 431))
#colors = np.vstack((colors4, colors3, colors2))
#mymap = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors)


# Create animation in current working directory
animate(tracks_obj, anim_gen, './output',
        keep_frames=True, vmin = -320, vmax = -198, cmap = mymap)

