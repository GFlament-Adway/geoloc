import io
import json
import os
import reverse_geocoder

def add_countries(prop_new_loc, coordinates, comp):
    print(prop_new_loc)
    country = reverse_geocoder.search((coordinates[0], coordinates[1]))[0]["cc"]
    if os.path.exists("visited_countries.json"):
        with open("visited_countries.json", "r") as json_file:
            data = json.load(json_file)
        with open("visited_countries.json", "w") as json_file:
            if comp in data.keys():
                if country in data[comp].keys():
                        data[comp].update({country : data[comp][country] + [prop_new_loc.count(True)]})
                else:
                    data[comp].update({country: [prop_new_loc.count(True)]})
            else:
                data.update({comp : {country : [prop_new_loc.count(True)]}})
            json.dump(data, json_file)

    else:

        with open("visited_countries.json", "w") as json_file:
            data = {comp : {country: [prop_new_loc.count(True)]}}
            json.dump(data, json_file)
def get_forbidden_country(comp):
    try:
        with open("visited_country.json", "r") as json_file:
            data = json.load(json_file)
        return [key for key in list(data[comp].keys) if data[comp][key].count(0)/len(data[comp][key]) < 0.1 ]
    except:
        print("Can't find visited country file")
        return []


def append_data(data, file, path="../json_db/"):
    """
    Permet d'ajouter une ligne à la base de données.
    :param data: Un dictionnaire qui contient les données à ajouter à la base de données
    :param file: Contient le nom du fichier où stocker les données, en général est le nom de l'entreprise.
    :return:
    """
    file += ".json"
    try:
        with open(path + file, "r", encoding="utf-8") as json_file:
            past_data = json.load(json_file)
            if data not in past_data:
                print("adding to db : ", data)
                past_data += [data]
                with open(path + file, "w", encoding="utf-8") as json_file:
                    json.dump(past_data, json_file, indent=4, ensure_ascii=False)
                return True
            else :
                print("Already in db : ", data)
                return False
    except FileNotFoundError:
        with open(path + file, "w", encoding="utf-8") as json_file:
            json.dump([data], json_file, indent=4, ensure_ascii=False)
        return True


def read_data(path):
    with open(path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


def write_data(data, file):
    with open(file, "r") as txt_file:
        txt_file.writelines(data)
