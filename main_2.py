from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import requests
import csv
import json
import time

# File paths
csv_file_path = r"C:\Users\roberto.renteria\OneDrive - Unique Travel Vacation\Desktop\py8\data\urls.csv"
output_json_path = r"C:\Users\roberto.renteria\OneDrive - Unique Travel Vacation\Desktop\py8\data\structured_data.json"

# Path to GeckoDriver
gecko_driver_path = r"C:\Users\roberto.renteria\OneDrive - Unique Travel Vacation\Desktop\py8\webdriver\geckodriver.exe"

def read_urls_from_csv(file_path):
    urls = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and (row[0].startswith('http://') or row[0].startswith('https://')):
                urls.append(row[0])
    return urls

def scrape_url(url, use_selenium=False):
    try:
        if use_selenium:
            firefox_options = FirefoxOptions()
            firefox_options.add_argument("--headless")
            service = FirefoxService(executable_path=gecko_driver_path)
            with webdriver.Firefox(service=service, options=firefox_options) as driver:
                driver.get(url)
                time.sleep(2)  # Rate limiting to be respectful to servers
                soup = BeautifulSoup(driver.page_source, 'html.parser')
        else:
            response = requests.get(url, timeout=10)  # <|ISF|> Added timeout to requests.get
            response.raise_for_status()  # <|ISF|> Added to raise HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')

        if soup.find('footer'):
            soup.find('footer').decompose()
        page_data = {
            "URL": url,
            "Content": soup.get_text(separator=' ', strip=True)
        }
    except (requests.exceptions.RequestException, WebDriverException) as e:
        page_data = {
            "URL": url,
            "Error": str(e)
        }
    return page_data

urls = read_urls_from_csv(csv_file_path)

# <|ISF|> Parallelized scraping using ThreadPoolExecutor
from concurrent.futures import ThreadPoolExecutor

def scrape_all_urls(urls, use_selenium=False):
    structured_data = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(scrape_url, url, use_selenium) for url in urls]
        for future in futures:
            structured_data.append(future.result())
    return structured_data

structured_data = scrape_all_urls(urls, use_selenium=True)

with open(output_json_path, 'w', encoding='utf-8') as f:
    json.dump(structured_data, f, indent=4, ensure_ascii=False)

print("Scraping completed and data saved to JSON.")