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

start = timer()

def _nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


# Presets
file = '/home/scarani/Desktop/data/goes/001/OR_ABI-L2-MCMIPM1-M3_G16_s20181761156347_e20181761156404_c20181761156475.nc'        
channel = 13

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


north = y.max()
south = y.min()
east = x.max()
west = x.min()


fig = plt.figure(figsize=(15, 15))
ax = fig.add_subplot(1, 1, 1, projection=trans)
#ax.set_xlim(west,east)
#ax.set_ylim(south,north)

vmin = 198
vmax = 320

lcl = 268

colormap = colortables.get_colortable('ir_rgbv')

colormap = pyart.graph.cm.NWSRef_r

colors1 = plt.cm.Greys(np.linspace(.7, 1, ((205-vmin)/(vmax-vmin))*1000))
colors2 = colormap(np.linspace(.1, 1, ((253-205)/(vmax-vmin))*1000))
colors3 = plt.cm.Greys(np.linspace(.2, .7, ((lcl-253)/(vmax-vmin))*1000))
colors4 = plt.cm.Greys(np.linspace(.8, .9, ((vmax-lcl)/(vmax-vmin))*1000))
colors = np.vstack((colors1, colors2, colors3, colors4))
mymap = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors)


im = ax.pcolormesh(x,y,c, cmap=mymap, vmin=vmin, vmax=vmax, transform = proj)
ax.add_feature(cfeature.STATES, linewidth=2, edgecolor='black')
ax.coastlines(resolution = '10m', linewidth=1, edgecolor='black')
ax.add_feature(cfeature.BORDERS, linewidth=1, edgecolor='black')
#ax.set_xlim(-2665343.0, -1665338.4)
#ax.set_ylim(3008030.2,4008034.8)


cbar_ticks = np.arange(vmin,vmax, round(((abs(vmax)-abs(vmin))/6),2))
cbar = fig.colorbar(im, ticks=cbar_ticks, orientation='horizontal', shrink = 0.6,
                    pad=.02)
cbar.ax.set_yticklabels(str(cbar_ticks))

cbar_label = str(data.units)

cbar.set_label(cbar_label, rotation=0, labelpad=5, fontsize = 13)

cbar.ax.invert_yaxis() 

# Figure Text
txt = open('channel_title.txt', "r")
titles = txt.readlines()
ch = titles[int(channel)][:-1]
time = str(nc.time_coverage_start[:-3] + 'UTC')
orbital_slot = nc.orbital_slot

fmt = '%Y-%m-%dT%H:%M:%SUTC'

sd = datetime.strptime(time, fmt)
savetime = sd.strftime('%Y%m%d%H%M%S')

dataset_name = nc.dataset_name[15:17]
sector = '***sector error***'

if dataset_name == 'M1':
    sector = 'Mesoscale-1'

if dataset_name == 'M2':
    sector = 'Mesoscale-2'

if dataset_name == 'F-':
    sector = 'Full-Disk'

if dataset_name == 'C-':
    sector = 'CONUS'

ax.set_title(orbital_slot + ': ' + sector + '\n' + ch + '\n' + str(time), fontsize = 15)

savelocation = '/home/scarani/Desktop/output/goes/' + sector + '/'

#plt.savefig(savelocation + str(savetime) + '_' + str(sector) + '_' + 
#            str(channel) + '.png', bbox_inches = 'tight', dpi = 300)


plt.show()
plt.close()

gc.collect()
end = timer()
print("Time: %s min"%round((end - start)/60,2))