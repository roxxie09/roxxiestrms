from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Load the mlb.html file
with open('mlb.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Find all the <tr> rows in the table
rows = soup.find_all('tr')

# Function to parse and format the event time
def format_event_time(event_time_str):
    # Convert the event time string into a datetime object
    try:
        event_time = datetime.strptime(event_time_str, '%B %d, %Y %H:%M %p')
    except ValueError:
        # Fallback in case the format doesn't match exactly
        event_time = datetime.strptime(event_time_str, '%B %d, %Y %H:%M %M')
    return event_time

# Loop through each row and update the countdown timer data-start and data-end attributes
for row in rows:
    # Find all the <td> elements in the row
    tds = row.find_all('td')
    
    # Make sure the row contains at least 3 <td> elements (Event, Start Time, Countdown)
    if len(tds) >= 3:
        event_time_str = tds[1].get_text(strip=True)  # Get the start time from the second column

        # Format the event time
        formatted_event_time = format_event_time(event_time_str)

        # Find the countdown timer (third <td> in the row)
        countdown_timer = tds[2].find('span', class_='countdown-timer')
        
        if countdown_timer:
            # Set the data-start attribute to the formatted event time
            countdown_timer['data-start'] = formatted_event_time.strftime('%B %d, %Y %H:%M:%S')

            # Set the data-end attribute to 2 hours after the event start time
            end_time = formatted_event_time + timedelta(hours=23)
            countdown_timer['data-end'] = end_time.strftime('%B %d, %Y %H:%M:%S')

# Save the updated HTML back to the file
with open('mlb.html', 'w', encoding='utf-8') as file:
    file.write(str(soup))

print("HTML file updated successfully!")
