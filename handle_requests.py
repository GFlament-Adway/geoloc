import csv
import numpy as np

from write_data import read_data

def get_requetes(comp_name, mapping):
    """
    :param comp_name: Nom de l'entreprise
    :param mapping: Niveau de granularité souhaite: cities, region, departement, world
    :return: La liste des requêtes, et les coordonnées GPS de ces requêtes.
    """
    if mapping.lower() == "cities":
        with open("settings/villes_france.csv", "r") as csv_file:
            data = csv.reader(csv_file)
            villes = []
            for row in data:
                if int(row[14]) > 500000:
                    villes += [row[2]]
        for k in range(len(villes)):
            if villes[k].lower() == "paris":
                villes += ["paris " + str(arrondissement) for arrondissement in range(1, 21)]
            if villes[k].lower() == "marseille":
                villes += ["marseille " + str(arrondissement) for arrondissement in range(1, 17)]
            if villes[k].lower() == "lyon":
                villes += ["lyon " + str(arrondissement) for arrondissement in range(1, 10)]
        return [comp_name + " " + ville for ville in villes], [[48.856, 2.352] for ville in villes]
    elif mapping.lower() == "region":
        with open("settings/regions-france.csv", "r") as csv_file:
            data = csv.reader(csv_file)
            departements = []
            for row in data:
                departements += [row[1]]
        return [comp_name + " " + dep for dep in departements], [[48.856, 2.352] for dep in departements]
    elif mapping.lower() == "departement":
        with open("settings/departement.csv", "r") as csv_file:
            data = csv.reader(csv_file)
            departements = []
            for row in data:
                departements += [row[2]]
        return [comp_name + " " + dep for dep in departements], [[48.856, 2.352] for dep in departements]
    elif mapping.lower() == "world":
        with open("settings/activities.csv", "r") as csv_file:
                data = csv.reader(csv_file)
                activities = []
                for row in data:
                    if row[0] == comp_name:
                        activities += row[1:]
        if activities == []:
            activities = [" "]
        data = read_data("settings/countries_data.json")
        print(data)
        countries = [country["name"] for country in data if country["population"] > 20000000]
        gps_locs =  [country["latlng"] for country in data if country["population"] > 20000000]
        return list(np.array([[comp_name + " " + activity + " " + country for activity in activities if activity != ""]for country in countries if country != ""]).flatten()), gps_locs