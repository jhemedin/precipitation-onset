import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from netCDF4 import Dataset as netcdf_dataset
import numpy as np

import gc
from timeit import default_timer as timer
start = timer()

file = '/home/scarani/Downloads/OR_ABI-L2-MCMIPM2-M3_G16_s20181642040593_e20181642041050_c20181642041118.nc'
#file = '/home/scarani/Desktop/OR_ABI-L2-MCMIPF-M3_G16_s20181630045394_e20181630056161_c20181630056244.nc'

filename = os.path.join(os.path.dirname(ccrs.__file__),'data', 'netcdf', file)
nc = netcdf_dataset(filename)


earth_cir = 40074274.9
x_old = nc.variables['x'][:]
y_old = nc.variables['y'][:]
x_ = ((nc.variables['x'][:].data)/(2*np.pi))*earth_cir #radians to meters
y_ = ((nc.variables['y'][:].data)/(2*np.pi))*earth_cir #radians to meters
c = nc.variables['CMI_C13'][:]
data1 = nc.variables['CMI_C13']
sat = nc.variables
satvar = nc.variables.keys()
height = nc.variables['goes_imager_projection'].perspective_point_height


proj_var = nc.variables[nc.variables['CMI_C13'].grid_mapping]

globe = ccrs.Globe(ellipse='sphere', semimajor_axis=proj_var.semi_major_axis,
                   semiminor_axis=proj_var.semi_minor_axis)

proj = ccrs.Geostationary(central_longitude=-75,
                          sweep_axis='x', satellite_height=35786023.0, globe = globe)


#proj = ccrs.NearsidePerspective(central_longitude=-97.41666667, central_latitude=39.83333333,
#                                satellite_height= 35786023.0, globe = globe)

#proj = ccrs.LambertConformal(central_longitude=-75,
#                             central_latitude=0,
#                             globe=globe)


north = y_old.max()
south = y_old.min()
east = x_old.max()
west = x_old.min()


#north = proj.y_limits[1]
#south = proj.y_limits[0]
#east = proj.x_limits[1]
#west = proj.x_limits[0]

x, y = np.meshgrid(x_old, y_old)
fig = plt.figure(figsize=(15, 15))
ax = fig.add_subplot(1, 1, 1, projection=proj)
#ax = fig.add_subplot(1, 1, 1, projection=ccrs.LambertConformal())
#ax = plt.axes(projection=proj)
#ax.set_xlim(west,east)
#ax.set_ylim(south,north)

ax.pcolormesh(x,y,c, cmap='Greys')
#ax.add_feature(cfeature.STATES, linewidth=1, edgecolor='black')
#ax.coastlines(resolution = '10m', linewidth=10, edgecolor='black')
#ax.add_feature(cfeature.BORDERS, linewidth=1, edgecolor='black')
plt.show()
plt.close()

gc.collect()
end = timer()
print("Time: %s seconds"%round((end - start),2))