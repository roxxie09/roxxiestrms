import os
import requests
from bs4 import BeautifulSoup
import re

# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Paths to your files
INDEX_HTML_PATH = os.path.join(current_directory, 'index.html')
OUTPUT_HTML_PATH = os.path.join(current_directory, 'm3u8.html')

def extract_stream_links(index_html):
    links = []
    
    with open(index_html, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find all event links
    for card in soup.find_all('a', class_='item-card'):
        href = card.get('href')
        if href and 'nfl-streams' in href:
            # Fetch the stream page
            try:
                response = requests.get(href)
                response.raise_for_status()
                
                # Parse the stream page
                stream_soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for m3u8 links in the script tags or within the page
                for script in stream_soup.find_all('script'):
                    if script.string:  # Check if the script has content
                        m3u8_links = re.findall(r'https?://[^\s]+\.m3u8', script.string)
                        links.extend(m3u8_links)

                # Alternatively, if .m3u8 links are in <a> tags
                for link in stream_soup.find_all('a', href=True):
                    if link['href'].endswith('.m3u8'):
                        links.append(link['href'])
                        
            except Exception as e:
                print(f"Error fetching {href}: {e}")

    return list(set(links))  # Remove duplicates

def create_output_html(links):
    with open(OUTPUT_HTML_PATH, 'w', encoding='utf-8') as file:
        file.write("<!DOCTYPE html>\n<html lang='en'>\n<head>\n")
        file.write("<meta charset='UTF-8'>\n<title>M3U8 Links</title>\n</head>\n<body>\n")
        file.write("<h1>Available M3U8 Links</h1>\n<ul>\n")
        
        for link in links:
            file.write(f"<li><a href='{link}'>{link}</a></li>\n")
        
        file.write("</ul>\n</body>\n</html>")

if __name__ == "__main__":
    links = extract_stream_links(INDEX_HTML_PATH)
    create_output_html(links)
    print(f"Extracted {len(links)} links and saved to {OUTPUT_HTML_PATH}")
