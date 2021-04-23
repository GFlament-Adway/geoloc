from urllib.parse import unquote

import numpy as np
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from utils.write_data import append_data, write_data

from utils.scraping_utilities import check_agreement_google, unscroll, scroll, check_comp_name, check_n_results, wait_new_url
import warnings
import time

from utils.math import distance


def get_loc_comp_v3(timeout, comp_name, driver_options, verif, scroll):
    """
    Version améliorée.
    :param timeout: Temps d'attente maximal
    :param driver_options: True, alors le navigateur ne sera pas visible, si False, alors le navigateur apparaîtra.
    :param comp_name: Le nom de l'entreprise à scrapper.
    :param verif: Vérification si l'adresse appartient bien à l'entreprise ou non.
    :return:
    """
    timeout = timeout
    failed_agreement = False
    if driver_options:
        options = Options()
        options.add_argument('--headless')
    else:
        options = Options()
    requete = comp_name
    failed_agreement = False
    new_agreement_form = False
    # On lance le navigateur.
    driver = webdriver.Firefox(options=options)
    print("requests : ", requete)
    # On met la recherche directement dans l'URL et on place la carte sur cette requête.
    url = "https://www.google.fr/maps/search/{requete}".format(
        requete=comp_name)
    driver.get(url)
    try:
        driver = check_agreement_google(driver, timeout)
    except selenium.common.exceptions.NoSuchWindowException:
        failed_agreement = True
        print("check agreement failed")
    except selenium.common.exceptions.TimeoutException:
        failed_agreement = True
        print("Check agreement took to long, failed")
    if failed_agreement:
        try:
            driver.find_element_by_xpath(
                "/html/body/div/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button").click()
            failed_agreement = False
            new_agreement_form = True
            time.sleep(2.5)
        except:
            failed_agreement = True
            print("last check failed")
    print("agreement : ", failed_agreement)
    unscroll(driver, '//*[@id="widget-zoom-out"]', scroll)
    try:
        driver.find_element_by_xpath(
            "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[3]/button").click()
    except selenium.common.exceptions.NoSuchElementException:
        driver.find_element_by_xpath(
            "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[5]/div[3]/button").click()
    prop_new_loc = []
    max_dist = 300
    n_move = 0
    while 1:
        maps = driver.find_element_by_xpath("/html/body/jsl/div[3]/div[9]/div[1]/div[3]")
        webdriver.ActionChains(driver).double_click(maps).perform()
        n = check_n_results(driver)
        if prop_new_loc.count(False) > 0:
            print(prop_new_loc.count(True) / prop_new_loc.count(False))
        obj_lat, obj_long = move_map(maps, 3, driver, max_dist)
        prop_new_loc = []
        print("is type 1 : ", n)
        n_move += 1
        if n:
            k = 1
            # k permet de parcourir la liste des résultats renvoyés par Google.
            while k < 42:
                print(k)
                save = True
                try:
                    clicked = False
                    # Récupération des informations pour ce résultat.
                    try:
                        activity = driver.find_element_by_xpath(
                            "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[2]/div[1]/div[{k}]/div[2]/div[1]/div[2]/span[4]".format(
                                k=k)).text
                    except selenium.common.exceptions.NoSuchElementException:
                        try:
                            activity = driver.find_element_by_xpath(
                                "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div[{k}]/div[2]/div[1]/div[2]/span[4]".format(
                                    k=k)).text

                        except selenium.common.exceptions.NoSuchElementException:
                            try:
                                activity = driver.find_element_by_xpath(
                                    "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div[{k}]/div/div/div[2]/div[1]/div/div/div/div[4]/div[1]".format(
                                        k=k)).text
                            except selenium.common.exceptions.NoSuchElementException:
                                try:
                                    activity = driver.find_element_by_xpath(
                                        "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[5]/div[1]/div[{k}]/div/div[2]/div[2]/div[1]/div/div/div/div[1]/div".format(
                                            k=k + 4)).text
                                except:
                                    warnings.warn("Can't find activity")
                                    activity = ""
                    try:
                        add = driver.find_element_by_xpath(
                            "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div[{k}]/div/a".format(
                                k=k)).get_attribute("href")
                        print(add)
                        gps = [lat[2:] for lat in add.split("!")[-2:]]
                        gps[1] = gps[1].split("?")[0]
                        print(distance(obj_long, obj_lat, float(gps[0]), float(gps[1])))
                        if distance(obj_long, obj_lat, float(gps[0]), float(gps[1])) > max_dist:
                            k = 42
                        add = add.replace("+", " ")
                        enseigne = add.split("/")[5]
                    except AttributeError:
                        try:
                            time.sleep(1)
                            add = driver.find_element_by_xpath(
                                "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div[{k}]/div/a".format(
                                    k=k)).get_attribute("href")
                            print(add)
                            gps = [lat[2:] for lat in add.split("!")[-2:]]
                            gps[1] = gps[1].split("?")[0]
                            print(distance(obj_long, obj_lat, float(gps[0]), float(gps[1])))
                            if distance(obj_long, obj_lat, float(gps[0]), float(gps[1])) > 150:
                                k = 42
                            add = add.replace("+", " ")
                            enseigne = add.split("/")[5]
                        except:
                            print("failed, don't save")
                            save = False
                    x_path = "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div[{k}]/div[2]/div[3]/div[1]/a".format(
                        k=k)
                    k += 2
                    # On vérifie si le point appartient bien à l'entreprise.
                    if verif:
                        print(comp_name, enseigne, activity)
                        is_comp = check_comp_name(driver, comp_name, enseigne, activity, x_path)
                    else:
                        is_comp = True

                    if is_comp and save:
                        # On l'ajoute à la base de données.
                        add = ", ".join(add.split(",")[1:])
                        is_new = append_data(
                            {"activity": unquote(activity), "enseigne": unquote(enseigne),
                             "longitude": unquote(gps[0]), "latitude": unquote(gps[1])},
                            comp_name, path = "dev_db/")
                        prop_new_loc += [is_new]

                    try:
                        time.sleep(0.5)
                        for _ in range(k):
                            driver.find_elements_by_xpath(
                                "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]")[
                                -1].send_keys(Keys.DOWN)
                    except selenium.common.exceptions.ElementNotInteractableException:
                        print("Can't scroll, testing something else")
                        try:
                            for _ in range(k):
                                driver.find_element_by_xpath(
                                    "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[5]/div[4]").send_keys(
                                    Keys.DOWN)
                        except selenium.common.exceptions.ElementNotInteractableException:
                            warnings.warn("Can't scroll below")
                    except:
                        print("problem")
                except selenium.common.exceptions.NoSuchElementException:
                    print("click for next results")
                    try:
                        time.sleep(2)
                        driver.find_element_by_xpath(
                            '//*[@id="n7lv7yjyC35__section-pagination-button-next"]').click()
                        time.sleep(2.5)
                        k = 1
                    except:
                        warnings.warn("Unable to find destination and next button")
                        k = 42
                    pass
                except selenium.common.exceptions.TimeoutException:
                    warnings.warn("TimeoutException")
            if prop_new_loc.count(False) + prop_new_loc.count(True) > 0:
                append_data({"requete": {"loc": [obj_long, obj_lat],
                                         "requete": n_move,
                                         "taux_pos": prop_new_loc.count(True) / (prop_new_loc.count(False) + prop_new_loc.count(True))}},
                            file="requests", path = "dev_db/")
            else :
                append_data({"requete": {"loc": [obj_long, obj_lat],
                                         "requete": n_move,
                                         "taux_pos": 0}},
                            file="requests", path="dev_db/")
        else:
            move_map(maps, 0, driver, max_dist)
        unscroll(driver, '//*[@id="widget-zoom-out"]', 1)


