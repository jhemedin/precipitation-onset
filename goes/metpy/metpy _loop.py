from datetime import datetime
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from siphon.catalog import TDSCatalog
from metpy.plots import colortables
import xarray as xr
from xarray.backends import NetCDF4DataStore
import time
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def sat_plot(ds):
    timestamp = datetime.strptime(ds.start_date_time, '%Y%j%H%M%S')
    print(timestamp)
    data_var = ds.metpy.parse_cf('Sectorized_CMI')

    sat_height = ds.satellite_altitude
    
    x = (ds['x'].data * sat_height)/1000000
    y = (ds['y'].data * sat_height)/1000000
    c = data_var[:].data
    
    globe = ccrs.Globe(ellipse='sphere', semimajor_axis=6378137.0,
                       semiminor_axis=6356752.31414)
    
    proj = ccrs.Geostationary(central_longitude=-75,
                              sweep_axis='x', satellite_height=sat_height, globe = globe)
    
    trans = ccrs.Miller(central_longitude=-75)
    
    fig = plt.figure(figsize=(15, 15))
    ax = fig.add_subplot(1, 1, 1, projection=trans)
    
    vmin = .012
    vmax = .8
    
    colormap = 'Greys_r'
    
    im = ax.pcolormesh(x,y,c, cmap=colormap, vmin=vmin, vmax=vmax, transform = proj)
    ax.add_feature(cfeature.STATES, linewidth=2, edgecolor='black')
    ax.coastlines(resolution = '10m', linewidth=1, edgecolor='black')
    ax.add_feature(cfeature.BORDERS, linewidth=1, edgecolor='black')
    
    # Colorbar
    cbar_ticks = np.arange(vmin,vmax, round(((abs(vmax)-abs(vmin))/6),2))
    cbar = fig.colorbar(im, ticks=cbar_ticks, orientation='horizontal', shrink = 0.6,
                        pad=.02)
    cbar.ax.set_yticklabels(str(cbar_ticks))
    
    cbar_label = data_var.standard_name
    
    cbar.set_label(cbar_label, rotation=0, labelpad=5, fontsize = 13)
    
    cbar.ax.invert_yaxis() 
    
    # Figure Text
    txt = open('channel_title.txt', "r")
    titles = txt.readlines()
    ch = titles[int(channel)][:-1]
    time = str(timestamp.strftime('%Y-%m-%dT%H:%M:%SUTC'))
    orbital_slot = ds.satellite_id
    sector = ds.source_scene
    savetime = timestamp.strftime('%Y%m%d%H%M%S')
    
    ax.set_title(orbital_slot + ': ' + sector + '\n' + ch + '\n' + str(time), fontsize = 15)
    
    savelocation = '/home/scarani/Desktop/output/goes/' + sector + '/'
    
    plt.savefig(savelocation + str(savetime) + '_' + str(channel) + '_' + 
                str(sector) + '.png', bbox_inches = 'tight', dpi = 300)

    plt.show()
    plt.close()
    
    del fig

channel = '02'   #01-13
date = '20180720' #20180615 or current
#date = 'current'
sector = 'Mesoscale-2'   #Mesoscale-1, Mesoscale-2, CONUS, FullDisk


savelocation = '/home/scarani/Desktop/output/goes/' + sector + '/'

baseurl = 'http://thredds-test.unidata.ucar.edu/thredds/catalog/satellite/goes16/GOES16/'
cat = TDSCatalog(baseurl + str(sector) + '/Channel' + str(channel) + '/' + str(date) + 
                 '/catalog.xml')
data = cat.datasets


for i in range (-1,-(len(data)),-1):
#for i in range (-1,-2,-1):
    ds = data[i]
    print(ds)
    ds = ds.remote_access(service='OPENDAP')
    ds = NetCDF4DataStore(ds)
    ds = xr.open_dataset(ds)
    
    sat_plot(ds)


