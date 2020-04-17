##
# standard library
import os
import time
import random
import shutil
# third-party
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def main(random_wait_base=1):
    """'Scraper' subprocess: downloads .csv files from client.
    
    Arguments:
        random_wait_base (int): defines the base wait time for each random wait.

    Returns:
        str: path to directory that will house any downloaded .csv files.
    """
    # --- SETUP ---
    #   set the temporary directory to download the data
    #   enabling auto-download in Firefox profile settings
    #   setup code is mostly straight from the documentation FAQ:
    #       https://selenium-python.readthedocs.io/faq.html
    download_dir = os.getcwd() + "\\temp_data"

    try:
        os.mkdir(download_dir)
        print("Temporary download dir at:\n\t" + download_dir)
    except:
        shutil.rmtree(download_dir)
        os.mkdir(download_dir)
        print("Leftover 'temp_data' dir detected and replaced at:\n\t" + download_dir)

    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.download.dir", download_dir)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

    #   creating driver instance
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(
        firefox_profile=fp,
        options=options,
        executable_path="geckopath/geckodriver.exe"
    )
    # driver.maximize_window()
    explicit_wait = WebDriverWait(driver, 10)
    print("Driver instance created.")

    # --- NAVIGATION ---
    #   driving to the web page
    print("~ Surfing the Web ~")
    driver.get("https://xxxx.xxxxxxxxx.xxx/xxxx/xxxxx")

    #   accepts cookie policy
    time.sleep( random_wait_base + (random.randint(1, 10) / 10) )
    print("Cookie time!")
    try:
        cookie_button = driver.find_element_by_id("cookieAgreeButton")
        cookie_button.click()
        print("Cookies accepted.")
    except:
        print("Could not find cookie button! :(")

    #   logs in
    print("Entering login information...")
    time.sleep( random_wait_base + (random.randint(1, 10) / 10) )
    username = driver.find_element_by_id("usernameText")
    username.clear()
    username.send_keys("xxxxx.xxxx@xxxxxxxxxxx.com")
    time.sleep( random_wait_base + (random.randint(1, 10) / 10) )
    password = driver.find_element_by_id("passwordText")
    password.clear()
    password.send_keys("xxxxxxxxxxxx")
    print("Logging in...")
    password.send_keys(Keys.RETURN)

    #   'Your current session is no longer valid' bug workaround
    try:
        time.sleep( random_wait_base + (random.randint(1, 10) / 10) )
        explicit_wait.until(
            ec.element_to_be_clickable(
                (By.XPATH, "/html/body/div[11]/div/div/div[3]/div[2]/button[1]")
            )
        ).click()
        print("Auto bug fix: 'Current session is no longer valid'")
    except:
        print('Current session is valid.')

    #   selects 'Reset All'
    time.sleep( random_wait_base + (random.randint(1, 10) / 10) )
    print("Resetting defaults...")
    # reset_button = driver.find_element_by_xpath(
    #     "/html/body/div[2]/div[3]/div[2]/div/div/div/div[2]/div[1]/div[2]/button"
    # )
    # driver.execute_script("arguments[0].click();", reset_button)
    # print("Execute script required to click reset button.")
    explicit_wait.until(
        ec.element_to_be_clickable(
            # BREAK THIS FOR TESTING: /div[2]/button -> /div[99]/button
            (By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/div/div/div[2]/div[1]/div[2]/button")
        )
    ).click()
    print("Explicit wait required to click reset button.")

    #   selects 'Containerships' from 'Fleet Types'
    print("Selecting 'Containerships'...")
    time.sleep( random_wait_base + (random.randint(1, 10) / 10) )
    explicit_wait.until(
        ec.element_to_be_clickable(
            (By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/div/div/div[2]/div[3]/div[1]/div/div/div[3]/ul[2]/li[3]/label/input")
        )
    ).click()

    #   clicks 'My Columns and Filters' and clears current fields
    print("Clicking 'My Columns'...")
    time.sleep( random_wait_base + (random.randint(1, 10) / 10) )
    explicit_wait.until(
        ec.element_to_be_clickable(
            (By.XPATH, "/html/body/div[2]/div[3]/div[2]/div/div/div/div[2]/div[1]/button")
        )
    ).click()

    try:
        explicit_wait.until(
            ec.element_to_be_clickable(
                (By.XPATH, "/html/body/div[6]/div/div/div[2]/div/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td[1]/button[3]")
            )
        ).click()
    except:
        print("Could not find any pre-selected fields.")

    #   creates custom grid
    print("Generating custom grid...")
    custom_filter = [
        'imo number', 'name', 'type', 'owner', 'operator', 'built date', 'draught',
        'loa', 'beam', 'gear', 'mmsi', 'speed', 'teu', 'reefer teu', 'tpc', 'consumption',
        'tanker category', 'sox scrubber details', 'sox scrubber 1 retrofit date', 'dwt',
        'electronic engine'
    ]
    for field in custom_filter:
        # search for field name
        field_search = driver.find_element_by_xpath(
            "/html/body/div[6]/div/div/div[2]/div/div[3]/table/tbody/tr/td[1]/input"
        )
        field_search.clear()
        field_search.send_keys(field)
        time.sleep( random_wait_base + (random.randint(1, 10) / 10) )

        # click on result
        try:
            explicit_wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[6]/div/div/div[2]/div/div[3]/table/tbody/tr/td[1]/select/option[1]")
                )
            ).click()
        except:
            explicit_wait.until(
                ec.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[6]/div/div/div[2]/div/div[3]/table/tbody/tr/td[1]/select/option")
                )
            ).click()

        # add result to custom grid 'Grid Fields'
        time.sleep( random_wait_base + (random.randint(1, 10) / 10) )
        explicit_wait.until(
            ec.element_to_be_clickable(
                (By.XPATH, "/html/body/div[6]/div/div/div[2]/div/div[3]/table/tbody/tr/td[2]/table/tbody/tr[1]/td[1]/button[1]")
            )
        ).click()
        print("\t-> {}".format(field))
        time.sleep( random_wait_base + (random.randint(1, 10) / 10) )

    #   exits 'My Columns and Filters'
    print("Exiting My Columns...")
    ok_button = driver.find_element_by_xpath("/html/body/div[6]/div/div/div[3]/button[1]")
    driver.execute_script("arguments[0].click();", ok_button)

    #   downloads multiple .csv files
    #   sorts ascending, downloads 5000 -> sorts descending, downloads 5000
    #   note: this works for up to 10,000 items maximum
    print("Downloading .csv files...")
    for i in range(2):
        # sorts by 'IMO Number' column (column has 3 states: normal->asc->desc)
        time.sleep( random_wait_base + (random.randint(1, 10) / 10) )
        imo_column = driver.find_element_by_xpath(
            "/html/body/div[2]/div[3]/div[2]/div/div/div/div[2]/div[3]/div[3]/div/div[2]/div[2]/div/div[1]/div/table/thead/tr/th[3]/a"
        )
        driver.execute_script("arguments[0].click();", imo_column)

        # clicking the download button
        time.sleep( random_wait_base + (random.randint(1, 10) / 10) )
        download_button = driver.find_element_by_xpath(
            "/html/body/div[2]/div[3]/div[2]/div/div/div/div[2]/div[1]/div[5]/div[2]/button"
        )
        driver.execute_script("arguments[0].click();", download_button)

        # choosing the .csv option
        time.sleep( random_wait_base + (random.randint(1, 10) / 10) )
        csv_button = driver.find_element_by_xpath(
            "/html/body/div[2]/div[3]/div[2]/div/div/div/div[2]/div[1]/div[5]/div[2]/div/div/button[2]"
        )
        driver.execute_script("arguments[0].click();", csv_button)

        # accepting the terms and conditions of .csv export
        time.sleep( random_wait_base + (random.randint(1, 10) / 10) )
        accept_button = driver.find_element_by_xpath("/html/body/div[6]/div/div/div[3]/button[2]")
        driver.execute_script("arguments[0].click();", accept_button)
        print("\tDownload {} complete.".format(i))

    # --- EXIT ---
    driver.close()
    print('Selenium Subprocess complete.')

    return download_dir


if __name__ == "__main__":
    main()
