# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier. All Rights Reserved.
# Distributed under the (new) BSD License.
# -----------------------------------------------------------------------------
# Based on : https://peak5390.wordpress.com
# -> 2012/12/08/matplotlib-basemap-tutorial-plotting-global-earthquake-activity/
# -----------------------------------------------------------------------------
import urllib
import numpy as np
import matplotlib
matplotlib.rcParams['toolbar'] = 'None'
import matplotlib.pyplot as plt
from  matplotlib.animation import FuncAnimation
try:
    from mpl_toolkits.basemap import Basemap
    use_basemap = True
except ImportError:
    import cartopy
    use_basemap = False



# Open the earthquake data
# -------------------------
# -> https://earthquake.usgs.gov/earthquakes/feed/v1.0/csv.php
feed = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/"

# Significant earthquakes in the past 30 days
# url = urllib.urlopen(feed + "significant_month.csv")

# Earthquakes of magnitude > 4.5 in the past 30 days
url = urllib.request.urlopen(feed + "4.5_month.csv")

# Earthquakes of magnitude > 2.5 in the past 30 days
# url = urllib.urlopen(feed + "2.5_month.csv")

# Earthquakes of magnitude > 1.0 in the past 30 days
# url = urllib.urlopen(feed + "1.0_month.csv")

# Set earthquake data
data = url.read()
data = data.split(b'\n')[+1:-1]
E = np.zeros(len(data), dtype=[('position',  float, 2),
                               ('magnitude', float)])
for i in range(len(data)):
    row = data[i].split(b',')
    E['position'][i] = float(row[2]),float(row[1])
    E['magnitude'][i] = float(row[4])


fig = plt.figure(figsize=(14,10))
P = np.zeros(50, dtype=[('position', float, 2),
                        ('size',     float),
                        ('growth',   float),
                        ('color',    float, 4)])

if use_basemap:
    ax = plt.subplot(1,1,1)
    # Basemap projection
    map = Basemap(projection='mill')
    map.drawcoastlines(color='0.50', linewidth=0.25)
    map.fillcontinents(color='0.95')
else:
    # Cartopy projection
    ax = plt.axes(projection=cartopy.crs.Miller())
    ax.coastlines(color='0.50', linewidth=0.25)
    ax.add_feature(cartopy.feature.LAND, color='0.95')
    ax.set_global()

scat = ax.scatter(P['position'][:,0], P['position'][:,1], P['size'], lw=0.5,
                  edgecolors = P['color'], facecolors='None', zorder=10)


def update(frame):
    current = frame % len(E)
    i = frame % len(P)

    P['color'][:,3] = np.maximum(0, P['color'][:,3] - 1.0/len(P))
    P['size'] += P['growth']

    magnitude = E['magnitude'][current]
    P['position'][i] = map(*E['position'][current]) if use_basemap else \
        cartopy.crs.Miller().transform_point(*E['position'][current], cartopy.crs.PlateCarree())
    P['size'][i] = 5
    P['growth'][i]= np.exp(magnitude) * 0.1

    if magnitude < 6:
        P['color'][i]    = 0,0,1,1
    else:
        P['color'][i]    = 1,0,0,1
    scat.set_edgecolors(P['color'])
    scat.set_facecolors(P['color']*(1,1,1,0.25))
    scat.set_sizes(P['size'])
    scat.set_offsets(P['position'])
    return scat,

plt.title("Earthquakes > 4.5 in the last 30 days")
animation = FuncAnimation(fig, update, interval=10, blit=True)
plt.show()
