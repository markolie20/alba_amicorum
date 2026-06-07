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


with open("data/http___data.bibliotheken.nl_rise-alba.jsonld", "r", encoding="utf-8") as file:
    data = json.loads(file.readline())
    graph = data[0]['@graph']
    urls = list({entry['@id'] for entry in graph if '@id' in entry and '/alba/' in entry['@id']})


def scrape(url):
    options = Options()
    options.add_argument("--headless")

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

    result = {"url": url, "sections": []}
    for section in sections:
        entry = {"title": section.find('h5').text, "values": []}
        for description in section.find_all(class_='_literal_1urvj_24')[::2]:
            if description.find('span').find('span'):
                entry["values"].append(description.find('span').find('span').get('title'))
            else:
                entry["values"].append(description.find('span').text)
        for link in section.find_all(class_='_link_1thfn_4'):
            if link:
                entry["values"].append(link.text)
        result["sections"].append(entry)

    return result


OUTPUT = "data/scraped.jsonl"

# Resume: load already-scraped URLs
scraped_urls = set()
try:
    with open(OUTPUT, encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            scraped_urls.add(entry['url'])
    print(f"Resuming: {len(scraped_urls)} already scraped.")
except FileNotFoundError:
    pass

remaining = [u for u in urls if u not in scraped_urls]
total = len(urls)
done = len(scraped_urls)

with open(OUTPUT, 'a', encoding='utf-8') as f:
    for url in remaining:
        done += 1
        print(f"[{done}/{total}] Scraping {url}")
        result = scrape(url)
        f.write(json.dumps(result, ensure_ascii=False) + '\n')
        f.flush()

print("Done.")