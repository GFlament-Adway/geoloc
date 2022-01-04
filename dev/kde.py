import os

import numpy as np
from sklearn.neighbors import KernelDensity
from sklearn.neighbors import RadiusNeighborsRegressor, KNeighborsRegressor
import matplotlib.pyplot as plt
from utils.write_data import read_data

from mpl_toolkits.basemap import Basemap

def kde2D(x, y, bandwith=1, xbins=500j, ybins=500j, **kwargs):
    """
    https://stackoverflow.com/questions/41577705/how-does-2d-kernel-density-estimation-in-python-sklearn-work
    :param x:
    :param y:
    :param bandwidth:
    :param xbins:
    :param ybins:
    :param kwargs:
    :return:
    """

    # create grid of sample locations (default: 100x100)
    xx, yy = np.mgrid[x.min():x.max():xbins,
                      y.min():y.max():ybins]

    xy_sample = np.vstack([yy.ravel(), xx.ravel()]).T
    xy_train  = np.vstack([y, x]).T

    kde_skl = KernelDensity(bandwidth = bandwith, **kwargs)
    kde_skl.fit(xy_train)

    # score_samples() returns the log-likelihood of the samples
    z = 1/(1 + np.exp(-kde_skl.score_samples(xy_sample)))
    return xx, yy, np.reshape(z, xx.shape), kde_skl

def kernel_ridge(loc, Y, xbins=100j, ybins=100j):
    neigh = RadiusNeighborsRegressor(radius=2)
    print(len(Y))
    neigh.fit(loc, Y)

    x = np.array([loc[k][0] for k in range(len(loc))])
    y = np.array([loc[k][1] for k in range(len(loc))])

    xx, yy = np.mgrid[x.min():x.max():xbins,
             y.min():y.max():ybins]
    xy_sample = np.vstack([xx.ravel(), yy.ravel()]).T
    z = neigh.predict(xy_sample)
    z = np.nan_to_num(z)
    z = np.reshape(z, xx.shape)


    return xx, yy, np.reshape(z, xx.shape), neigh

if __name__ == "__main__":

    requete = True
    comp = False
    if comp:
        data = read_data("dev_db/Aldi.json")
        y = [float(data[k]["longitude"]) for k in range(len(data))]
        x = [float(data[k]["latitude"]) for k in range(len(data))]
        xx, yy, zz, kde = kde2D(np.array(x), np.array(y))
    if requete:
        data = read_data("../dev/dev_db/requests.json")
        loc = np.array([[data[i]["requete"]["loc"][1], data[i]["requete"]["loc"][0]]  for i in range(len(data))])
        n_positives = []
        for k in range(len(data)):
            try:
                n_positives += [float(data[k]["requete"]["positive_requests"])]
            except KeyError:
                n_positives += [0]
        xx, yy, zz, kde = kernel_ridge(loc, n_positives)
    plt.figure()
    m = Basemap(projection='cyl', llcrnrlat=max(yy.min(), -90), urcrnrlat=min(yy.max(), 90), llcrnrlon=max(xx.min(), - 180), urcrnrlon=min(180, xx.max()),
                resolution='l', lat_ts=20)
    m.drawcoastlines()
    m.drawcountries()
    plt.contourf(xx, yy, zz)
    plt.colorbar(label="Nombre de résultats attendus")
    plt.title("A priori pour la géolocalisation des entreprises.")
    plt.show()

    import reverse_geocoder
    coordinates = (47.92, 3.35)
    print(reverse_geocoder.search(coordinates)[0]["cc"])
    coordinates = (48.201, 16.39)
    print(reverse_geocoder.search(coordinates)[0]["cc"])
