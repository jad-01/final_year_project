import matplotlib.pyplot as plt
import cartopy
import cartopy.crs as ccrs
import cartopy.util as cartopy_util
import numpy as np
from netCDF4 import Dataset as ncfile
import psutil
from matplotlib.animation import FuncAnimation
from psutil import cpu_percent 
from psutil import cpu_count
from multiprocessing import Pool, cpu_count
import multiprocessing
from datetime import datetime
import functools
from multiprocessing import Pool
from functools import partial

########################################################################################

def stress_test(args):
    cpu, value = args
    start_time = datetime.now()
    for i in range(value):
        value = value * i
        
########################################################################################

def map_creation():
    nc = ncfile('ECMWF_ERA-40_subset.nc')
    field=nc.variables['p2t'][0,:,:]
    lons=nc.variables['longitude'][:]
    lats=nc.variables['latitude'][:]
    field = field - 273.15

    print(np.shape(field))
    print(np.min(field), np.max(field))

    lonrange = np.max(lons)-np.min(lons)
    if lonrange <= 360:
        field, lons = cartopy_util.add_cyclic_point(field, lons)

    plot=plt.figure(figsize=(11, 8))

    lonmin=-180
    lonmax=180.01

    latmin=-90
    latmax=90

    lon_0=(lonmax-lonmin)/2.0+lonmin
    proj=ccrs.PlateCarree(central_longitude=lon_0)

    mymap = plot.add_subplot(1,1,1, projection=proj)
    mymap.set_extent((lonmin, lonmax, latmin, latmax), crs=proj)

# Contour data
    clevs=np.arange(-32, 32, 4) # levels
    cs = mymap.contourf(lons, lats, field, clevs,extend='both', transform=ccrs.PlateCarree(), cmap='bwr')
    cb = plot.colorbar(cs, orientation='horizontal', aspect=75, pad=0.08, ticks=clevs)
    cs = mymap.contour(lons, lats, field, clevs, colors='k', linestyles='solid', transform=ccrs.PlateCarree())
    plt.clabel(cs, fmt = '%d', colors = 'k', fontsize=11) 

# Axes
    mymap.set_xticks(np.arange(-180, 181, 60), crs=proj)
    mymap.set_yticks(np.arange(-90, 91, 30))

# Coastlines
    mymap.coastlines(resolution='110m')

# Title
    title = plt.title('Temperature in degrees Celsius', y=1.03)
    plt.show()

########################################################################################

y = []
def animate(*args, **kwargs):
    y.append(cpu_percent())
    plt.cla()
    plt.plot(y, 'r', label = 'Real-Time CPU Uses')
    plt.xlim(0,100)
    plt.xlabel('Time (s)')
    plt.ylabel('CPU Uses (%)')
    plt.legend(loc = 'upper right')

########################################################################################

cpu_count = cpu_count()
def pool():
    start_time = datetime.now()
    with Pool(cpu_count - 1) as mp_pool:
        mp_pool.map(stress_test, [(cpu, 100000000) for cpu in range(cpu_count)])
    print("total:", datetime.now() - start_time)

########################################################################################

process3 = multiprocessing.Process(target=pool)
process2 = multiprocessing.Process(target=animate)
process1 = multiprocessing.Process(target=map_creation)

########################################################################################

if __name__ == '__main__':
    process1.start()
    process2.start()
    process3.start()
    plt.tight_layout()
    animationPlot = FuncAnimation(plt.gcf(),animate, interval=50)
    plt.savefig('Save as map.png')
    plt.show()

