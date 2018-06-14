from datetime import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib import patheffects
from netCDF4 import Dataset
import numpy as np
from scipy import interpolate
from siphon.catalog import TDSCatalog
import metpy
import xarray as xr
from xarray.backends import NetCDF4DataStore

baseurl = 'http://thredds-test.unidata.ucar.edu/thredds/catalog/satellite/goes16/GOES16/'

cat = TDSCatalog(baseurl + 'Mesoscale-1/Channel13/20180614/catalog.xml')
#cat = TDSCatalog(baseurl + 'CONUS/Channel14/current/catalog.xml')
#ds = cat.datasets.filter_time_nearest(datetime.now())
#ds = cat.datasets[-2]

for i in range (-1,-1000,-2):
    ds = cat.datasets[i]
    print(ds.name)
    ds = ds.remote_access(service='OPENDAP')
    ds = NetCDF4DataStore(ds)
    ds = xr.open_dataset(ds)
    timestamp = datetime.strptime(ds.start_date_time, '%Y%j%H%M%S')
    data_var = ds.metpy.parse_cf('Sectorized_CMI')
    
    x = ds['x']
    y = ds['y']
    
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1, projection=data_var.metpy.cartopy_crs)
    bounds = (x.min(), x.max(), y.min(), y.max())
    im = ax.imshow(data_var[:], extent=bounds, origin='upper')
    ax.coastlines(resolution='50m', color='black')
    ax.add_feature(cfeature.STATES, linestyle=':')
    ax.add_feature(cfeature.BORDERS, linewidth=2)
    
    # Add text (aligned to the right); save the returned object so we can manipulate it.
    txt = open('channel_title.txt', "r")
    titles = txt.readlines()
    ch = titles[ds.channel_id][:-1]
    times = str(str(ds.time.values)[:-10]+ 'UTC')
    
    ax.set_title(ch + '\n' + times, fontsize = 15)
    
    
    savelocation = '/home/scarani/Desktop/output/goes/meso-1/'
    plt.savefig(savelocation + times + '.png', bbox_inches = 'tight', dpi = 300)
    plt.close()