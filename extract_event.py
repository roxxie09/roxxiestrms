from bs4 import BeautifulSoup
from datetime import datetime

# Function to extract events and save them to a text file
def extract_events_from_file(html_file, category, output_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find all the <a> tags within <td> tags for events
    events = soup.find_all('td', {'class': None})  # Adjust if necessary

    with open(output_file, 'a', encoding='utf-8') as output:
        # Write category header
        output.write(f'{category}:\n')

        # Write each event under the category
        for event in events:
            link = event.find('a')
            if link:
                title = link.text.strip()
                href = link.get('href')
                output.write(f'{title}: {href}\n')

        # Add a newline for separation between categories
        output.write('\n')

# Get today's date in the format: March 06, 2025
today_date = datetime.now().strftime("%B %d, %Y")

# Specify the output text file
output_file = 'events.txt'

# Clear any previous contents of the output file
with open(output_file, 'w', encoding='utf-8') as output:
    # Write the date at the top of the file
    output.write(f'Date: {today_date} Events\n\n')

# Extract events for each category (Soccer, NBA, Motorsports, Fighting, NFL)
extract_events_from_file('soccer.html', 'Soccer', output_file)
extract_events_from_file('nba.html', 'NBA', output_file)
extract_events_from_file('motorsports.html', 'Motorsports', output_file)
extract_events_from_file('fighting.html', 'Fighting', output_file)
extract_events_from_file('nfl.html', 'NFL', output_file)
extract_events_from_file('march-madness.html', 'March Madness', output_file)

print(f'Events have been extracted and saved to {output_file}')
