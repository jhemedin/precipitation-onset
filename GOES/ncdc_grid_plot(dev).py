import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from netCDF4 import Dataset as netcdf_dataset
import numpy as np
import gc
from timeit import default_timer as timer
from datetime import date, datetime, timedelta
from metpy.plots import colortables
import matplotlib.colors as mcolors
import pyart
import scipy
import tint
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML, Image, display
import tempfile
import os
import shutil

import pyart
from tint.data_utils import get_nexrad_keys, read_nexrad_key
from tint import Cell_tracks, animate
from tint.visualization import embed_mp4_as_gif

start = timer()

def get_grid(x, y, c, proj):
   
    _time = {'calendar': 'gregorian','data': np.array([ 0.934]),
            'long_name': 'Time of grid', 'standard_name': 'time',
            'units': str('seconds since ' + nc.time_coverage_end)}
    
    _fields = {'ROI': {'_FillValue': -9999.0, 'data': np.ma.masked_array(c, mask= False),
                       'long_name': 'Reflectivity',
                       'standard_name': 'equivalent_reflectivity_factor',
                       'units': 'dBZ', 'valid_max': c.max(), 'valid_min': c.min()}}
    
    _metadata = {'Conventions': '', 'comment': '',
                'history': '', 'institution': '', 'instrument_name': '',
                'original_container': 'NEXRAD Level II', 'references': '',
                'source': '', 'title': '', 'vcp_pattern': '', 'version': ''}
    
    _origin_latitude = {'data': np.array([0]),
                       'long_name': 'Latitude at grid origin',
                       'standard_name': 'latitude',
                       'units': 'degrees_north', 'valid_max': 90.0,
                       'valid_min': -90.0}
    
    _origin_longitude = {'data': np.array([-75]), 
                        'long_name': 'Longitude at grid origin', 
                        'standard_name': 'longitude', 'units': 'degrees_east', 
                        'valid_max': 180.0, 'valid_min': -180.0}
    
    _origin_altitude = {'data': np.array([0]), 
                       'long_name': 'Altitude at grid origin', 
                       'standard_name': 'altitude', 'units': 'm'}
    
    _x = {'axis': 'X', 'data': x, 
          'long_name': 'X distance on the projection plane from the origin', 
          'standard_name': 'projection_x_coordinate', 'units': 'm'}
    
    _y = {'axis': 'Y', 'data': y, 
          'long_name': 'Y distance on the projection plane from the origin', 
          'standard_name': 'projection_x_coordinate', 'units': 'm'}
    
    _z = {'axis': 'Z', 'data': np.array([0]),
          'long_name': 'Z distance on the projection plane from the origin',
          'positive': 'up', 'standard_name': 'projection_z_coordinate',
          'units': 'm'}
    
    _projection = {'_include_lon_0_lat_0': True, 'proj': proj}
    
    grid = pyart.core.grid.Grid(time=_time, fields=_fields, metadata=_metadata,
         origin_latitude=_origin_latitude, origin_longitude=_origin_longitude,
         origin_altitude=_origin_altitude, x=_x, y=_y, z=_z, projection=_projection,
         radar_longitude= _origin_longitude, radar_latitude=_origin_latitude)
    return grid

# Presets
filelist = sorted(os.listdir('/home/scarani/Desktop/data/goes/001/'))
channel = 13
#gridlist = []
#grids = []




def gridlist(i):
    startfortime = timer()

    file = str('/home/scarani/Desktop/data/goes/001/' + i)   

    filename = os.path.join(os.path.dirname(ccrs.__file__),'data', 'netcdf', file)
    nc = netcdf_dataset(filename)
    
    sat_height = nc.variables['goes_imager_projection'].perspective_point_height
    
    
    x = nc.variables['x'][:].data * sat_height
    y = nc.variables['y'][:].data * sat_height
    c = nc.variables['CMI_C13'][:]
    data = nc.variables['CMI_C13']
    satvar = nc.variables.keys()
    proj_var = nc.variables[data.grid_mapping]
    
    
    globe = ccrs.Globe(ellipse='sphere', semimajor_axis=proj_var.semi_major_axis,
                       semiminor_axis=proj_var.semi_minor_axis)
    
    proj = ccrs.Geostationary(central_longitude=-75,sweep_axis='x',
                              satellite_height=sat_height, globe = globe)
    
    
    grid = get_grid(x, y, c, proj)
    print(grid.radar_longitude)
    #gridlist.append(grid)
    endfortime = timer()
    
    return grid
    
  
#for i in gridlist:
#    griditer = iter(i)
#    
#    grids.append(griditer)
grid_gen = (gridlist(i) for i in filelist)  
#grid_gen = (pyart.io.read_grid(file_name) for file_name in grid_files)

# Instantiate tracks object and view parameter defaults
tracks_obj = Cell_tracks()
print(tracks_obj.params)

# Adjust size parameter
#tracks_obj.params['MIN_SIZE'] = 4

# Get tracks from grid generator

# Inspect tracks
tracks_obj.get_tracks(grid_gen)
print(tracks_obj.tracks)

# Create generator of the same grids for animator
# anim_gen = (pyart.io.read_grid(file_name) for file_name in grid_files)

# Create animation in current working directory
#animate(tracks_obj, anim_gen, 'tint_test_animation', alt=1500)
        
        

#xlist = x.tolist()
#ylist = y.tolist()
#loc = []
#
#for i in range(0,500,1):
#    
#    loc.append((xlist[i],ylist[i]))
    
