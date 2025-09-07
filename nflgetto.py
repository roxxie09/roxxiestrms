from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Load the nfl.html file
with open('nfl.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Find all the <tr> rows in the schedule table
rows = soup.find_all('tr')

# Function to parse and format the event time
def format_event_time(event_time_str):
    try:
        # Common format: "September 07, 2025 8:15 PM"
        event_time = datetime.strptime(event_time_str, '%B %d, %Y %I:%M %p')
    except ValueError:
        # Alternative format if needed
        event_time = datetime.strptime(event_time_str, '%B %d, %Y %H:%M')
    return event_time

# Loop through each row and update countdown timer
for row in rows:
    tds = row.find_all('td')
    if len(tds) >= 3:
        event_time_str = tds[1].get_text(strip=True)  # Assuming second column has event time
        try:
            formatted_event_time = format_event_time(event_time_str)
        except Exception as e:
            print(f"Skipping row due to time parse error: {e}")
            continue
        
        countdown_timer = tds[2].find('span', class_='countdown-timer')
        if countdown_timer:
            countdown_timer['data-start'] = formatted_event_time.strftime('%B %d, %Y %H:%M:%S')
            end_time = formatted_event_time + timedelta(hours=4)  # NFL game approx 4 hours max
            countdown_timer['data-end'] = end_time.strftime('%B %d, %Y %H:%M:%S')

# Save the updated HTML back to the file
with open('nfl.html', 'w', encoding='utf-8') as file:
    file.write(str(soup))

print("NFL HTML schedule updated successfully!")
