import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time

import json
import re

with open("data/http___data.bibliotheken.nl_rise-alba.jsonld", "r", encoding="utf-8") as file:
    data = json.loads(file.readline())
    text = str(data)
    ids = re.findall(r"/alba/([A-Za-z0-9_-]+)", text)
    urls = ['http://data.bibliotheken.nl/id/alba/' + id for id in ids]

def scrape(url):

    options = Options()

    options.binary_location = "./scraping_requirements/firefox/firefox"

    service = Service(executable_path="./scraping_requirements/geckodriver-v0.36.0-linux64/geckodriver")

    driver = webdriver.Firefox(service=service, options=options)
    driver.get(url)

    time.sleep(2)

    while True:
        try:
            # Find ALL visible "Show more" buttons
            buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Show more')]")
            
            # Filter only visible ones
            visible_buttons = [b for b in buttons if b.is_displayed()]
            
            if not visible_buttons:
                print("No more 'Show more' buttons.")
                break
            
            # Click the first visible one
            btn = visible_buttons[0]
            
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            driver.execute_script("arguments[0].click();", btn)
            
            time.sleep(1) 

        except Exception as e:
            print("Done or error:", e)
            break

    html = driver.page_source
    driver.close()

    soup = bs(html, 'html.parser')
    sections = soup.find_all(class_='_outLink_1nmlh_136 _container_1urvj_33')

    for section in sections:
        print(section.find('h5').text)
        for description in section.find_all(class_='_literal_1urvj_24')[::2]:
            if description.find('span').find('span'):
                print(description.find('span').find('span').get('title'))
            else:
                print(description.find('span').text)

        for link in section.find_all(class_='_link_1thfn_4'):
            if link:
                print(link.text, f'href: {link.get('href')}')
        print()
    print('------------------------------------')

for url in urls[:5]:
    scrape(url)