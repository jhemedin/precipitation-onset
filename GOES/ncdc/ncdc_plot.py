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
from math import sin, cos, sqrt, atan2, radians

start = timer()

def _nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def deg2m(x,y):
#    point = proj.transform_point(x-.1,y+1.8,trans)
    point = proj.transform_point(x,y,trans)
    return(point[0],point[1])
    


# Presets
file = '/home/scarani/Desktop/data/goes/001/OR_ABI-L2-MCMIPM1-M3_G16_s20181732000338_e20181732000396_c20181732000472.nc'        
#file = '/home/scarani/Desktop/data/goes/001/OR_ABI-L2-MCMIPM1-M3_G16_s20181751724344_e20181751724401_c20181751724471.nc'
channel = 13

filename = os.path.join(os.path.dirname(ccrs.__file__),'data', 'netcdf', file)
nc = netcdf_dataset(filename)

sat_height = nc.variables['goes_imager_projection'].perspective_point_height


_x = nc.variables['x'] * sat_height
_y = nc.variables['y'] * sat_height
_c = nc.variables['CMI_C13'][:]
data = nc.variables['CMI_C13']

proj_var = nc.variables[data.grid_mapping]

globe = ccrs.Globe(datum='WGS84', ellipse='WGS84', semimajor_axis=proj_var.semi_major_axis,
                   semiminor_axis=proj_var.semi_minor_axis)

proj = ccrs.Geostationary(central_longitude=-75,sweep_axis='x',
                          satellite_height=sat_height, globe = globe)

#trans = ccrs.Miller(central_longitude=0)
trans = ccrs.PlateCarree(central_longitude=0)


lonlat = trans.transform_points(proj, _x, _y)


center = [-98.124,36.741]
extent = 2
zoom = (25/15)*extent

lim_nw = deg2m(center[0]-zoom,center[1]+extent)
lim_se = deg2m(center[0]+zoom,center[1]-extent)

lim = [_nearest(_x[:],lim_nw[0]),_nearest(_x[:],lim_se[0]),
       _nearest(_y[:],lim_nw[1]),_nearest(_y[:],lim_se[1])]

x = _x[lim[0]:lim[1]]
y = _y[lim[2]:lim[3]]
c = _c[lim[2]:lim[3],lim[0]:lim[1]]

#x = _x
#y = _y
#c = _c

time = nc['t']


fig = plt.figure(figsize=(15, 15))
ax = fig.add_subplot(1, 1, 1, projection=trans)
#ax.set_xlim(west,east)
#ax.set_ylim(south,north)

vmin = 198
vmax = 320

lcl = 269.5

colormap = colortables.get_colortable('ir_rgbv')

#colormap = pyart.graph.cm.NWSRef_r
colormap = pyart.graph.cm_colorblind.HomeyerRainbow_r
colors1 = plt.cm.Purples(np.linspace(.7, 1, int(((205-vmin)/(vmax-vmin))*1000)))
colors2 = colormap(np.linspace(.1, 1, int(((253-205)/(vmax-vmin))*1000)))
#colors2 = plt.cm.jet_r(np.linspace(.1, .9, int(((253-205)/(vmax-vmin))*1000)))
colors3 = plt.cm.Greys(np.linspace(.1, .6, int(((lcl-253)/(vmax-vmin))*1000)))
colors4 = plt.cm.Greys(np.linspace(.8, .85, int(((vmax-lcl)/(vmax-vmin))*1000)))
colors = np.vstack((colors1, colors2, colors3, colors4))
mymap = mcolors.LinearSegmentedColormap.from_list('my_colormap', colors)


im = ax.pcolormesh(x, y, c, cmap=plt.cm.Greys, vmin=vmin, vmax=vmax, transform = proj)
ax.add_feature(cfeature.STATES, linewidth=2, edgecolor='black')
ax.coastlines(resolution = '10m', linewidth=1, edgecolor='black')
ax.add_feature(cfeature.BORDERS, linewidth=1, edgecolor='black')
ax.add_feature(cfeature.LAKES, linewidth=20, edgecolor='black')
#ax.text(_x[_nearest(t_xy[:,0],-98.0)], _y[_nearest(t_xy[:,1],36.741)], 'KVNX', transform=proj, fontsize = 20)
kvnx = deg2m(-98.12799,36.741)
ax.plot(kvnx[0], kvnx[1], transform=proj, color='blue', linewidth=1, marker='o')

if4 = deg2m(-97.363834,36.578650)
ax.plot(if4[0], if4[1], transform=proj, color='green', linewidth=1, marker='o')

if5 = deg2m(	-97.593936,	36.491178)
ax.plot(if5[0], if5[1], transform=proj, color='green', linewidth=1, marker='o')

if6 = deg2m(	-97.547446,36.767569)
ax.plot(if6[0], if6[1], transform=proj, color='green', linewidth=1, marker='o')


cbar_ticks = np.arange(vmin,vmax, round(((abs(vmax)-abs(vmin))/6),2))
cbar = fig.colorbar(im, ticks=cbar_ticks, orientation='horizontal',
                    shrink = 0.6, pad=.02)
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