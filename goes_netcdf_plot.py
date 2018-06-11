import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from netCDF4 import Dataset as netcdf_dataset
import numpy as np

import gc
from timeit import default_timer as timer
start = timer()

file = os.path.join(os.path.dirname(ccrs.__file__),'data', 'netcdf',
    '/home/scarani/Desktop/OR_ABI-L2-MCMIPC-M3_G16_s20181591902335_e20181591905108_c20181591905239.nc')
nc = netcdf_dataset(file)


earth_cir = 40074274.9
x = nc.variables['x'][:]
y = nc.variables['y'][:]
#x = ((nc.variables['x'][:])/(2*np.pi))*earth_cir
#y = ((nc.variables['y'][:])/(2*np.pi))*earth_cir
z = nc.variables['CMI_C13'][:].data 
data1 = nc.variables['CMI_C13']
sat = nc.variables
satvar = nc.variables.keys()
height = nc.variables['goes_imager_projection'].perspective_point_height


proj_var = nc.variables[nc.variables['CMI_C13'].grid_mapping]

globe = ccrs.Globe(ellipse='sphere', semimajor_axis=proj_var.semi_major_axis,
                   semiminor_axis=proj_var.semi_minor_axis)

proj = ccrs.Geostationary(central_longitude=-75, 
                          sweep_axis='x', satellite_height=35786023.0, globe = globe)

#proj = ccrs.LambertConformal(central_longitude=-75,
#                             central_latitude=0,
#                             globe=globe)


north = proj.y_limits[1]
south = proj.y_limits[0]
east = proj.x_limits[1]
west = proj.x_limits[0]


fig = plt.figure(figsize=(15, 15))
ax = fig.add_subplot(1, 1, 1, projection=proj)
#ax = plt.axes(projection=ccrs.LambertConformal())
#ax.set_extent([west, east, south, north])
#ax.pcolormesh(x,y,z,zorder=1, transform=ccrs.Geostationary())
ax.set_xlim(west,east)
ax.set_ylim(south,north)
#ax.add_feature(cfeature.STATES, linewidth=1, edgecolor='black',zorder=2)
#ax.coastlines(resolution = '10m', linewidth=1, edgecolor='black',zorder=2)
#ax.add_feature(cfeature.BORDERS, linewidth=1, edgecolor='black',zorder=2)
ax.imshow(z, origin='upper', cmap='Greys', transform=ccrs.Geostationary())
plt.show()

gc.collect()
end = timer()
print("Time: %s seconds"%round((end - start),2))