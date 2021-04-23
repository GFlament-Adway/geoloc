from urllib.parse import unquote

import numpy as np
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.handle_requests import get_requetes
from utils.write_data import append_data

from utils.scraping_utilities import check_agreement_google, unscroll, check_comp_name, check_n_results
import warnings
import time


def get_loc_comp_v2(timeout=5, driver_options=True, comp_name="Total", mapping = "World", verif=True, scroll=True):
    """
    Version améliorée.
    :param timeout: Temps d'attente maximal
    :param driver_options: True, alors le navigateur ne sera pas visible, si False, alors le navigateur apparaîtra.
    :param comp_name: Le nom de l'entreprise à scrapper.
    :param mapping: Permet de modifier le niveau de granularité, valeurs possibles : cities, region, departement, world
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
    #On génère les requêtes.
    requetes, gps_loc = get_requetes(comp_name, mapping)
    n_activities = len(requetes) // len(gps_loc)
    np.random.shuffle(requetes)
    print(requetes)
    requete = requetes[0]
    failed_agreement = False
    new_agreement_form = False
    for i, requete in enumerate(requetes):
        # On lance le navigateur.
        driver = webdriver.Firefox(options=options)
        print("-----------------------------")
        print("Requete {n}/{n_requetes}".format(n=i+1, n_requetes=len(requetes)))
        print("-----------------------------")
        print("requests : ", requete)
        # On met la recherche directement dans l'URL et on place la carte sur cette requête.
        url = "https://www.google.fr/maps/search/{requete}/@{lat},{long},3z".format(
            requete=requete, lat=gps_loc[0][0], long=gps_loc[0][1])
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
        #Si on a passé la première étape (accpeter les cookies/CGU ...)
        if not failed_agreement:
            #Vérification du type de retour de google, si n est vrai, alors il y a plusieurs résultat, sinon il n'y en a qu'un.
            n = check_n_results(driver)
            print("is type 1 : ", n)
            if n:
                k = 1
                #k permet de parcourir la liste des résultats renvoyés par Google.
                while k < 42:
                    save = True
                    try:
                        clicked = False
                        #Récupération des informations pour ce résultat.
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
                                    activity = driver.find_element_by_xpath("/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div[{k}]/div/div/div[2]/div[1]/div/div/div/div[4]/div[1]".format(k=k)).text
                                except:
                                    warnings.warn("Can't find activity")
                                    activity = ""
                        try:
                            add = driver.find_element_by_xpath("/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div[{k}]/div/a".format(k=k)).get_attribute("href")
                            gps = [lat[2:] for lat in add.split("!")[-2:]]
                            gps[1] = gps[1].split("?")[0]
                            add = add.replace("+", " ")
                            enseigne = add.split("/")[5]
                        except AttributeError:
                            try:
                                time.sleep(1)
                                add = driver.find_element_by_xpath(
                                    "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div[{k}]/div/a".format(
                                        k=k)).get_attribute("href")
                                gps = [lat[2:] for lat in add.split("!")[-2:]]
                                gps[1] = gps[1].split("?")[0]
                                add = add.replace("+", " ")
                                enseigne = add.split("/")[5]
                            except:
                                save = False
                        x_path = "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div[{k}]/div[2]/div[3]/div[1]/a".format(
                            k=k)
                        k += 2
                        #On vérifie si le point appartient bien à l'entreprise.
                        if verif:
                            is_comp = check_comp_name(driver, comp_name, enseigne, activity, x_path)
                        else:
                            is_comp = True

                        if is_comp and save:
                            #On l'ajoute à la base de données.
                            add = ", ".join(add.split(",")[1:])
                            append_data(
                                {"activity": unquote(activity), "enseigne": unquote(enseigne),
                                 "longitude": unquote(gps[0]), "latitude": unquote(gps[1])},
                                comp_name)
                        try:
                            time.sleep(0.5)
                            for _ in range(k):
                                driver.find_elements_by_xpath("/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]")[-1].send_keys(Keys.DOWN)
                        except selenium.common.exceptions.ElementNotInteractableException:
                            warnings.warn("Can't scroll below")
                        except:
                            pass
                    except selenium.common.exceptions.NoSuchElementException:
                        try:
                            driver.find_element_by_xpath('//*[@id="n7lv7yjyC35__section-pagination-button-next"]').click()
                            time.sleep(2.5)
                            k = 1
                        except:
                            warnings.warn("Unable to find destination and next button")
                            k = 42
                        pass
                    except selenium.common.exceptions.TimeoutException:
                        warnings.warn("TimeoutException")
            else:
                #Dans ce cas, il n'y a qu'un résultat, il y a beaucoup moins de travail à faire.
                try:
                    time.sleep(0.5 + np.random.uniform(0.1, 0.4))
                    try:
                        """/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div[3]/div/a """
                        activity = driver.find_element_by_xpath(
                            "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[2]/span[1]/span[1]/button").text
                    except selenium.common.exceptions.NoSuchElementException:
                        print("failed to find activity")
                        activity = ""
                    driver.find_element_by_xpath(
                        "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[4]/div[1]/div").click()
                    WebDriverWait(driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH,
                                                        "/html/body/jsl/div[3]/div[9]/div[3]/div[1]/div[2]/div/div[3]/div[1]/div[2]/div[2]/div/div/input")))
                    time.sleep(0.3 + np.random.uniform(0.05, 0.2))
                    add = driver.current_url.split("/")[6]
                    add = add.replace("+", " ")
                    gps = [lat[2:] for lat in driver.current_url.split("!")[-2:]]
                    enseigne = add.split(",")[0]
                    add = ", ".join(add.split(",")[1:])
                    if verif:
                        is_comp = check_comp_name(driver, comp_name, unquote(enseigne), unquote(activity),
                                                  x_path="/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[10]/div[3]/button/div[1]/div[2]/div[1]")
                    else:
                        is_comp = True
                    if is_comp:
                        append_data(
                            {"activity": unquote(activity), "enseigne": unquote(enseigne), "adresse": unquote(add),
                             "longitude": unquote(gps[0]), "latitude": unquote(gps[1])},
                            comp_name)
                except selenium.common.exceptions.NoSuchElementException:
                    print("failed adress")
        driver.quit()


if __name__ == "__main__":
    debut = time.time()
    get_loc_comp_v2(timeout=5, comp_name="Generali", driver_options=False, verif=True, scroll=True)
    print("Temps de scrapping : ", time.time() - debut)