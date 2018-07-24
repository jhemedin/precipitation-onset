from boto.s3.connection import S3Connection
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from netCDF4 import Dataset as netcdf_dataset
import numpy as np
from timeit import default_timer as timer
from datetime import date, datetime, timedelta
from boto.s3.connection import S3Connection

#noaa-goes16,ABI-L2-MCMIPM/2018/173/08/OR_ABI-L2-MCMIPM1-M3_G16_s20181730839336_e20181730839400_c20181730839468.nc
#
#fmt = %Y/%m
startdatetime = 
enddatetime = 


conn = S3Connection(anon=True)
bucket = conn.get_bucket('noaa-goes16')

bucket.list(prefix = 'ABI-L2-MCMIPM')
bucket.list()
