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

#sleep 30s; shutdown -h now

baseurl = 'http://thredds-test.unidata.ucar.edu/thredds/catalog/satellite/goes16/GOES16/'

channel = '13'   #01-13
date = '20180624' #20180615 or current
sector = 'Mesoscale-1'   #Mesoscale-1, Mesoscale-2, CONUS, FullDisk
#sector = 'CONUS'


savelocation = '/home/scarani/Desktop/output/goes/' + sector + '/'

baseurl = 'http://thredds-test.unidata.ucar.edu/thredds/catalog/satellite/goes16/GOES16/'
cat = TDSCatalog(baseurl + str(sector) + '/Channel' + str(channel) + '/' + str(date) + 
                 '/catalog.xml')
data = cat.datasets

ds = cat.datasets[-120]
data = cat.datasets
# 'Mercator'
# 'Fixed Grid'

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
#bounds = (x.min(), x.max(), y.min(), y.max())
bounds = (x.min().values.sum(), x.max().values.sum(), y.min().values.sum(), y.max().values.sum())

#colormap = 'magma_r'
colormap = 'Greys'
#vmin = 0.03
#vmax = 1.2
vmin = 190
vmax = 305
#ax.set_extent(bounds, crs=ccrs.LambertConformal(central_longitude=-75.0, central_latitude=0.0))
im = ax.imshow(data_var[:], extent = bounds, origin='upper', cmap=colormap, vmin=vmin, vmax=vmax)
ax.coastlines(resolution='50m', color='black')
ax.add_feature(cfeature.STATES, linestyle=':')
ax.add_feature(cfeature.BORDERS, linewidth=2)


cbar_ticks = np.arange(vmin,vmax, round(((abs(vmax)-abs(vmin))/6),2))
cbar = fig.colorbar(im, ticks=cbar_ticks, orientation='horizontal', shrink = 0.6,
                    pad=.02)
cbar.ax.set_yticklabels(str(cbar_ticks))

if z.units == '1':
    cbar.set_label(z.standard_name, rotation=0, labelpad=5, fontsize = 11)
else:
    cbar.set_label(z.units, rotation=0, labelpad=5, fontsize = 11)

# Figure Text
txt = open('channel_title.txt', "r")
titles = txt.readlines()
ch = titles[ds.channel_id][:-1]
times = str(str(ds.time.values)[:-10]+ 'UTC')

ax.set_title('GOES 16: ' + sector + '\n' + ch + '\n' + times, fontsize = 13)

#plt.savefig(savelocation + str(times) + '_' + str(sector) + '_' + 
#            str(channel) + '.png', bbox_inches = 'tight', dpi = 300)
plt.show()
plt.close()
