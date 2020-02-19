#!/usr/bin/env python3
# Python 3.7.4
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def main():
    """'Scraper' subprocess: downloads updated .csv from client

    --- SETUP ---
      enabling auto-download in Firefox profile settings
      this code is straight from the documentation FAQ:
          https://selenium-python.readthedocs.io/faq.html
      creates driver instance
    --- NAVIGATION ---
      drives to the web page
      accepts cookie policy
      logs in
      clicks filter grid and clears current fields
      creates custom grid
        searches for field name
        clicks on result
        add result to custom grid 
      exits filter grid
      clicks download button
      choosing the csv option
      accepting the terms and conditions of csv export
    --- EXIT ---
    """
    # --- SETUP ---
    #   enabling auto-download in Firefox profile settings
    #   this code is straight from the documentation FAQ:
    #       https://selenium-python.readthedocs.io/faq.html
    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", "a/dir")
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

    #   creates driver instance
    driver = webdriver.Firefox(firefox_profile=fp)
    driver.implicitly_wait(10)


    # --- NAVIGATION ---
    #   drives to the web page
    driver.get("https://xxxx.xxxxxxxxx.xxx/xxxx/xxxxxx")

    #   accepts cookie policy
    cookie_button = driver.find_element_by_id("cookieAgreeButton")
    cookie_button.click()

    #   logs in
    username = driver.find_element_by_id("usernameText")
    username.clear()
    username.send_keys("usr")
    password = driver.find_element_by_id("passwordText")
    password.clear()
    password.send_keys("pw")
    password.send_keys(Keys.RETURN)
    #driver.implicitly_wait(0)

    #   clicks filter grid and clears current fields
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/div/div/div[2]/div[1]/button"))).click()
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div/div/div[2]/div/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td[1]/button[3]"))).click()
    except:
        print("Could not find any pre-selected fields.")

    #   creates custom grid
    FILTER = [
        'imo number', 'name', 'type', 'owner', 'operator', 'built', 'built date', 'draught',
        'loa', 'beam', 'gear', 'mmsi', 'speed', 'teu', 'reefer teu', 'tpc', 'consumption',
        'tanker category', 'sox scrubber details', 'sox scrubber retrofit date'
    ]
    for field in FILTER:
        # searches for field name
        field_search = driver.find_element_by_xpath("/html/body/div[6]/div/div/div[2]/div/div[3]/table/tbody/tr/td[1]/input")
        field_search.clear()
        field_search.send_keys(field)
        time.sleep(1 + (random.randint(1, 10) / 10))
        # clicks on result
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div/div/div[2]/div/div[3]/table/tbody/tr/td[1]/select/option[1]"))).click()
        except:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div/div/div[2]/div/div[3]/table/tbody/tr/td[1]/select/option"))).click()        
        # add result to custom grid 
        time.sleep(1 + (random.randint(1, 10) / 10))
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div/div/div[2]/div/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td[1]/button[1]"))).click()
        time.sleep(1 + (random.randint(1, 10) / 10)) 

    #   exits filter grid
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div/div/div[3]/button[2]"))).click()

    #   clicks download button
    time.sleep(1 + (random.randint(1, 10) / 10))
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/div/div/div[2]/div[1]/div[5]/div[2]/button"))).click()

    #   choosing the csv option
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/div/div/div[2]/div[1]/div[5]/div[2]/div/div/button[2]"))).click()

    #   accepting the terms and conditions of csv export
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div/div/div[3]/button[2]"))).click()


    # --- EXIT ---
    driver.close()
    print('Subprocess complete.')
    return 1


if __name__ == "__main__":
    main()
