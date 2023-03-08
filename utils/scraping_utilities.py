from urllib.parse import unquote

import numpy as np
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import warnings
import time


def unscroll(driver, xpath='//*[@id="widget-zoom-out"]', n_click=1):
    for _ in range(n_click):
        try:
            time.sleep(0.5)
            driver.find_element_by_xpath(xpath).click()
        except selenium.common.exceptions.NoSuchElementException:
            pass
def scroll(driver, xpath='//*[@id="widget-zoom-in"]', n_click=1):
    for _ in range(n_click):
        try:
            time.sleep(0.5)
            driver.find_element_by_xpath(xpath).click()
        except selenium.common.exceptions.NoSuchElementException:
            pass

def check_n_results(driver):
    """

    :param driver: une instance webdriver
    :return: True s'il y a une liste de résultat à la requête, false s'il n'y a qu'un résultat.
    Cette distinction est nécessaire puisque l'affichage sur google est différent.
    """
    try:
        elem = driver.find_element_by_xpath(
            '//*[@id="pane"]/div/div[1]/div/div/div[1]/div[1]/button/img')
        size = elem.size["width"]
        if size == 408.0 or size == 426.0 or size == 480.0:
            return False
        else:
            warnings.warn("Never saw this before ! Check this query ! Image format : " + str(size))
            return False
    except:
        return True
    # return max(len(driver.find_elements_by_xpath("//img[contains(@class,'section-result-action-icon')]")),
    #           len(driver.find_elements_by_xpath("//img[contains(@class, 'iRxY3GoUYUY__icon')]")))


def check_comp_name(driver, comp_name, enseigne, activity, x_path, authorized_activites=None):
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

    return comp_name in enseigne.split(" ") or comp_name in activity.split(" ")


def wait_new_url(driver, old_url):
    """

    :param driver: un objet webdriver
    :param old_url: l'ancienne URL
    :return: True lorsqu'une nouvelle URL a été chargée
    """
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(lambda driver: driver.current_url != old_url)
        return True
    except selenium.common.exceptions.TimeoutException:
        return False

def check_agreement_google(driver, timeout=20):
    """

    :param driver: Une instance webdriver
    :param timeout: Un temps d'attente maximal
    :return: Une instance webdriver après avoir accepté les conditions google.
    """
    time.sleep(5)
    x_path = "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button"
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "/html/body/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button"))).click()
    time.sleep(2.5)
    return driver
