"""
Py-ART Animation

Choosing the radar volume from a Nexrad site over a time span.

Based on code by Scott Collis:
github.com/scollis/radar_in_the_cloud/blob/master/notebooks/Matthew.ipynb

Jonathan Helmus:
anaconda.org/jjhelmus/scipy2015_openaccessradar_jjh/notebook

memory fixes by Robert Jackson:
github.com/rcjackson/pyart_practice/blob/master/nexrad_animatedgif.py

and Zach Sherman helped designing the code:
github.com/zssherman/pyart_animation/blob/master/examples/pyart_animation_example.py

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
import cartopy.crs as ccrs
import cartopy.feature as cfeature

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


def get_grid(radar):
    """ Returns grid object from radar object. """
    grid = pyart.map.grid_from_radars(
        radar, grid_shape=(31, 500, 500),
        grid_limits=((0, 15000), (-200000, 0), (0, 200000)),
        fields=['reflectivity'], gridding_algo='map_gates_to_grid',
        h_factor=0., nb=0.6, bsp=1., min_radius=200.)
    return grid


# Plotting and creating an animation using the radar datas.
# Something close to home.
# Use the option of saying 'now' to retrieve current UTC.
my_data_keys = nexrad_site_datespan(start_date='20180530',
                                         start_date_time='000000',
                                         end_date='20180530',
                                         end_date_time='000400',
                                         site='kvnx')

# Showing that the nexrad_site_datespan
# function correctly retrieved all keys between each date.
print(my_data_keys)


for key in my_data_keys:
    localfile = tempfile.NamedTemporaryFile()
    key.get_contents_to_filename(localfile.name)
    
    radar = pyart.io.read(localfile.name)
    
    grid = get_grid(radar)
    
    

