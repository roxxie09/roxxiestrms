import requests
from bs4 import BeautifulSoup
import re

def extract_stream_links(html_path, event_type):
    links = []
    
    # Open the HTML file and parse with BeautifulSoup
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Determine the event selector based on event type (nba, soccer, march-madness, fighting, motorsports)
    if event_type == 'nba':
        event_selector = '#eventsTable tbody tr'  # Adjust if needed
    elif event_type == 'soccer':
        event_selector = '#eventsTable tbody tr'  # Adjust if needed for soccer
    elif event_type == 'fighting':
        event_selector = '#eventsTable tbody tr'  # Adjust if needed for Fighting events
    elif event_type == 'motorsports':
        event_selector = '#eventsTable tbody tr'  # Adjust if needed for Motorsports events
    else:
        raise ValueError("Invalid event type")

    # Debug: Notify that the parsing has started
    print(f"Started extracting {event_type} stream links...")

    # Loop through the rows in the event table
    for row in soup.select(event_selector):
        try:
            # Try to extract the event name and link
            event_name_cell = row.find('td')
            if event_name_cell:
                event_link_tag = event_name_cell.find('a')
                if event_link_tag:
                    event_name = event_link_tag.text.strip()
                    event_link = event_link_tag.get('href')
                    if event_link:
                        print(f"Fetching stream from: {event_link} - Title: {event_name}")
                        try:
                            response = requests.get(event_link)
                            response.raise_for_status()
                            
                            # Parse the stream page
                            stream_soup = BeautifulSoup(response.text, 'html.parser')

                            # Extract m3u8 links from the page
                            found_links = set(re.findall(r'https?://[^\s]+\.m3u8', response.text))
                            if found_links:
                                print(f"Found m3u8 links: {found_links}")
                            else:
                                print(f"No m3u8 links found for: {event_name}")
                            links.append(f"<strong>{event_name}</strong><br>" + "<br>".join(f"<a href='{link}'>{link}</a> (Stream {i+1})<br>" for i, link in enumerate(found_links)))
                        except Exception as e:
                            print(f"Error fetching {event_link}: {e}")
                else:
                    print(f"Skipping row due to missing <a> tag in event: {row}")
            else:
                print(f"Skipping row due to missing <td> tag in event: {row}")
        except Exception as e:
            print(f"Error processing row: {e}")
    
    # Print completion message
    if links:
        print(f"Finished extracting {len(links)} stream links.")
    else:
        print("No stream links found.")

    return links  # Return the list of links as HTML formatted strings


# Main execution starts here
NBA_HTML_PATH = 'nba.html'  # Path to NBA HTML file
SOCCER_HTML_PATH = 'soccer.html'  # Path to Soccer HTML file
FIGHTING_HTML_PATH = 'fighting.html'  # Path to Fighting HTML file
MOTOSPORTS_HTML_PATH = 'motorsports.html'  # Path to Motorsports HTML file

# Extract links for NBA, Soccer, March Madness, Fighting, and Motorsports
nba_links = extract_stream_links(NBA_HTML_PATH, 'nba')
soccer_links = extract_stream_links(SOCCER_HTML_PATH, 'soccer')
fighting_links = extract_stream_links(FIGHTING_HTML_PATH, 'fighting')
motorsports_links = extract_stream_links(MOTOSPORTS_HTML_PATH, 'motorsports')

# Create the HTML content
html_content = """
<html>
<head><title>Stream Links</title></head>
<body>
<h1>Stream Links</h1>
<h2>NBA Streams</h2>
<div>
    {}
</div>
<h2>Soccer Streams</h2>
<div>
    {}
</div>
<h2>Fighting Streams</h2>
<div>
    {}
</div>
<h2>Motorsports Streams</h2>
<div>
    {}
</div>
</body>
</html>
""".format("<br><hr>".join(nba_links), "<br><hr>".join(soccer_links), "<br><hr>".join(fighting_links), "<br><hr>".join(motorsports_links))

# Write the HTML content to m3u8.html
with open("m3u8.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("m3u8.html has been created.")
