import csv
import asyncio
from scraper.crawler import Crawler  # Corrected import path
from scraper.parser import Parser    # Corrected import path


async def save_data(url, section_data, output_csv_path):
    with open(output_csv_path, 'a', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file, quoting=csv.QUOTE_MINIMAL, doublequote=True)
        for content in section_data:
            # Sanitize content by replacing newlines, carriage returns, and escaping quotes
            content_sanitized = content.replace('\n', ' ').replace('\r', ' ').replace('"', '""')
            csv_writer.writerow([url, 'section', f'"{content_sanitized}"'])

def read_urls_from_csv(input_csv_path: str) -> List[str]:
    urls = []
    with open(input_csv_path, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader, None)  # Skip header
        for row in csvreader:
            urls.append(row[0])
    return urls

async def scrape_urls(urls, output_csv_path):
    for url in urls:
        crawler = Crawler(url)
        content = await crawler.fetch_content(url)
        if content:
            parser = Parser(content)
            parsed_data = parser.parse()
            await save_data(url, parsed_data, output_csv_path)

async def scrape_batch(urls, output_csv_path):
    for url in urls:
        crawler = Crawler(url)
        content = await crawler.fetch_content(url)
        if content:
            parser = Parser(content)
            # Assuming parse_sections returns a list of section contents
            section_data = parser.parse_sections()
            await save_data(url, section_data, output_csv_path)
        print(f"Scraped: {url}")  # Status update

async def main():
    input_csv_path = Path("data/urls.csv")
    output_csv_path = Path("/data/scraped_data.csv")

    # Initialize output CSV file with headers
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(['URL', 'HTML Tag', 'Content'])

    urls = read_urls_from_csv(input_csv_path)
    batch_size = int(input("Enter the number of URLs to scrape in a batch: "))

    for i in range(0, len(urls), batch_size):
        batch_urls = urls[i:i + batch_size]
        await scrape_batch(batch_urls, output_csv_path)
        print(f"Completed scraping {len(batch_urls)} URLs.")
        
        if i + batch_size < len(urls):  # Check if there are more URLs to scrape
            if input("Continue scraping? (y/n): ").lower() != 'y':
                break

if __name__ == "__main__":
    asyncio.run(main())