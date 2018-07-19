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
from scipy import interpolate
# %%
start = timer()

def _nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

#def haversine(lat1, lon1, lat2, lon2):
#    R = 6372800.  # Earth radius in kilometers
#
#    dLat = np.radians(lat2 - lat1)
#    dLon = np.radians(lon2 - lon1)
#    lat1 = np.radians(lat1)
#    lat2 = np.radians(lat2)
#
#    a = np.sin(dLat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dLon/2)**2
#    c = 2*np.arcsin(np.sqrt(a))
#
#    return R * c

def interp_lonlat(lon, lat, data, radar_lon, radar_lat, grid_x, grid_y):
    print('Interpolating...')
    
    x, y = pyart.core.transforms.geographic_to_cartesian_aeqd(lon, lat,
                                                              radar_lon,
                                                              radar_lat)

    target_x, target_y = np.meshgrid(grid_x['data'], grid_y['data'])
    print('x', np.any(np.isnan(target_x)))
    print('y', np.any(np.isnan(target_y)))
    points = list(zip(x.flatten(), y.flatten()))
    values = data.flatten()
    interp_data = interpolate.griddata(points, values, (target_x, target_y))
    interp_data = np.ma.masked_where(np.isnan(interp_data), interp_data)
    interp_data = np.tile(interp_data, (2, 1, 1))
    interp_data = interp_data[np.newaxis, :, :, :]
    print(interp_data.shape)
    print('Done interpolating')
    return interp_data

# %% Setup
   
out_dir = '/home/scarani/grid/'

example_grid = pyart.io.read_grid('/home/scarani/Desktop/data/radar/grids_nc/20180524-25/KVNX20180524_190332_V06.nc')
grid_x = example_grid.x
grid_y = example_grid.y
_orig_lon = example_grid.origin_longitude
_orig_lat = example_grid.origin_latitude
_orig_alt = example_grid.origin_altitude
_projection = example_grid.projection
mesh_size = grid_x['data'][1] - grid_x['data'][0]
   
# %%
def get_grid(filename):
    print('gridding', filename)
    
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
    
    trans = ccrs.PlateCarree(central_longitude=0)
    
    transform_xy = trans.transform_points(proj, _x, _y)
    
    lim = [_nearest(transform_xy[:,0],-103),_nearest(transform_xy[:,0],-92)
            ,_nearest(transform_xy[:,1],42),_nearest(transform_xy[:,1],30)]
    
    x = _x[lim[0]:lim[1]]
    y = _y[lim[2]:lim[3]]
    
    c = _c[lim[2]:lim[3],lim[0]:lim[1]]
        
    x_mesh, y_mesh = np.meshgrid(x, y)
    
    lonlat = trans.transform_points(proj, x_mesh, y_mesh)
    lons = lonlat[:, :, 0]
    lats = lonlat[:, :, 1]
    print(lons, lats)
    
    interp_c = interp_lonlat(lons, lats, c,
                             radar_lon, radar_lat, grid_x, grid_y) 
    
    _time = {'calendar': 'gregorian','data': np.array([ 0.934]),
            'long_name': 'Time of grid', 'standard_name': 'time',
            'units': str('seconds since ' + nc.time_coverage_end)}
    
#    _fields = {'reflectivity': {'_FillValue': -9999.0, 'data': np.ma.masked_array(c, mask= False),
#                       'long_name': 'reflectivity',
#                       'standard_name': 'equivalent_reflectivity_factor',
#                       'units': 'dBZ', 'valid_max': c.max(), 'valid_min': c.min()}}
    
    _fields = {'c13': {'_FillValue': -9999.0,
                                'data': interp_c,
               'long_name': 'channel 13 10.3 microns K',
               'standard_name': 'c13',
               'units': 'K', 'valid_max': c.max(), 'valid_min': c.min()}}
    
    _metadata = {'Conventions': '', 'comment': '',
                'history': '', 'institution': '', 'instrument_name': '',
                'original_container': 'NEXRAD Level II', 'references': '',
                'source': '', 'title': '', 'vcp_pattern': '', 'version': ''}
    
    _origin_latitude = {'data': np.array([0]),
                       'long_name': 'Latitude at grid origin',
                       'standard_name': 'latitude',
                       'units': 'degrees_north', 'valid_max': 90.0,
                       'valid_min': -90.0}
    
#    _origin_longitude = {'data': np.ma.array([radar_lon]), 
#                        'long_name': 'Longitude at grid origin', 
#                        'standard_name': 'longitude', 'units': 'degrees_east', 
#                        'valid_max': 180.0, 'valid_min': -180.0}
#    
#    _origin_altitude = {'data': np.ma.masked_array(np.array([0]), mask= False), 
#                       'long_name': 'Altitude at grid origin', 
#                       'standard_name': 'altitude', 'units': 'm'}
    
    _x = {'axis': 'X', 'data': grid_x['data'], 
          'long_name': 'X distance on the projection plane from the origin', 
          'standard_name': 'projection_x_coordinate', 'units': 'm'}
    
    _y = {'axis': 'Y', 'data': grid_y['data'], 
          'long_name': 'Y distance on the projection plane from the origin', 
          'standard_name': 'projection_x_coordinate', 'units': 'm'}
    
    _z = {'axis': 'Z', 'data': np.array([0, mesh_size]),
          'long_name': 'Z distance on the projection plane from the origin',
          'positive': 'up', 'standard_name': 'projection_z_coordinate',
          'units': 'm'}
    
    grid = pyart.core.grid.Grid(time=_time, fields=_fields, metadata=_metadata,
         origin_latitude=_orig_lat, origin_longitude=_orig_lon,
         origin_altitude=_orig_alt, x=_x, y=_y, z=_z, projection=_projection,
         radar_longitude= _orig_lon, radar_latitude=_orig_lat, radar_altitude=_orig_alt)
    
#    display = pyart.graph.GridMapDisplay(grid)
#    display.plot_grid(field='c13', edges=False)
    
    grid_name = os.path.basename(filename[:-3] + '_grid.nc')
    full_name = os.path.join(out_dir, grid_name)
    pyart.io.write_grid(full_name, grid)
    
# %%
# Execute
def build_fn(data_dir, basename):
    file = os.path.join(data_dir, basename)
    return os.path.join(os.path.dirname(ccrs.__file__),'data', 'netcdf', file)   

filelist = sorted(os.listdir('/home/scarani/Desktop/data/goes/001/'))
data_dir = '/home/scarani/Desktop/data/goes/001/' 
filenames = [build_fn(data_dir, bn) for bn in filelist[:5]]
for fn in filenames:
    get_grid(fn)
