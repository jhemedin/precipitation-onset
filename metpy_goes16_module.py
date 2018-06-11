from datetime import datetime
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from matplotlib import patheffects
from netCDF4 import Dataset
import numpy as np
from scipy import interpolate
from siphon.catalog import TDSCatalog

savelocation = '/home/scarani/Desktop/output/goes/'



def open_dataset(date, channel, idx, region):
    """
    Open and return a netCDF Dataset object for a given date, channel, and image index
    of GOES-16 data from THREDDS test server.
    """
    cat = TDSCatalog('http://thredds-test.unidata.ucar.edu/thredds/catalog/satellite/goes16/GOES16/'
                 '{}/Channel{:02d}/{:%Y%m%d}/catalog.xml'.format(region, channel, date))
    ds = cat.datasets[idx].remote_access(service='OPENDAP')                     
    return ds



def plot_GOES16_channel(date, idx, channel, region):
    """
    Get and plot a GOES 16 data band from the ABI.
    """
    ds = open_dataset(date, channel, idx, region)
    x = ds.variables['x'][:]
    y = ds.variables['y'][:]
    z = ds.variables['Sectorized_CMI'][:]
    proj_var = ds.variables[ds.variables['Sectorized_CMI'].grid_mapping]

    # Create a Globe specifying a spherical earth with the correct radius
    globe = ccrs.Globe(ellipse='sphere', semimajor_axis=proj_var.semi_major,
                       semiminor_axis=proj_var.semi_minor)

    # Select the correct projection.
    
#    print (proj_var.standard_parallel)
    

    if proj_var.grid_mapping_name == 'lambert_conformal_conic':
        proj = ccrs.LambertConformal(central_longitude=proj_var.longitude_of_central_meridian,
                                     central_latitude=proj_var.latitude_of_projection_origin,
                                     standard_parallels=[proj_var.standard_parallel],
                                     globe=globe)

    else:
        proj = ccrs.Mercator(central_longitude=proj_var.longitude_of_projection_origin, 
                             latitude_true_scale=proj_var.standard_parallel,
                             globe=globe)

    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1, projection=proj)
    ax.coastlines(resolution='10m', color='black')
    ax.add_feature(cfeature.STATES, linestyle=':', edgecolor='black')
    ax.add_feature(cfeature.BORDERS, linewidth=2, edgecolor='black')
    print (y.max())
    for im in ax.images:
        im.remove()
    im = ax.imshow(z, extent=(x.min(), x.max(), y.min(), y.max()), origin='upper', cmap='Greys')
    timestamp = datetime.strptime(ds.start_date_time, '%Y%j%H%M%S')
    # Plot text
    #plt.title('GOES 16: '+ str(channel_title[int(channel)+1]), fontsize=20)
    plt.text(0.5,1.035, 'GOES 16: '+ str(channel_title[int(channel)-1]),
             horizontalalignment = 'center', fontsize=15,transform = ax.transAxes)
    plt.text(0.5,1.01, timestamp.strftime('%H%MZ %d %B %Y'),
             horizontalalignment = 'center', fontsize=10,transform = ax.transAxes)

    # Make the text stand out even better using matplotlib's path effects
    plt.savefig(savelocation + timestamp.strftime('%Y%m%d%H%M_') + 'ch-' + str(chno) + '.png', bbox_inches = 'tight', dpi = 300)
    plt.show()
    plt.close()
"""
channel_list = {u'1 - Blue Band 0.47 \u03BCm': 1,
            u'2 - Red Band 0.64 \u03BCm': 2,
            u'3 - Veggie Band 0.86 \u03BCm': 3,
            u'4 - Cirrus Band 1.37 \u03BCm': 4,
            u'5 - Snow/Ice Band 1.6 \u03BCm': 5,
            u'6 - Cloud Particle Size Band 2.2 \u03BCm': 6,
            u'7 - Shortwave Window Band 3.9 \u03BCm': 7,
            u'8 - Upper-Level Tropo. WV Band 6.2 \u03BCm': 8,
            u'9 - Mid-Level Tropo. WV Band 6.9 \u03BCm': 9,
            u'10 - Low-Level WV Band 7.3 \u03BCm': 10,
            u'11 - Cloud-Top Phase Band 8.4 \u03BCm': 11,
            u'12 - Ozone Band 9.6 \u03BCm': 12,
            u'13 - Clean IR Longwave Band 10.3 \u03BCm': 13,
            u'14 - IR Longwave Band 11.2 \u03BCm': 14,
            u'15 - Dirty Longwave Band 12.3 \u03BCm': 15,
            u'16 - CO2 Longwave IR 13.3 \u03BCm': 16}
"""
channel_title = ['Blue Band 0.47 µm',
            'Red Band 0.64 µm',
            'Veggie Band 0.86 µm',
            'Cirrus Band 1.37 µm',
            'Snow/Ice Band 1.6 µm',
            'Cloud Particle Size Band 2.2 µm',
            'Shortwave Window Band 3.9 µm',
            'Upper-Level Tropo. WV Band 6.2 µm',
            'Mid-Level Tropo. WV Band 6.9 µm',
            'Low-Level WV Band 7.3 µm',
            'Cloud-Top Phase Band 8.4 µm',
            'Ozone Band 9.6 µm',
            'Clean IR Longwave Band 10.3 µm',
            'IR Longwave Band 11.2 µm',
            'Dirty Longwave Band 12.3 µm',
            'CO2 Longwave IR 13.3 µm']


# Mesoscale-1', 'Mesoscale-2', 'CONUS']

#for n in range(1,16,1):
chno = 13
    
#plot_GOES16_channel( date=datetime.utcnow(), idx=-2, channel=chno, region='Mesoscale-1')
#plot_GOES16_channel( date=datetime.utcnow(), idx=-2, channel=chno, region='Mesoscale-2')
plot_GOES16_channel( date=datetime.utcnow(), idx=5, channel=chno, region='CONUS')