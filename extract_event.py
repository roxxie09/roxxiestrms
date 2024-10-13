from bs4 import BeautifulSoup
from datetime import datetime

# Read the index.html file
with open('index.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'lxml')

# Get the current date in mm/dd format
current_date = datetime.now().strftime('%m/%d')

# Open a new text file to write the results
with open('events.txt', 'w', encoding='utf-8') as output_file:
    # Write the current date at the top
    output_file.write(f"{current_date} events:\n\n")
    
    # Find all upcoming events
    upcoming_events = soup.find_all('div', class_='px-2 py-2')
    
    for event in upcoming_events:
        # Find the event name
        event_title = event.find('h5', class_='card-title').get_text(strip=True)
        # Find the corresponding URL
        event_link = event.find('a', class_='item-card')['href']
        
        # Write the result to the file
        output_file.write(f"{event_title}: {event_link}\n")

print("Event names and URLs have been extracted to events.txt.")
