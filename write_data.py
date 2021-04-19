import io
import json

def append_data(data, file):
    """
    Permet d'ajouter une ligne à la base de données.
    :param data: Un dictionnaire qui contient les données à ajouter à la base de données
    :param file: Contient le nom du fichier où stocker les données, en général est le nom de l'entreprise.
    :return:
    """
    comp_name = file
    file += ".json"
    try:
        with open("json_db/" + file, "r", encoding="utf-8") as json_file:
            past_data = json.load(json_file)
            if data not in past_data:
                print("adding to db : ", data)
                past_data += [data]
                with open("json_db/" + file, "w", encoding="utf-8") as json_file:
                    json.dump(past_data, json_file, indent=4, ensure_ascii=False)
            else :
                print("Already in db : ", data)
    except FileNotFoundError:
        with open("json_db/" + file, "w", encoding="utf-8") as json_file:
            json.dump([data], json_file, indent=4, ensure_ascii=False)

def read_data(path):
    with open(path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)
    return data


def write_data(data, file):
    with open(file, "r") as txt_file:
        txt_file.writelines(data)
