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
            "/html/body/jsl/div[3]/div[9]/div[8]/div/div[1]/div/div/div[1]/div[1]/button/img")
        size = elem.size["width"]
        if size == 408.0 or size == 426.0:
            print("One result")
            return False
        else:

            warnings.warn("Never saw this before ! Check this query ! Image format : " + str(size))
            return True
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

    try:
        return ((comp_name in activity or comp_name in enseigne or comp_name.lower() in driver.find_element_by_xpath(
            x_path).get_attribute("href")) & np.sum(
            [activity in auth_activity for auth_activity in authorized_activites]) >= 1)
    except selenium.common.exceptions.NoSuchElementException:
        try:
            return ((comp_name in activity or comp_name in enseigne or comp_name in driver.find_element_by_xpath(
                x_path).text) and np.sum([activity in auth_activity for auth_activity in authorized_activites]) >= 1)
        except selenium.common.exceptions.NoSuchElementException:
            return (comp_name in enseigne or comp_name in activity) and np.sum(
                [activity in auth_activity for auth_activity in authorized_activites]) >= 1
    except TypeError:
        return comp_name in enseigne or comp_name in activity

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
    try:
        # WebDriverWait(driver, timeout).until(
        # EC.frame_to_be_available_and_switch_to_it((By.XPATH, "/html/body/jsl/div[2]/div/div[1]/iframe")))
        WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="introAgreeButton"]')))
        driver.switch_to.frame(driver.find_elements_by_xpath("/html/body/jsl/div[2]/div/div[1]/iframe"))
        driver.find_element_by_xpath('//*[@id="introAgreeButton"]').click()
        """/html/body/div/c-wiz/div/div/div/div[2]/div[1]/div[4]/form/div[1]/div/button/div[1]"""
    except selenium.common.exceptions.TimeoutException:
        WebDriverWait(driver, timeout).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "/html/body/jsl/div[2]/div/div[1]/iframe")))
        driver.find_element_by_xpath('//*[@id="introAgreeButton"]').click()
    driver.switch_to.parent_frame()
    return driver
