from datetime import datetime
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from siphon.catalog import TDSCatalog
import metpy
from metpy.plots import colortables
import xarray as xr
from xarray.backends import NetCDF4DataStore
import cartopy.crs as ccrs
import numpy as np

# Presets
baseurl = 'http://thredds-test.unidata.ucar.edu/thredds/catalog/satellite/goes16/GOES16/'

channel = '13'   #01-13
date = 'current' #'current'   #20180615 or current
sector = 'Mesoscale-2'   #Mesoscale-1, Mesoscale-2, CONUS, FullDisk

# Import data
savelocation = '/home/scarani/Desktop/output/goes/' + sector + '/'
cat = TDSCatalog(baseurl + str(sector) + '/Channel' + str(channel) + '/' + str(date) + 
                 '/catalog.xml')


ds = cat.datasets[-1]
ds = ds.remote_access(service='OPENDAP')
ds = NetCDF4DataStore(ds)
ds = xr.open_dataset(ds)

print(ds.projection)
timestamp = datetime.strptime(ds.start_date_time, '%Y%j%H%M%S')
data_var = ds.metpy.parse_cf('Sectorized_CMI')

x = ds['x']
y = ds['y']
z = data_var[:]

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(1, 1, 1, projection=data_var.metpy.cartopy_crs)
bounds = (x.min(), x.max(), y.min(), y.max())

# Plot
colormap = 'Greys'
vmin = z.min()
vmax = z.max()

im = ax.imshow(data_var[:], extent = bounds, origin='upper', cmap=colormap, vmin=vmin, vmax=vmax, zorder = 1)

ax.coastlines(resolution='50m', color='black', zorder = 2)
ax.add_feature(cfeature.STATES, linestyle=':', zorder = 2)
ax.add_feature(cfeature.BORDERS, linewidth=2, zorder = 2)

# Figure Text
times = str(str(ds.time.values)[:-10]+ 'UTC')

ax.set_title('GOES 16: ' + sector + '\n' + 'Ch.13 Clean IR Longwave Band' + '\n' + times, fontsize = 13)

plt.show()
plt.close()