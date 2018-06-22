11from datetime import datetime
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from siphon.catalog import TDSCatalog
from metpy.plots import colortables
import xarray as xr
from xarray.backends import NetCDF4DataStore
import time

def sat_plot(ds):
    timestamp = datetime.strptime(ds.start_date_time, '%Y%j%H%M%S')
    print(timestamp)
    data_var = ds.metpy.parse_cf('Sectorized_CMI')
    
    x = ds['x']
    y = ds['y']
    z = data_var[:]
    
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1, projection=data_var.metpy.cartopy_crs)
    bounds = (x.min(), x.max(), y.min(), y.max())
    #colormap = ctables.get_colortable('NWSReflectivity')
    colormap = 'magma_r'
#    colormap = 'Greys_r'
    im = ax.imshow(data_var[:], extent=bounds, origin='upper', cmap = colormap,
                   vmin = 150, vmax = 310)
    
    #ax.set_xticks(np.arange(westlimit,eastlimit, 4.0))
    #ax.set_yticks(np.arange(southlimit,northlimit, 4.0))
    
#    wv_norm, wv_cmap = colortables.get_with_range('WVCIMSS_r', 195, 265)
#    im.set_cmap(wv_cmap)
#    im.set_norm(wv_norm)
    
    ax.coastlines(resolution='50m', color='black')
    ax.add_feature(cfeature.STATES, linestyle=':')
    ax.add_feature(cfeature.BORDERS, linewidth=2)
    
    
    
    # Figure Text
    txt = open('channel_title.txt', "r")
    titles = txt.readlines()
    ch = titles[ds.channel_id][:-1]
    times = str(str(ds.time.values)[:-10]+ 'UTC')
    
    ax.set_title(ch + '\n' + sector + '\n' + times, fontsize = 13)
    
    plt.savefig(savelocation + str(times) + '_' + str(sector) + '_' + 
                str(channel) + '.png', bbox_inches = 'tight', dpi = 300)
    plt.show()
    plt.close()

channel = '13'   #01-13
date = 20180615 #'currentcurrent'   #20180615 or current
sector = 'Mesoscale-1'   #Mesoscale-1, Mesoscale-2, CONUS, FullDisk


savelocation = '/home/scarani/Desktop/output/goes/' + sector + '/'

baseurl = 'http://thredds-test.unidata.ucar.edu/thredds/catalog/satellite/goes16/GOES16/'
cat = TDSCatalog(baseurl + str(sector) + '/Channel' + str(channel) + '/' + str(date) + 
                 '/catalog.xml')
data = cat.datasets


for i in range (-1,-(len(data)),-1):
#for i in range (-1,-30,-1):
    start = time.time()
    ds = data[i]
    print(ds)
    ds = ds.remote_access(service='OPENDAP')
    ds = NetCDF4DataStore(ds)
    ds = xr.open_dataset(ds)
    
    if ds.projection == 'Mercator':
        sat_plot(ds)
        
    if ds.projection == 'Lambert Conformal':
        sat_plot(ds)
    
    end = time.time()
    dif = (end - start)
    split = round(dif, 2)
    print(str(split) + ' sec.')
    time_left = (((len(data)+i)/2)*dif)/60
    print(str(round(time_left,2)) + ' min.')


