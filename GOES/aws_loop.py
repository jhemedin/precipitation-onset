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
from boto.s3.connection import S3Connection
import gzip
from matplotlib import pyplot as plt
import tempfile
import pandas as pd
import cartopy
from metpy.plots import colortables
start = timer()

start_date='20180621'
start_date_time='130000'
end_date='20180621'
end_date_time='140000'
scan= 'M!'

savelocation = '/home/scarani/Desktop/output/goes/Mesoscale-1/'
#savelocation = '/home/scarani/Desktop/output/goes/Chicago_20180621-22/'


def _nearestDate(dates, pivot):
    return min(dates, key=lambda x: abs(x - pivot))

def plotsat():
    nc = netcdf_dataset(localfile.name)
    
    sat_height = nc.variables['goes_imager_projection'].perspective_point_height
    
    
    x = nc.variables['x'][:].data * sat_height
    y = nc.variables['y'][:].data * sat_height
    data = nc.variables['CMI_C02']
    c = data[:]
    satvar = nc.variables.keys()
    time = nc['t']
    
    proj_var = nc.variables[nc.variables['CMI_C13'].grid_mapping]
    
    globe = ccrs.Globe(ellipse='sphere', semimajor_axis=proj_var.semi_major_axis,
                       semiminor_axis=proj_var.semi_minor_axis)
    
    proj = ccrs.Geostationary(central_longitude=-75,
                              sweep_axis='x', satellite_height=sat_height, globe = globe)
    
    
    north = y.max()
    south = y.min()
    east = x.max()
    west = x.min()
    
    
    x, y = np.meshgrid(x, y)
    fig = plt.figure(figsize=(15, 15))
    ax = fig.add_subplot(1, 1, 1, projection=proj)
    ax.set_xlim(west,east)
    ax.set_ylim(south,north)
    
#    vmin = 190 #13
#    vmax = 305 #13
#    colormap = 'Greys' #13
    vmin = 0.03 #02
    vmax = 1.2 #02
    colormap = 'Greys_r' #02
    
#    colormap = colortables.get_colortable('WVCIMSS')
    
    im = ax.pcolormesh(x,y,c, cmap=colormap, vmin=vmin, vmax=vmax)
    ax.add_feature(cfeature.STATES, linewidth=2, edgecolor='black')
    ax.coastlines(resolution = '10m', linewidth=1, edgecolor='black')
    ax.add_feature(cfeature.BORDERS, linewidth=1, edgecolor='black')
    
    
    cbar_ticks = np.arange(vmin,vmax, round(((abs(vmax)-abs(vmin))/6),2))
    cbar = fig.colorbar(im, ticks=cbar_ticks, orientation='horizontal', shrink = 0.6,
                        pad=.02)
    cbar.ax.set_yticklabels(str(cbar_ticks))
    
    print(data.units)
    
    if data.units == '1':
        cbar.set_label(data.standard_name, rotation=0, labelpad=5, fontsize = 13)
    else:
        cbar.set_label(data.units, rotation=0, labelpad=5, fontsize = 13)
    
    print(data.units)
    
    # Figure Text
    txt = open('/home/scarani/Desktop/precipitation-onset/GOES/channel_title.txt', "r")
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
    
    print(nc.dataset_name[15:-58])
    
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
    
    
    plt.savefig(savelocation + str(savetime) + '_' + str(scan) + '_' + 
                str(channel) + '.png', bbox_inches = 'tight', dpi = 300)
    
    
    plt.show()
    plt.close()
    
    gc.collect()
    
    mid = timer()
    print(round((mid - start)/60,2))


#ABI-L2-MCMIPM/2018/175/17/OR_ABI-L2-MCMIPM1-M3_G16_s20181751706344_e20181751706401_c20181751706475.nc
#range(0,60,1)

fmt = '%Y%m%d_%H%M%S'

sd = datetime.strptime(start_date + '_' + start_date_time, fmt)
ed = datetime.strptime(end_date + '_' + end_date_time, fmt)
sd_ = datetime.strptime(start_date, '%Y%m%d')
ed_ = datetime.strptime(end_date, '%Y%m%d')

t_delta = ed_ - sd_

conn = S3Connection(anon=True)
bucket = conn.get_bucket('noaa-goes16')

keys = []

file = 'ABI-L2-MCMIPM' + (sd.strftime('/%Y/%j/%H/'))

#sdfileprefix = str('ABI-L2-MCMIPM' + (sd.strftime('/%Y/%j/%H/') 
#                    + 'OR_ABI-L2-MCMIP' + scan + '-M3_G16_'))
#sdkey = bucket.get_all_keys(prefix = sdfileprefix)

if scan == 'C':
    scanprefix = scan

if scan == 'F':
    scanprefix = scan
    
if scan == 'M1':
    scanprefix = 'M'
    
if scan == 'M2':
    scanprefix = 'M'

for i in range(t_delta.days,-1,-1):
    e_d = ed - timedelta(days=i)
    print(e_d)
    
    for a in range(0,24,1):
        edfileprefix = str('ABI-L2-MCMIP' + scanprefix + (e_d.strftime('/%Y/%j/') + str(a).zfill(2)
                        + '/' + 'OR_ABI-L2-MCMIP' + scan + '-M3_G16_'))
    
    #    edfileprefix = str('ABI-L2-MCMIPM' + ((e_d.strftime('/%Y/%j/'))))
        edkey = bucket.get_all_keys(prefix = edfileprefix)
        
        for b in range(0,len(edkey),1):
            keys.append(edkey[b])

keysdict = {}

for i in keys:
    keysdict[str(i)[-34:][:-21]] = i
    
keyslist = list(keysdict.keys())

datekeyslist = []
    
for i in keyslist:
    datekeyslist.append(datetime.strptime(i, '%Y%j%H%M%S'))
    
_sd = sd.strftime('%Y%j%H%M%S')
_ed = ed.strftime('%Y%j%H%M%S')
    

sdsatdatetime = _nearestDate(datekeyslist, sd)
edsatdatetime = _nearestDate(datekeyslist, ed)

sdsatdate = sdsatdatetime.strftime('%Y%j%H%M%S')
edsatdate = edsatdatetime.strftime('%Y%j%H%M%S')

sdkey = keysdict[sdsatdate]
edkey = keysdict[edsatdate]

sdindex = keys.index(sdkey)
edindex = keys.index(edkey)

for i in range(sdindex,edindex+1,1):
    localfile = tempfile.NamedTemporaryFile()
    keys[i].get_contents_to_filename(localfile.name)
    plotsat()
    
end = timer()
print("Time: %s seconds"%round((end - start),2))


#ffmpeg -framerate 17 -pattern_type glob -i '/*.png' -movflags faststart -pix_fmt yuv420p -vf 'scale=trunc(iw/2)*2:trunc(ih/2)*2' -y '/home/scarani/Desktop/output/goes/animation.mp4'