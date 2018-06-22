import boto
from boto.s3.connection import S3Connection
from datetime import timedelta, datetime
import os
import pyart
from matplotlib import pyplot as plt
import tempfile
import numpy as np
import cartopy

def _nearestDate(dates, pivot):
    return min(dates, key=lambda x: abs(x - pivot))

base_date = "20150520_190000"
fmt = '%Y%m%d_%H%M%S' 
b_d = datetime.strptime(base_date, fmt)

datetime_t = b_d
site = 'KHGX'


"""
Get the closest volume of NEXRAD data to a particular datetime.
Parameters
----------
site : string
    four letter radar designation
datetime_t : datetime
    desired date time
Returns
-------
radar : Py-ART Radar Object
    Radar closest to the queried datetime
"""

#First create the query string for the bucket knowing
#how NOAA and AWS store the data

my_pref = datetime_t.strftime('%Y/%m/%d/') + site

#Connect to the bucket

conn = S3Connection(anon = True)
bucket = conn.get_bucket('noaa-nexrad-level2')

#Get a list of files

bucket_list = list(bucket.list(prefix = my_pref))


#we are going to create a list of keys and datetimes to allow easy searching

keys = []
datetimes = []

#populate the list

for i in range(len(bucket_list)):
    this_str = str(bucket_list[i].key)
    print(this_str)
    if 'gz' in this_str:
        endme = this_str[-22:-4]
        fmt = '%Y%m%d_%H%M%S_V0'
        dt = datetime.strptime(endme, fmt)
        datetimes.append(dt)
        keys.append(bucket_list[i])

    if this_str[-3::] == 'V06':
        endme = this_str[-19::]
        fmt = '%Y%m%d_%H%M%S_V06'
        dt = datetime.strptime(endme, fmt)
        datetimes.append(dt)
        keys.append(bucket_list[i])

#find the closest available radar to your datetime

closest_datetime = _nearestDate(datetimes, datetime_t)
index = datetimes.index(closest_datetime)

localfile = tempfile.NamedTemporaryFile()
keys[index].get_contents_to_filename(localfile.name)
radar = pyart.io.read(localfile.name)
#print (radar.info())
#my_radar.fields.keys()
#my_radar.metadata['vcp_pattern']
