# Python 3.7.4 64-bit ('scrp': conda)
# Author: Adam Turner <turner.adch@gmail.com>

# standard library
import os
import re
import time
import shutil
import pathlib
from random import random
# third-party
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException


class SeleniumBot(object):

    def __init__(self, download_path, headless, wait):
        self.downloads = str(download_path)
        self.headless = headless
        self.wait = wait
        self.driver = None
        self.exp_wait = None

    def __driver_setup(self, geckodriver_path):
        fp = webdriver.FirefoxProfile()
        fp.set_preference("browser.download.folderList", 2)
        fp.set_preference("browser.download.manager.showWhenStarting", False)
        fp.set_preference("browser.download.dir", self.downloads)
        fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")

        opts = Options()
        if self.headless:
            opts.add_argument("--headless")

        driver = webdriver.Firefox(
            firefox_profile=fp,
            options=opts,
            executable_path=geckodriver_path
        )
        self.driver = driver
        self.exp_wait = WebDriverWait(self.driver, 10)
        print("Driver instance created.")

        return self

    def __random_wait(self):
        time.sleep(self.wait + random())

        return self

    def __wait_and_click(self, xpath):
        element = self.exp_wait.until(ec.element_to_be_clickable((By.XPATH, xpath)))
        element.click()

        return self

    def access_site(self):
        # NAVIGATE
        print("Surfing the Web...")
        self.driver.get("https://x.x.x")

        # LOGIN
        print("Looking for cookies...")
        self.__random_wait()
        self.__wait_and_click(xpath="//*[@id='cookieAgreeButton']")
        print("-> Cookies accepted.")

        print("Entering login information...")
        self.__random_wait()
        username = self.driver.find_element_by_xpath("//*[@id='usernameText']")
        username.clear()
        username.send_keys("x@x.com")

        self.__random_wait()
        password = self.driver.find_element_by_xpath("//*[@id='passwordText']")
        password.clear()
        password.send_keys("x")
        password.send_keys(Keys.RETURN)
        print("-> Logging in...")

        return self

    def reset_site_state(self):
        # RESET STATE
        try:
            self.__wait_and_click(xpath="//button[contains(., 'Refresh')")
            print("Current session was refreshed.")
        except TimeoutException:
            print("Current session is valid.")

        # selects 'Reset All'
        self.__random_wait()
        print("Resetting defaults...")
        self.__wait_and_click(xpath="//*[@title='Default all selections']")
        
        # once the reset is complete, the 'Type Specific' header will go away
        header_locator = (By.XPATH, "//div[@class='criteriaSection ng-scope']//div[contains(., 'Type Specific')]")
        self.exp_wait.until(ec.invisibility_of_element_located(header_locator))

        # selects 'Containerships' from 'Fleet Types'
        print("Selecting 'Containerships'...")
        self.__random_wait()
        self.__wait_and_click(xpath="//label[contains(., 'Containerships')]")

        # the "Type Specific" header returns when container ship update is complete
        self.exp_wait.until(ec.visibility_of_element_located(header_locator))

        return self

    def build_custom_grid(self):
        # clicks 'My Columns and Filters' and clears current fields
        print("Clicking 'My Columns'...")
        self.__random_wait()
        self.__wait_and_click(xpath="//button[contains(., 'Columns')]")
        
        # option is the last thing to load during modal fade
        option_locator = (By.XPATH, "//td[@class='selections-list']/select/option[1]")
        self.exp_wait.until(ec.element_to_be_clickable(option_locator))
        try:
            self.__wait_and_click(xpath="//button[contains(., 'Clear')]")
            print("Grid cleared.")
        except TimeoutException:
            print("Grid is already clear. Continuing...")

        print("Generating custom grid...")
        custom_filter = [
            'imo number', 'name', 'type', 'owner', 'operator', 'built date', 'draught',
            'loa', 'beam', 'gear', 'mmsi', 'speed', 'teu', 'reefer teu', 'tpc', 'consumption',
            'tanker category', 'sox scrubber details', 'sox scrubber 1 retrofit date', 'dwt',
            'electronic engine'
        ]
        for field in custom_filter:
            for _ in range(5):
                # search for field
                field_search = self.driver.find_element_by_xpath("//input[@ng-model='searchText']")
                field_search.clear()
                field_search.send_keys(field)

                option = self.exp_wait.until(ec.element_to_be_clickable(option_locator))
                # click on option if it matches the field
                if re.search(f"(?i){field}", option.text):
                    print(f"-> '{option.text}' matched regex: '{field}'")
                    option.click()
                    break
                else:
                    print(f"-> '{option.text}' did not match regex: '{field}'")
                    time.sleep(1)

            self.__wait_and_click(xpath="//td[@class='buttons-list grid add-gap']/button[contains(., 'Add')]")
            print(f"-> Added: {field}")
            self.__random_wait()

        print("Exiting 'My Columns'...")
        self.__wait_and_click(xpath="//button[contains(., 'OK')]")

        return self

    def download_sequence(self):
        # downloads 2 csv files but each can only contain 5000 records max
        # sorts ascending, downloads 5000 -> sorts descending, downloads 5000 -> drops dups later
        # note: this works for up to 10,000 items maximum
        print("Downloading csv files...")
        sort_order = ['asc', 'desc']
        for i in range(2):
            # sorts by 'IMO Number' column (column has 3 states: normal -> asc -> desc)
            self.__random_wait()
            self.__wait_and_click(xpath="//th[@data-title='IMO Number']/a")

            # confirm that imo column is now ordered correctly (i = 0: 'asc', i = 1: 'desc')
            for state in range(3):
                if state == 2:
                    raise ValueError("Data did not sort as expected.")
                else:
                    try:
                        self.exp_wait.until(
                            ec.visibility_of_element_located(
                                (By.XPATH, f"//th[@data-title='IMO Number' and @data-dir='{sort_order[i]}']/a")
                            )
                        )
                        print("IMO column is correctly sorted.")
                        break
                    except TimeoutException:
                        print("IMO column is incorrectly sorted. Changing sort state...")
                        self.__wait_and_click(xpath="//th[@data-title='IMO Number']/a")
                                        
            # clicking the export button
            self.__random_wait()
            self.__wait_and_click(xpath="//button[contains(., 'Export')]")
            # choosing the csv option
            self.__wait_and_click(xpath="//button[contains(., 'CSV')]")
            # accepting the terms and conditions of csv export
            self.__random_wait()
            self.__wait_and_click(xpath="//button[contains(., 'Accept')]")
            time.sleep(5)
            print(f"Download {i} complete.")
            continue
        
        return self

    def main(self):
        self.__driver_setup("/home/adam/utils/geckodriver-v0.26.0-linux64/geckodriver")
        self.access_site()
        self.reset_site_state()
        self.build_custom_grid()
        self.download_sequence()
        self.driver.close()

        return self


def main(random_wait_base=1):
    """'Scraper' subprocess: downloads csv files from client.

    Returns:
        str: path to directory that will house any downloaded csv files.
    """
    path_src = pathlib.Path(__file__).parent.absolute()
    path_tmp_data = path_src.parent / 'tmp_data'
    try:
        os.mkdir(path_tmp_data)
        print(f"Temporary download dir at:\n-> {path_tmp_data}")
    except FileExistsError:
        shutil.rmtree(path_tmp_data)
        os.mkdir(path_tmp_data)
        print(f"Leftover dir detected and replaced at:\n-> {path_tmp_data}")

    print("Launching SeleniumBot...")
    SeleniumBot(path_tmp_data, headless=True, wait=random_wait_base).main()

    return path_tmp_data


if __name__ == "__main__":
    main()
