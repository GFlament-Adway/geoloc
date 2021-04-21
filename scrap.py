import time
from urllib.parse import unquote

import time
from urllib.parse import unquote

import numpy as np
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from handle_requests import get_requetes
from write_data import append_data

import warnings
import time

def check_n_results(driver):
    """

    :param driver: une instance webdriver
    :return: True s'il y a une liste de résultat à la requête, false s'il n'y a qu'un résultat.
    Cette distinction est nécessaire puisque l'affichage sur google est différent.
    """
    try:
        elem = driver.find_element_by_xpath("/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[1]/div[1]/button/img")
        size = elem.size["width"]
        if size == 408.0 or size == 426.0:
            print("One result")
            return False
        else:
            
            warnings.warn("Never saw this before ! Check this query ! Image format : " + str(size))
            return True
    except:
        return True
    #return max(len(driver.find_elements_by_xpath("//img[contains(@class,'section-result-action-icon')]")),
    #           len(driver.find_elements_by_xpath("//img[contains(@class, 'iRxY3GoUYUY__icon')]")))


def check_comp_name(driver, comp_name, enseigne, activity, x_path, authorized_activites = None):
    """

    :param driver: Une instance webdriver
    :param comp_name: Le nom de l'entreprise a scrapper
    :param enseigne: Le nom de l'enseigne à cette adresse, par exemple le premier résultat de carrefour ile de France renvoie l'adresse : Carrefour bercy
    :param activity: L'activité à cette adresse, (hypermarché, supermarché, station service, banque ....)
    par exemple le premier résultat de carrefour ile de France est, renvoie l'adresse : Hypermarché, centre commercial bercy 2, Place de l'Europe.
    :param x_path: le x_path à examiner
    :param authorized_activites: Les activités authorisées pour cette enseigne, à faire !
    :return: True si l'adresse appartient à l'entreprise
    False sinon.
    """
    comp_name = comp_name.lower()
    enseigne = unquote(enseigne.lower())
    activity = unquote(activity.lower())
    if authorized_activites is None:
        authorized_activites = [activity]


    try:
        return ((comp_name in activity or comp_name in enseigne or comp_name.lower() in driver.find_element_by_xpath(
            x_path).get_attribute("href")) & np.sum([activity in auth_activity for auth_activity in authorized_activites]) >= 1)
    except selenium.common.exceptions.NoSuchElementException:
        try:
            return ((comp_name in activity or comp_name in enseigne or comp_name in driver.find_element_by_xpath(
                x_path).text ) and np.sum([activity in auth_activity for auth_activity in authorized_activites]) >= 1)
        except selenium.common.exceptions.NoSuchElementException:
            return (comp_name in enseigne or comp_name in activity) and np.sum([activity in auth_activity for auth_activity in authorized_activites]) >= 1
    except TypeError:
        return comp_name in enseigne or comp_name in activity


def check_agreement_google(driver, timeout=20):
    """

    :param driver: Une instance webdriver
    :param timeout: Un temps d'attente maximal
    :return: Une instance webdriver après avoir accepté les conditions google.
    """
    try:
        # WebDriverWait(driver, timeout).until(
        # EC.frame_to_be_available_and_switch_to_it((By.XPATH, "/html/body/jsl/div[2]/div/div[1]/iframe")))
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="introAgreeButton"]')))
        driver.switch_to.frame(driver.find_elements_by_xpath("/html/body/jsl/div[2]/div/div[1]/iframe"))
        driver.find_element_by_xpath('//*[@id="introAgreeButton"]').click()
    except selenium.common.exceptions.TimeoutException:
        WebDriverWait(driver, timeout).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "/html/body/jsl/div[2]/div/div[1]/iframe")))
        driver.find_element_by_xpath('//*[@id="introAgreeButton"]').click()
    driver.switch_to.parent_frame()
    return driver

def get_loc_comp_v2(timeout=5, driver_options=True, comp_name="Total", mapping = "World", verif=True):
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


    for i, requete in enumerate(requetes):
        print("-----------------------------")
        print("Requete {n}/{n_requetes}".format(n=i+1, n_requetes=len(requetes)))
        print("-----------------------------")
        failed_agreement = False
        new_agreement_form = False
        #On lance le navigateur.
        driver = webdriver.Firefox(options=options)
        print("requests : ", requete)
        #On met la recherche directement dans l'URL et on place la carte sur cette requête.
        url = "https://www.google.fr/maps/search/{requete}/@{lat},{long},3z".format(
            requete=requete, lat=gps_loc[i // n_activities][0], long=gps_loc[i // n_activities][1])
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
                driver.find_element_by_xpath("/html/body/div/c-wiz/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button").click()
                failed_agreement = False
                new_agreement_form = True
                time.sleep(2.5)
            except:
                failed_agreement=True
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
    get_loc_comp_v2(timeout=5, comp_name="Total", mapping="world", driver_options=True, verif=True)
    print("Temps de scrapping : ", time.time() - debut)