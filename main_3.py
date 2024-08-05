import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import csv
import logging
from aiohttp import ClientSession
from aiolimiter import AsyncLimiter
from concurrent.futures import ProcessPoolExecutor
import lxml

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Paths
csv_file_path = r"C:\Users\roberto.renteria\OneDrive - Unique Travel Vacation\Desktop\py8\data\urls.csv"
output_csv_path = r"C:\Users\roberto.renteria\OneDrive - Unique Travel Vacation\Desktop\py8\data\scraped_data.csv"

# Ensure the output directory exists
os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)

# Rate limiter: 5 requests per second
rate_limit = AsyncLimiter(5, 1)

# CSS selector for common HTML content tags
common_tags_selector = '.main-content p, .main-content h1, .main-content h2, .main-content h3, .main-content h4, .main-content h5, .main-content h6, .main-content li, .main-content a, .main-content img'

def read_urls_from_csv(file_path):
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip the header if present
        return [row[0].strip() for row in reader]

async def fetch_url(session, url):
    async with rate_limit:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            return None

def parse_html(html, url):
    if html is None:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    footer = soup.find('footer')
    if footer:
        footer.decompose()
    
    scraped_data = []
    for element in soup.select(common_tags_selector):
        tag = element.name
        if tag == 'a':
            anchor_text = element.get_text(strip=True)
            href = element.get('href', '')
            content = f"Anchor Text: {anchor_text} Url: {href}"
        elif tag == 'img':
            alt_text = element.get('alt', '')
            src = element.get('src', '')
            content = f"Alt Text: {alt_text} Source: {src}"
        else:
            content = ' '.join(element.stripped_strings)
        
        scraped_data.append([url, tag, content])
    
    return scraped_data

async def scrape_url(session, url):
    html = await fetch_url(session, url)
    return parse_html(html, url)

async def main(urls):
    async with ClientSession() as session:
        tasks = [scrape_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    
    return [item for sublist in results for item in sublist]

if __name__ == "__main__":
    urls = read_urls_from_csv(csv_file_path)
    
    # Use ProcessPoolExecutor for multiprocessing
    with ProcessPoolExecutor() as executor:
        loop = asyncio.get_event_loop()
        scraped_data = loop.run_until_complete(main(urls))
    
    # Write all data to CSV at once
    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['URL', 'Tag', 'Content'])
            writer.writerows(scraped_data)
        logging.info(f"Data scraping completed. Results saved to {output_csv_path}")
    except Exception as e:
        logging.error(f"Error writing to {output_csv_path}: {str(e)}")