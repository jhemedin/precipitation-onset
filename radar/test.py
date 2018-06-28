from boto.s3.connection import S3Connection
import pyart
import gzip
from matplotlib import pyplot as plt
from datetime import date, datetime, timedelta
from matplotlib import animation
import tempfile
import numpy as np
import pandas as pd
import shutil
import os
import urllib
import cartopy

temp_dir = '/home/scarani/Desktop/test'

def _nearestDate(dates, pivot):
    return min(dates, key=lambda x: abs(x - pivot))

start_date='20161019'
start_date_time='125000'
end_date='20161019'
end_date_time='160000'
site='KLOT' # Capitalized letters

fmt = '%Y%m%d_%H%M%S'

sd = datetime.strptime(start_date + '_' + start_date_time, fmt)
ed = datetime.strptime(end_date + '_' + end_date_time, fmt)

t_delta = ed - sd

conn = S3Connection(anon=True)
bucket = conn.get_bucket('noaa-nexrad-level2')

sdkey = bucket.get_all_keys(prefix = str(sd.strftime('%Y/%m/%d/') 
                                        + site + '/'))
edkey = bucket.get_all_keys(prefix = str(ed.strftime('%Y/%m/%d/') 
                                        + site + '/'))

key = bucket.get_all_keys()

keys = []

for a in range(0, (t_delta.days+1), 1):
    dif = ed - timedelta(days=a)
    print(dif.strftime('%Y-%m-%d'))
    edkey = bucket.get_all_keys(prefix = str(dif.strftime('%Y/%m/%d/') 
                                        + site + '/'))
    for i in range(0, len(edkey), 1):
        keys.append(edkey[i])

print(len(keys))

"""
for i in range (0, len(keys),1):
    url = keys[i].generate_url(expires_in=0, query_auth=False, force_http=True)
    testfile = urllib.URLopener()
    testfile.retrieve('url', temp_dir + 'file.gz')
    """

#list every date in str
#search for closest datetime
#find place and then subtrack from both dates
#_nearestDate(lsitj,sd)


#sdkey[1].generate_url(expires_in=0, query_auth=False, force_http=True)
#shutil.rmtree(temp_dir)
#os.makedirs(temp_dir)
    
for key in keys:
    localfile = tempfile.NamedTemporaryFile()
    key.get_contents_to_filename(localfile.name)
    
    radar = pyart.io.read(localfile.name)
    
    
    #Plot Bounds
    centerx = -95.3632700
    centery = 29.4718835
    zoom = 1.5
    
    xm = 25/18
    min_lon = centerx - (zoom*xm)
    min_lat = centery - zoom
    max_lon = centerx + (zoom*xm)
    max_lat = centery + zoom
    
    lal = np.arange(min_lat, max_lat, .5)
    lol = np.arange(min_lon, max_lon, .5)
    
    
    display = pyart.graph.RadarMapDisplayCartopy(radar)
    lat_0 = display.loc[0]
    lon_0 = display.loc[1]
    proj = cartopy.crs.Mercator(
                    central_longitude=lon_0,
                    min_latitude=min_lat, max_latitude=max_lat)
    
    saveloc = '/home/scarani/Desktop/output/radar/'
    
    #Plot Relfectivity
    fig = plt.figure(figsize = [20,8])
    display.plot_ppi_map('reflectivity', sweep = 0, projection=proj, resolution = '10m',
                         vmin = -8, vmax = 64, mask_outside = False,
                         cmap = pyart.graph.cm.NWSRef,
                         min_lat = min_lat, min_lon = min_lon,
                         max_lat = max_lat, max_lon = max_lon,
                         lat_lines = lal, lon_lines = lol)
    gl = display.ax.gridlines(draw_labels=True,
                              linewidth=2, color='gray', alpha=0.5, linestyle='--')
    plt.savefig(saveloc + radar.time['units'].split()[2] +'.png', bbox_inches = 'tight')
    plt.close()
    del radar
    
    #print(radar.fixed_angle['data'])
    
    
    
    
    