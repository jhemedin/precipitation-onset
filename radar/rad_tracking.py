import os
import glob
import pyart 
from tint.tracks import Cell_tracks
from tint.visualization import animate
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from metpy.plots import colortables
import numpy as np
import pyart

# %%  
# Obtain sorted list of pyart grid files

#data_dir = '/home/scarani/Desktop/data/tracking/radar_grids/20180623-25/KVNX20180623*'
data_dir = '/home/scarani/Desktop/data/tracking/radar_grids/test/*nc'
                
grid_files = glob.glob(data_dir, recursive=True)
grid_files = [os.path.join(data_dir, file_name) for file_name in grid_files]
grid_files.sort()

# Create generator of pyart grid objects
grid_gen = (pyart.io.read_grid(file_name) for file_name in grid_files)


# %%  
# Instantiate tracks object and view parameter defaults
tracks_obj = Cell_tracks(field='reflectivity')

# Adjust size parameter
tracks_obj.params['FIELD_THRESH'] = 35 #
tracks_obj.params['FLOW_MARGIN'] = 10000
tracks_obj.params['GS_ALT'] = 1500
tracks_obj.params['ISO_SMOOTH'] = 3
tracks_obj.params['ISO_THRESH'] = 8
tracks_obj.params['MAX_DISPARITY'] = 999
tracks_obj.params['MAX_FLOW_MAG'] = 50
tracks_obj.params['MAX_SHIFT_DISP'] = 15
tracks_obj.params['MIN_SIZE'] = 8 #
tracks_obj.params['SEARCH_MARGIN'] = 4000


# Get tracks from grid generator
print(tracks_obj.params)
tracks_obj.get_tracks(grid_gen)

# Inspect tracks
print(tracks_obj.tracks)
# %%
# Create generator of the same grids for animator
anim_gen = (pyart.io.read_grid(file_name) for file_name in grid_files)


colormap = pyart.graph.cm_colorblind.HomeyerRainbow

animate(tracks_obj, anim_gen, '/home/scarani/Desktop/output/tracking/rad_20180623-25',
        keep_frames=True, cmap = colormap)

        

# Create generator of the same grids for animator
#anim_gen = (pyart.io.read_grid(file_name) for file_name in grid_files)

# Create animation in current working directory
#animate(tracks_obj, anim_gen, 'tint_test_animation', alt=1500)
        
    

        

#xlist = x.tolist()
#ylist = y.tolist()
#loc = []
#
#for i in range(0,500,1):
#    
#    loc.append((xlist[i],ylist[i]))
    
