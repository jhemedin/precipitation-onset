import pyart
# %%
data_dir = '/home/scarani/grid/'
filenames = [os.path.join(data_dir, fn) for fn in os.listdir(data_dir)]
filenames.sort()
print(filenames)
# %%
grid = pyart.io.read_grid(filenames[0])
display = pyart.graph.GridMapDisplay(grid)
display.plot_grid(field='c13', edges=False)
display.plot_basemap()
display.plot_crosshairs(lon=-98.128, lat=36.741)
# %%
e_display = pyart.graph.GridMapDisplay(example_grid)
e_display.plot_grid(field='reflectivity', edges=False)
display.plot_basemap()
display.plot_crosshairs(lon=-98.128, lat=36.741)

# %%
from netCDF4 import Dataset
ds = Dataset(filenames[0], mode='r')