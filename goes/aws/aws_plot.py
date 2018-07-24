from boto.s3.connection import S3Connection
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from netCDF4 import Dataset as netcdf_dataset
import numpy as np
import gc
from timeit import default_timer as timer
from datetime import date, datetime, timedelta
start = timer()

file = '/home/scarani/Desktop/data.nc'


def _nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

filename = os.path.join(os.path.dirname(ccrs.__file__),'data', 'netcdf', file)
nc = netcdf_dataset(filename)

sat_height = nc.variables['goes_imager_projection'].perspective_point_height


_x = nc.variables['x'] * sat_height
_y = nc.variables['y'] * sat_height
_c = nc.variables['CMI_C13'][:]

lim = [_nearest(_x,-2304620.0),_nearest(_x,-1605218.0)
        ,_nearest(_y,3687472.0),_nearest(_y,3346709.0)]

x = _x[lim[0]:lim[1]]
y = _y[lim[2]:lim[3]]
c = _c[lim[2]:lim[3],lim[0]:lim[1]]
data = nc.variables['CMI_C13']
satvar = nc.variables.keys()
time = nc['t']


proj_var = nc.variables[data.grid_mapping]

globe = ccrs.Globe(ellipse='sphere', semimajor_axis=proj_var.semi_major_axis,
                   semiminor_axis=proj_var.semi_minor_axis)

proj = ccrs.Geostationary(central_longitude=-75,
                          sweep_axis='x', satellite_height=sat_height, globe = globe)

trans = ccrs.Miller(central_longitude=-75)


fig = plt.figure(figsize=(15, 15))
ax = fig.add_subplot(1, 1, 1, projection=proj)

vmin = 198
vmax = 325
colormap = 'Greys'

im = ax.pcolormesh(x,y,c, cmap=colormap, vmin=vmin, vmax=vmax)
ax.add_feature(cfeature.STATES, linewidth=2, edgecolor='black')
ax.coastlines(resolution = '10m', linewidth=1, edgecolor='black')
ax.add_feature(cfeature.BORDERS, linewidth=1, edgecolor='black')


cbar_ticks = np.arange(vmin,vmax, round(((abs(vmax)-abs(vmin))/6),2))
cbar = fig.colorbar(im, ticks=cbar_ticks, orientation='horizontal', shrink = 0.6,
                    pad=.02)
cbar.ax.set_yticklabels(str(cbar_ticks))

cbar.set_label(data.units, rotation=0, labelpad=5, fontsize = 13)

# Figure Text
txt = open('channel_title.txt', "r")
titles = txt.readlines()
channel = data.ancillary_variables[-2:]
ch = titles[int(channel)][:-1]
#times = str(str(.time.values)[:-10]+ 'UTC')
orbital_slot = nc.orbital_slot

fmt = '%Y%m%d_%H%M%S'
epoch = '20000101_120000'

sd = datetime.strptime(epoch, fmt)
times = sd + timedelta(seconds = int(time[0].data))
time_title = times.strftime('%Y-%m-%dT%H:%M:%SUTC')
savetime = times.strftime('%Y%m%d%H%M%S')

sector = '***sector error***'
if nc.dataset_name[15:-58] == 'M1':
    sector = 'Mesoscale-1'

if nc.dataset_name[15:-58] == 'M2':
    sector = 'Mesoscale-2'

if nc.dataset_name[15:-58] == 'F':
    sector = 'Disk'

if nc.dataset_name[15:-58] == 'C':
    sector = 'CONUS'

ax.set_title(orbital_slot + ': ' + sector + '\n' + ch + '\n' + str(time_title), fontsize = 17)

savelocation = '/home/scarani/Desktop/output/goes/' + sector + '/'

plt.savefig(savelocation + str(savetime) + '_' + str(sector) + '_' + 
            str(channel) + '.png', bbox_inches = 'tight', dpi = 300)


plt.show()
plt.close()

gc.collect()
end = timer()
print("Time: %s seconds"%round((end - start),2))