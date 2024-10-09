import os
from datetime import datetime

# Function to get user input for event details
def get_event_details():
    title = input("Title of event: ")
    start_time = input("Starting time (e.g., October 9, 2024 18:00:00 GMT-0700): ")
    end_time = input("Ending time (e.g., October 9, 2024 21:00:00 GMT-0700): ")
    url = input("URL of the event: ")
    image_url = input("Image URL of the event: ")
    
    return title, start_time, end_time, url, image_url

# Function to create the event HTML
def create_event_html(title, start_time, end_time, url, image_url):
    return f'''
<div class="px-2 py-2" data-time="{start_time}" data-end-time="{end_time}">
    <a href="{url}" class="item-card">
        <div class="card bg-black text-white" style="width: 19rem;">
            <img src="{image_url}" alt="{title}" loading="lazy">
            <div class="card-body">
                <h5 class="card-title"><strong>{title}</strong></h5>
                <p class="card-text">
                    <span class="countdown-label">Starts in: </span><span class="countdown-timer"></span>
                </p>
            </div>
        </div>
    </a>
</div>
'''

# Function to insert the new event into index.html
def add_event_to_html(event_html, event_time):
    with open('index.html', 'r') as file:
        content = file.readlines()

    # Find where to insert new events
    event_insert_index = None
    events = []

    # Parse existing event times
    for i, line in enumerate(content):
        if 'data-time' in line:
            time_str = line.split('data-time="')[1].split('"')[0]
            events.append((datetime.strptime(time_str, '%B %d, %Y %H:%M:%S GMT%z'), line))
        
        # Find the insert position
        if event_insert_index is None and 'Upcoming Events' in line:
            event_insert_index = i + 2  # Insert after the header

    # Append the new event
    new_event_time = datetime.strptime(event_time, '%B %d, %Y %H:%M:%S GMT%z')
    events.append((new_event_time, event_html))

    # Sort events by time
    events.sort(key=lambda x: x[0])

    # Write back the original content up to the event insert index
    with open('index.html', 'w') as file:
        for line in content[:event_insert_index]:
            file.write(line)
        # Write the sorted events
        for _, line in events:
            file.write(line)
        # Write the remaining content
        for line in content[event_insert_index:]:
            file.write(line)

# Main function to run the script
def main():
    title, start_time, end_time, url, image_url = get_event_details()
    event_html = create_event_html(title, start_time, end_time, url, image_url)
    add_event_to_html(event_html, start_time)

if __name__ == "__main__":
    main()
