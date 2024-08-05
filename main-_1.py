import os
import requests
from bs4 import BeautifulSoup
import csv

# Path to the CSV file containing URLs
csv_file_path = r"C:\Users\roberto.renteria\OneDrive - Unique Travel Vacation\Desktop\py8\data\urls.csv"

# Output path for the scraped data CSV
output_csv_path = r"C:\Users\roberto.renteria\OneDrive - Unique Travel Vacation\Desktop\py8\data\scraped_data.csv"

# Ensure the output directory exists
output_dir = os.path.dirname(output_csv_path)
os.makedirs(output_dir, exist_ok=True)

# Function to read URLs from a CSV file
def read_urls_from_csv(file_path):
    urls = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip the header if present
        for row in reader:
            urls.append(row[0].strip())
    return urls

# CSS selector for common HTML content tags, including links and images
common_tags_selector = '.main-content p, .main-content h1, .main-content h2, .main-content h3, .main-content h4, .main-content h5, .main-content h6, .main-content li, .main-content a, .main-content img'

# Prepare the output CSV with headers
try:
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['URL', 'Tag', 'Content'])
except Exception as e:
    print(f'Error initializing output CSV: {str(e)}')
    exit(1)

# Call the function to get the list of URLs
urls = read_urls_from_csv(csv_file_path)

# Loop over each URL and scrape data
for url in urls:
    try:
        response = requests.get(url)
        response.raise_for_status()  # Handle HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Exclude footer
        footer = soup.find('footer')
        if footer:
            footer.decompose()
        
        scraped_data = []
        for element in soup.select(common_tags_selector):
            tag = element.name
            if tag == 'a':
                # Format for <a> tags
                anchor_text = element.get_text(strip=True)
                href = element.get('href', '')
                content = f"Anchor Text: {anchor_text} Url: {href}"
            elif tag == 'img':
                # Format for <img> tags
                alt_text = element.get('alt', '')
                src = element.get('src', '')
                content = f"Alt Text: {alt_text} Source: {src}"
            else:
                # General format for other tags
                content = ' '.join(element.stripped_strings)
            
            scraped_data.append([url, tag, content])

        # Append the scraped data to the CSV file
        try:
            with open(output_csv_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(scraped_data)

            print(f'Data scraping for {url} completed and saved to CSV.')
        except PermissionError as e:
            print(f'Permission error when writing to {output_csv_path}: {str(e)}')
        except Exception as e:
            print(f'Error writing to {output_csv_path}: {str(e)}')

    except requests.RequestException as e:
        print(f'Error scraping {url}: {str(e)}')
    except Exception as e:
        print(f'Error processing {url}: {str(e)}')
