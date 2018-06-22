import urllib.request

url = 'http://thredds-test.unidata.ucar.edu/thredds/catalog/satellite/goes16/GOES16/CONUS/Channel12/20180606/GOES16_CONUS_20180606_000230_9.61_2km_33.3N_90.1W.nc4'


urllib.request.urlretrieve(str(url), '/home/scarani/Desktop/test.nc4')

#testfile = urllib.URLopener()
#testfile.retrieve(str(url), '/home/scarani/Desktop/test.nc4')