def move_map(maps, n_key_press, driver, max_dist):
    url = driver.current_url
    lon = float(url.split("@")[1].split(",")[0])
    lat = float(url.split("@")[1].split(",")[1].replace("z", ""))
    dist = 0.2
    obj_lat = lat + np.random.uniform(-1, 1) * np.random.normal() * 10
    obj_lon = lon + np.random.uniform(-1, 1) * np.random.normal() * 10
    print(obj_lat, obj_lon)
    while distance(obj_lon, obj_lat, lon, lat) > max_dist / 3:
        should_unscroll = False
        should_scroll = False
        url = driver.current_url
        if lon - obj_lon > 0.2:
            maps.send_keys(Keys.ARROW_DOWN)
            got_new_url = wait_new_url(driver, url)
            while not got_new_url:
                maps.send_keys(Keys.ARROW_DOWN)
                got_new_url = wait_new_url(driver, url)
            url = driver.current_url
            if abs(lon - float(url.split("@")[1].split(",")[0])) < dist:
                should_unscroll = True
            if abs(lon - float(url.split("@")[1].split(",")[0])) > 5*dist:
                should_scroll = True
            lon = float(url.split("@")[1].split(",")[0])
        elif lon - obj_lon < -dist:
            maps.send_keys(Keys.ARROW_UP)
            got_new_url = wait_new_url(driver, url)
            while not got_new_url:
                maps.send_keys(Keys.ARROW_DOWN)
                got_new_url = wait_new_url(driver, url)
            url = driver.current_url
            if abs(lon - float(url.split("@")[1].split(",")[0])) < dist:
                should_unscroll = True
            if abs(lon - float(url.split("@")[1].split(",")[0])) > 5*dist:
                should_scroll = True
            lon = float(url.split("@")[1].split(",")[0])
        if lat - obj_lat > dist:
            maps.send_keys(Keys.ARROW_LEFT)
            got_new_url = wait_new_url(driver, url)
            while not got_new_url:
                maps.send_keys(Keys.ARROW_DOWN)
                got_new_url = wait_new_url(driver, url)
            url = driver.current_url
            if abs(lat - float(url.split("@")[1].split(",")[1].replace("z", ""))) < dist:
                should_unscroll = True
            if abs(lat - float(url.split("@")[1].split(",")[1].replace("z", ""))) > 5*dist:
                should_scroll = True
            lat = float(url.split("@")[1].split(",")[1].replace("z", ""))
        elif lat - obj_lat < -dist:
            maps.send_keys(Keys.ARROW_RIGHT)
            got_new_url = wait_new_url(driver, url)
            while not got_new_url:
                maps.send_keys(Keys.ARROW_DOWN)
                got_new_url = wait_new_url(driver, url)
            url = driver.current_url
            if abs(lat - float(url.split("@")[1].split(",")[1].replace("z", ""))) < dist:
                should_unscroll = True
            if abs(lat - float(url.split("@")[1].split(",")[1].replace("z", ""))) > 5*dist:
                should_scroll
            lat = float(url.split("@")[1].split(",")[1].replace("z", ""))
        if should_unscroll:
            unscroll(driver)
        if should_scroll:
            scroll(driver)
    time.sleep(3)
    if not check_n_results(driver):
        driver.find_element_by_xpath('//*[@id="searchbox-searchbutton"]').click()
        print("click on research button")
    time.sleep(2)
    return obj_lat, obj_lon


if __name__ == "__main__":
    debut = time.time()
    get_loc_comp_v3(timeout=5, comp_name="Generali", driver_options=False, verif=True, scroll=True)
    print("Temps de scrapping : ", time.time() - debut)
