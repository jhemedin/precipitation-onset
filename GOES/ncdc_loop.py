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

filelist = sorted(os.listdir('/home/scarani/Desktop/data/goes/001/'))
channel = 2



for i in range(1200,1501,1):
    
    print(i)
    
    file = str('/home/scarani/Desktop/data/goes/001/' + filelist[i])
    
    filename = os.path.join(os.path.dirname(ccrs.__file__),'data', 'netcdf', file)
    nc = netcdf_dataset(filename)
    
    sat_height = nc.variables['goes_imager_projection'].perspective_point_height
    
    
    x = nc.variables['x'][:].data * sat_height
    y = nc.variables['y'][:].data * sat_height
    c = nc.variables['Rad'][:]
    data = nc.variables['Rad']
    satvar = nc.variables.keys()
    time = nc['t']
    
    proj_var = nc.variables[nc.variables['Rad'].grid_mapping]
    
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
    
    vmin = 15
    vmax = 580
    colormap = 'Greys_r'
    
    im = ax.pcolormesh(x,y,c, cmap=colormap, vmin=vmin, vmax=vmax)
    ax.add_feature(cfeature.STATES, linewidth=2, edgecolor='black')
    ax.coastlines(resolution = '10m', linewidth=1, edgecolor='black')
    ax.add_feature(cfeature.BORDERS, linewidth=1, edgecolor='black')
    
    
    cbar_ticks = np.arange(vmin,vmax, round(((abs(vmax)-abs(vmin))/6),2))
    cbar = fig.colorbar(im, ticks=cbar_ticks, orientation='horizontal', shrink = 0.6,
                        pad=.02)
    cbar.ax.set_yticklabels(str(cbar_ticks))
    
    cbar_label = str(data.standard_name + '\n' + data.long_name)
    
    cbar.set_label(cbar_label, rotation=0, labelpad=5, fontsize = 13)
    
    # Figure Text
    txt = open('channel_title.txt', "r")
    titles = txt.readlines()
    ch = titles[int(channel)][:-1]
    time = str(nc.time_coverage_start[:-3] + 'UTC')
    orbital_slot = nc.orbital_slot
    
    fmt = '%Y-%m-%dT%H:%M:%SUTC'
    
    sd = datetime.strptime(time, fmt)
    savetime = sd.strftime('%Y%m%d%H%M%S')
    
    dataset_name = nc.dataset_name[14:-61]
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
    
    plt.savefig(savelocation + str(savetime) + '_' + str(sector) + '_' + 
                str(channel) + '.png', bbox_inches = 'tight', dpi = 300)
    
    
    plt.show()
    plt.close()
    
    gc.collect()
end = timer()
print("Time: %s seconds"%round((end - start),2))

exit()