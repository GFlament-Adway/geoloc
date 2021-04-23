import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BASE_COLORS, CSS4_COLORS, TABLEAU_COLORS
from mpl_toolkits.basemap import Basemap

from utils.write_data import read_data

if __name__ == "__main__":
    colors = list(BASE_COLORS.keys()) + list(TABLEAU_COLORS.keys()) + list(CSS4_COLORS.keys())
    entreprise = "Generali"
    map = Basemap(projection='merc', llcrnrlat=-80, urcrnrlat=80, \
                  llcrnrlon=-180, urcrnrlon=180, lat_ts=10, resolution='l')
    #map = Basemap(projection='merc', llcrnrlat=39, urcrnrlat=53.697, \
    #              llcrnrlon=-14, urcrnrlon=18.259, lat_ts=10, resolution='l')

    map.drawcoastlines()
    map.drawcountries()
    plt.title("{comp_name} ".format(comp_name=entreprise))
    data = read_data("json_db/{entreprise}.json".format(entreprise=entreprise))
    # map.bluemarble()
    map.drawcountries()
    gps_coordinates = np.array([[np.float(loc["longitude"]), np.float(loc["latitude"])] for loc in data])
    loc_activities = [line["activity"] for line in data]
    activities = list(dict.fromkeys(loc_activities))
    label_plotted = {activity: 0 for activity in activities}
    for i, coord in enumerate(gps_coordinates):
        x, y = map(coord[1], coord[0])
        map.plot(x, y, marker="o", markersize=2, color="r")
    map.drawcoastlines()
    plt.legend(bbox_to_anchor=(0.2, 1, 0, 0))
    plt.show()
