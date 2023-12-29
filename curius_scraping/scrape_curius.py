from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service
from typing import Dict, List
import time
import json
import csv
import os
from datetime import datetime, timezone
import configparser

# Constants
CUR_DIR = os.path.dirname(os.path.realpath(__file__))

# use configparser to read in INI file
config = configparser.ConfigParser()
config.read(os.path.join(CUR_DIR, '..', 'constants.ini'))

LINK_DUMP = os.path.join(config.get("CONSTANTS", "DATA_DIR"), f"links_{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S_%Z')}.json")
EDGE_DRIVER_PATH = os.path.join(CUR_DIR, "msedgedriver")

CURIUS_LINK = config.get("CONSTANTS", "CURIUS_LINK")

# CSS selectors
LINK_CSS_CLASS = "css-1eicj7r"
NEXT_BUTTON_SELECTOR = "#app > div > div > div.MuiGrid-root.MuiGrid-container > div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-sm-7 > div > div.css-gsabod > span:nth-child(2)"


def create_webdriver():
    # Set up Edge in headless mode
    edge_options = EdgeOptions()
    edge_options.use_chromium = True
    edge_options.add_argument("--headless")
    edge_options.add_argument("--disable-gpu")

    service = Service(EDGE_DRIVER_PATH)
    return webdriver.Edge(service=service, options=edge_options)


def click_button(driver, selector):
    button = driver.find_element(By.CSS_SELECTOR, selector)
    # check if it exists
    if button:
        try:
            button.click()
            return True
        except:
            print("reached end of links")
            pass
    return False


def save_links_to_file(links: List[Dict], json_file_path):
    # take incoming python dict and then convert to JSON and append to existing JSON list in file

    # Read the existing data from the file
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        # If the file does not exist, start with an empty list
        data = []

    # Append the new dictionary to the list
    data.extend(links)

    # Write the updated list back to the file
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=4)

    # Provide the path to the updated file
    return json_file_path


def extract_links_from_webelement(webelement: WebElement):
    # extract text from webelements and split on newline
    element_components = webelement.text.split("\n")

    # extract links from webelement
    nested_link_tags = webelement.find_elements(By.TAG_NAME, "a")
    nested_urls = [link.get_attribute(
        'href') for link in nested_link_tags if link.get_attribute('href')]

    # TODO: handle more advanced scraping of remaining elements later

    return {
        # title of webpage
        "title": element_components[0],
        # the website it came from
        "website": element_components[1],
        # "link": element_components[2],
        "urls": nested_urls,
    }


def scrape_site(site_url: str):
    driver = create_webdriver()
    try:
        # load initial bookmark page
        driver.get(site_url)
        time.sleep(2)

        # click next button until no more links
        scrape_next_page = True
        while scrape_next_page:
            # select all divs with class LINK_CSS_CLASS
            links: List[WebElement] = driver.find_elements(
                By.CLASS_NAME, LINK_CSS_CLASS)

            # map each link to dict
            links_as_dicts = list(map(extract_links_from_webelement, links))

            # save links to file
            save_links_to_file(links_as_dicts, LINK_DUMP)

            scrape_next_page = click_button(driver, NEXT_BUTTON_SELECTOR)
            time.sleep(2)
    finally:
        driver.quit()


if __name__ == "__main__":
    print(CURIUS_LINK)
