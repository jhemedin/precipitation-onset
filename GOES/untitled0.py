import xarray
import pyart
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
from tint.data_utils import get_nexrad_keys, read_nexrad_key
from tint import Cell_tracks, animate
from tint.visualization import embed_mp4_as_gif
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
from glob import glob
import os
import pyart
from tint.tracks import Cell_tracks
from tint.visualization import animate

# Function for pulling all keys between two dates at a chosen nexrad site.
def nexrad_site_datespan(start_date=None, start_date_time=None,
                         end_date=None, end_date_time=None, site=None):
    
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

###############################################################################

my_data_keys = nexrad_site_datespan(start_date='20180623',
                                         start_date_time='053000',
                                         end_date='20180623',
                                         end_date_time='180000',
                                         site='kvnx')

grids = []

print(len(my_data_keys))

a = 0

for key in my_data_keys:
    localfile = tempfile.NamedTemporaryFile()
    key.get_contents_to_filename(localfile.name)
    
    radar = pyart.io.read(localfile.name)
    
    grid = get_grid(radar)
    
    grids.append(grid)
    
    print(str(a) + ': ' + str(key)[41:-1])
    a = a+1

###############################################################################

local_name = '/home/scarani/Desktop/data/goes/001/OR_ABI-L2-MCMIPM1-M3_G16_s20181732134339_e20181732134396_c20181732134466.nc'
#sat = netCDF4.Dataset(fname)
sat = xarray.open_dataset(local_name)

fig = plt.figure(figsize=[15,10])

data = sat.CMI_C13

proj_var = sat.variables[data.grid_mapping]

globe = ccrs.Globe(datum='WGS84', ellipse='WGS84', semimajor_axis=6378137.0,
                   semiminor_axis=6356752.31414)

proj = ccrs.Geostationary(central_longitude=-75,sweep_axis='x',
                          satellite_height=35786023.0, globe = globe)

trans = ccrs.Miller(central_longitude=0)


my_ax = plt.subplot(projection = trans)

pc_sat = sat.CMI_C13.plot.pcolormesh(transform=proj, ax=my_ax,
                                     x='x', y='y', cmap='Greys',
                                     add_colorbar=False)