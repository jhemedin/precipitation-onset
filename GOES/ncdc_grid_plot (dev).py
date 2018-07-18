import os
import cartopy.crs as ccrs
from netCDF4 import Dataset as netcdf_dataset
import numpy as np
from timeit import default_timer as timer
import pyart
from tint import Cell_tracks
from tint.grid_utils import get_grid_size as ggs
import gc
from matplotlib import pyplot as plt
import itertools

start = timer()

def _nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def haversine(lat1, lon1, lat2, lon2):
    R = 6372800.  # Earth radius in kilometers

    dLat = np.radians(lat2 - lat1)
    dLon = np.radians(lon2 - lon1)
    lat1 = np.radians(lat1)
    lat2 = np.radians(lat2)

    a = np.sin(dLat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dLon/2)**2
    c = 2*np.arcsin(np.sqrt(a))

    return R * c


def get_grid(filename):
    nc = netcdf_dataset(filename)
    
    sat_height = nc.variables['goes_imager_projection'].perspective_point_height
    radar_lon = -98.128
    radar_lat = 36.741

    _x = nc.variables['x'] * sat_height
    _y = nc.variables['y'] * sat_height
    _c = nc.variables['CMI_C13'][:]
    data = nc.variables['CMI_C13']
    
    proj_var = nc.variables[data.grid_mapping]
    
    globe = ccrs.Globe(ellipse='sphere', semimajor_axis=proj_var.semi_major_axis,
                       semiminor_axis=proj_var.semi_minor_axis)
    
    proj = ccrs.Geostationary(central_longitude=-75,sweep_axis='x',
                              satellite_height=sat_height, globe = globe)
    
    trans = ccrs.Miller(central_longitude=0)
    
    transform_xy = trans.transform_points(proj, _x, _y)
    
    lim = [_nearest(transform_xy[:,0],-100.75),_nearest(transform_xy[:,0],-95.5)
            ,_nearest(transform_xy[:,1],38.822),_nearest(transform_xy[:,1],34.66)]
    
    x = _x[lim[0]:lim[1]]
    y = _y[lim[2]:lim[3]]
    

    for i in range(0,100,1):
        a = y[(i+1)] - y[i]
        b = y[(i+2)] - y[(i+1)]
        print(b-a)
    
    c = _c[lim[2]:lim[3],lim[0]:lim[1]]
    
    print(c)
    
    satvar = nc.variables.keys()
    
    x_mesh, y_mesh = np.meshgrid(x, y)

    data = nc.variables['CMI_C13']
    satvar = nc.variables.keys()
    proj_var = nc.variables[data.grid_mapping]
    
    globe = ccrs.Globe(ellipse='sphere', semimajor_axis=proj_var.semi_major_axis,
                       semiminor_axis=proj_var.semi_minor_axis)
    
    proj = ccrs.Geostationary(central_longitude=-75,sweep_axis='x',
                              satellite_height=sat_height, globe = globe)
    
    trans = ccrs.Miller(central_longitude=0)
    t_xy = trans.transform_points(proj, x_mesh, y_mesh)
    x_meters = haversine(t_xy[:, :, 1], radar_lon, t_xy[:, :, 1], t_xy[:, :, 0])
    y_meters = haversine(radar_lat, t_xy[:, :, 0], t_xy[:, :, 1], t_xy[:, :, 0])
    plt.plot(x_meters[0, :])
    plt.plot(y_meters[:, 0])
#    xy_meters = [[haversine(radar_lat, radar_lon, lat, lon)
#                  for lat, lon in zip(row[:, 1], row[:, 0])]
#                 for row in ]
#    print(t_xy[0, 0, :])
    
#    print(min(x), max(x))
#    print(min(y), max(y))
#    print(min(t_x), max(t_x))
#    print(min(t_y), max(t_y))
#    points = [(x, y) for x, y in itertools.product(t_x, t_y)]
#    values = [c[x, y] for x, y in points]
#    
#    target_mesh = np.mgrid()
    
    
#    print(t_xy.shape)
    
    
    _time = {'calendar': 'gregorian','data': np.array([ 0.934]),
            'long_name': 'Time of grid', 'standard_name': 'time',
            'units': str('seconds since ' + nc.time_coverage_end)}
    
    _fields = {'reflectivity': {'_FillValue': -9999.0, 'data': np.ma.masked_array(c, mask= False),
                       'long_name': 'reflectivity',
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
    
    _origin_altitude = {'data': np.ma.masked_array(np.array([0]), mask= False), 
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
         radar_longitude= _origin_longitude, radar_latitude=_origin_latitude, radar_altitude=_origin_altitude)
    return grid
gc.collect()
get_grid(filenames[1])
# %%
# Presets
def build_fn(data_dir, basename):
    file = os.path.join(data_dir, basename)
    return os.path.join(os.path.dirname(ccrs.__file__),'data', 'netcdf', file)   

filelist = sorted(os.listdir('/home/scarani/Desktop/data/goes/001/'))
data_dir = '/home/scarani/Desktop/data/goes/001/' 
filenames = [build_fn(data_dir, bn) for bn in filelist[:5]]
grid_gen = (get_grid(fn) for fn in filenames)

channel = 13
# %%  
# Instantiate tracks object and view parameter defaults
tracks_obj = Cell_tracks(field='reflectivity')

# Adjust size parameter
tracks_obj.params['FIELD_THRESH'] = -273
tracks_obj.params['FLOW_MARGIN'] = 10000
tracks_obj.params['GS_ALT'] = 1500
tracks_obj.params['ISO_SMOOTH'] = 3
tracks_obj.params['ISO_THRESH'] = 8
tracks_obj.params['MAX_DISPARITY'] = 999
tracks_obj.params['MAX_FLOW_MAG'] = 50
tracks_obj.params['MAX_SHIFT_DISP'] = 15
tracks_obj.params['MIN_SIZE'] = 4
tracks_obj.params['SEARCH_MARGIN'] = 4000


# Get tracks from grid generator
print(tracks_obj.params)
tracks_obj.get_tracks(grid_gen)
# %%
# Inspect tracks
print(tracks_obj.tracks)



#for i in range(0,500,1):
#    for j in range(0,500,1):
#        k = b[i][j]
#        u = str(k)
#        if k == 'nan':
#            print('[' + str(i) + ']' + '[' + str(j) + ']' + '\n')
        

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
    
