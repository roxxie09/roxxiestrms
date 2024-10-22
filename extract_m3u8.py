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

    # Find all event links in upcoming events
    for card in soup.select('#upcoming-stream-cards a.item-card'):
        href = card.get('href')
        title_element = card.find('h5')  # Extract title from the card directly
        title = title_element.text.strip() if title_element else "Unknown Event"

        if href:
            print(f"Fetching stream from: {href} - Title: {title}")  # Debug output
            try:
                response = requests.get(href)
                response.raise_for_status()
                
                # Parse the stream page
                stream_soup = BeautifulSoup(response.text, 'html.parser')

                # Look for m3u8 links in the script tags or within the page
                found_links = set(re.findall(r'https?://[^\s]+\.m3u8', response.text))  # Use set to remove duplicates
                if found_links:
                    print(f"Found m3u8 links: {found_links}")  # Debug output
                links.append(f"{title}\n" + "\n".join(f"{link} (Stream {i+1})" for i, link in enumerate(found_links)))

            except Exception as e:
                print(f"Error fetching {href}: {e}")

    return list(set(links))  # Remove duplicates based on titles

def create_output_html(links):
    with open(OUTPUT_HTML_PATH, 'w', encoding='utf-8') as file:
        file.write("<!DOCTYPE html>\n<html lang='en'>\n<head>\n")
        file.write("<meta charset='UTF-8'>\n<title>M3U8 Links</title>\n</head>\n<body>\n")
        file.write("<h1>Available M3U8 Links</h1>\n<pre>\n")  # Use <pre> for formatting
        
        for link in links:
            file.write(f"{link}\n\n")  # Each event with its m3u8 links
        
        file.write("</pre>\n</body>\n</html>")

if __name__ == "__main__":
    links = extract_stream_links(INDEX_HTML_PATH)
    create_output_html(links)
    print(f"Extracted {len(links)} links and saved to {OUTPUT_HTML_PATH}")
