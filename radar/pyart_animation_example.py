"""
Py-ART Animation

Choosing the radar volume from a Nexrad site over a time span.

Based on code by Scott Collis:
https://github.com/scollis/radar_in_the_cloud/blob/master/notebooks/Matthew.ipynb

Jonathan Helmus:
https://anaconda.org/jjhelmus/scipy2015_openaccessradar_jjh/notebook

and memory fixes by Robert Jackson:
https://github.com/rcjackson/pyart_practice/blob/master/nexrad_animatedgif.py

Note: NEXRAD s3 files are set in UTC.

"""

from boto.s3.connection import S3Connection
import pyart
import gzip
from matplotlib import pyplot as plt
from datetime import date, datetime, timedelta
from matplotlib import animation
import tempfile
import numpy as np
import pandas as pd
import cartopy

# Function for pulling all keys between two dates at a chosen nexrad site.
def nexrad_site_datespan(start_date=None, start_date_time=None,
                         end_date=None, end_date_time=None, site=None):

    """
    Get all volumes of NEXRAD data between two particular datetimes.
    Parameters
    ----------
    start_date : string
        Eight number date, for example '20150623'
    start_date_time : string
        Six number time, for example '145501'
    end_date : string
        Eight number date or 'Now' to retrieve current UTC
    end_date_time : string, optional if end_date = 'Now'
        Six number time
    site : string
        Four letter radar designation in, for example 'KJAX'

    Reference
    ---------
    Helmus, J.J. & Collis, S.M., (2016). The Python ARM Radar Toolkit
    (Py-ART), a Library for Working with Weather Radar Data in the
    Python Programming Language. Journal of Open Research Software.
    4(1), p.e25. DOI: http://doi.org/10.5334/jors.119

    """

    fmt = '%Y%m%d_%H%M%S'

    # Allows for the choice of now for the end date so current UTC is pulled.
    if end_date.upper() == 'NOW':
        e_d_selected = datetime.utcnow()
    else:
        e_d_selected = datetime.strptime(end_date + '_' + end_date_time, fmt)

    s_d = datetime.strptime(start_date + '_' + start_date_time, fmt)
    e_d_fixed = e_d_selected + timedelta(days=1)

    if s_d > e_d_selected:
            raise ValueError('You provided a start date' 
                             ' that comes after the end date.')

    times = []
    for timestamp in datespan((s_d), (e_d_fixed), delta=timedelta(days=1)):
        time = timestamp
        times += [datetime.strftime(time, '%Y/%m/%d/' + site.upper())]

    conn = S3Connection(anon=True)
    bucket = conn.get_bucket('noaa-nexrad-level2')

    # Get a list of files
    keys = []
    datetimes = []
    for time in times:
        bucket_list = list(bucket.list(time))
        for i in range(len(bucket_list)):
            this_str = str(bucket_list[i].key)
            if 'gz' in this_str:
                endme = this_str[-22:-3]
                fmt = '%Y%m%d_%H%M%S_V06'
                dt = datetime.strptime(endme, fmt)
                datetimes.append(dt)
                keys.append(bucket_list[i])

            if this_str[-3::] == 'V06':
                endme = this_str[-19::]
                fmt = '%Y%m%d_%H%M%S_V06'
                dt = datetime.strptime(endme, fmt)
                datetimes.append(dt)
                keys.append(bucket_list[i])

    # Code belows chooses all keys between the user's dates.

    d = {'keys': keys}
    key_object = pd.DataFrame(data=d, index=pd.to_datetime(datetimes))

    selected_keys = key_object.loc[s_d: e_d_selected, :]
    # radar_datetimes = selected_keys.index.tolist()
    data_keys = selected_keys['keys'].tolist()
    return data_keys

def datespan(start_date, end_date, delta=timedelta(days=1)):
    current_date = start_date
    while current_date < end_date:
        yield current_date
        current_date += delta


# Plotting and creating an animation using the radar datas.
# Something close to home.
# Use the option of saying 'now' to retrieve current UTC.
my_data_keys = nexrad_site_datespan(start_date='20180621',
                                         start_date_time='090000',
                                         end_date='20180621',
                                         end_date_time='190000',
                                         site='khgx')

# Showing that the nexrad_site_datespan
# function correctly retrieved all keys between each date.
print(my_data_keys)


for key in my_data_keys:
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
#    gl = display.ax.gridlines(draw_labels=True,
#                              linewidth=2, color='gray', alpha=0.5, linestyle='--')
    plt.savefig(saveloc + radar.time['units'].split()[2] +'.png', bbox_inches = 'tight')
    plt.close()
    del radar
    
    print(radar.fixed_angle['data'])