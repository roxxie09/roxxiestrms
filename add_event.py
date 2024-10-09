import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Function to parse the time and return a datetime object
def parse_time(time_str):
    return datetime.strptime(time_str, '%m/%d/%Y %I:%M %p')

# Function to create the event HTML block
def create_event_html(title, start_time, end_time, url, image_url):
    event_html = f'''
<div class="px-2 py-2" data-time="{start_time.strftime('%B %d, %Y %H:%M:%S GMT-0700')}" data-end-time="{end_time.strftime('%B %d, %Y %H:%M:%S GMT-0700')}">
    <a href="{url}" class="item-card">
        <div class="card bg-black text-white" style="width: 19rem;">
            <img src="{image_url}" width="285px" height="160px" alt="{title}" loading="lazy">
            <div class="card-body">
                <h5 class="card-title"><strong>{title}</strong></h5>
                <p class="card-text">
                    <span>Starts in: </span><span class="countdown-timer"></span>
                </p>
            </div>
        </div>
    </a>
</div>
'''
    return event_html

# Function to delete all events
def delete_all_events(soup):
    upcoming_streams = soup.find(id='upcoming-stream-cards')
    upcoming_streams.clear()
    return soup

# Main menu function
def main_menu():
    html_file_path = 'index.html'
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    while True:
        print("\nMenu:")
        print("1. Add New Event")
        print("2. Delete All Events")
        print("3. Exit")
        choice = input("Choose an option (1/2/3): ").strip()

        if choice == '1':
            # Get user input
            title = input("Title of event: ")

            # Get the current date
            now = datetime.now()
            current_year = 2024
            current_month = now.month
            current_day = now.day

            # Ask if the user wants to use the current month
            use_current_month = input(f"Use current month ({current_month})? (y/n): ").strip().lower()
            if use_current_month == 'y':
                month = current_month
            else:
                month = int(input("Enter month (1-12): "))

            # Ask if the user wants to use the current day
            use_current_day = input(f"Use current day ({current_day})? (y/n): ").strip().lower()
            if use_current_day == 'y':
                day = current_day
            else:
                day = int(input("Enter day (1-31): "))

            # Prompt for start time
            start_time_input = input(f"Enter starting time (HH:MM AM/PM): ")

            # Combine inputs into the start datetime object
            start_time = parse_time(f"{month}/{day}/{current_year} {start_time_input}")

            # Prompt for end time (optional)
            end_time_input = input("Enter ending time (HH:MM AM/PM, press Enter to skip): ")

            # Set the end time, default to 2 hours after start if not provided
            if end_time_input.strip() == "":
                end_time = start_time + timedelta(hours=2)  # Default to 2 hours after start
            else:
                end_time = parse_time(f"{month}/{day}/{current_year} {end_time_input}")

            # Get URL and image URL
            url = input("URL of event: ")
            image_url = input("Image URL of event: ")

            # Create the new event HTML
            new_event_html = create_event_html(title, start_time, end_time, url, image_url)

            # Find the upcoming stream cards
            upcoming_streams = soup.find(id='upcoming-stream-cards')

            # List to store existing events for sorting
            existing_events = []

            # Add existing events to the list
            for event in upcoming_streams.find_all('div', class_='px-2 py-2'):
                existing_time = datetime.strptime(event['data-time'], '%B %d, %Y %H:%M:%S GMT-0700')
                existing_events.append((existing_time, str(event)))

            # Append the new event to the list
            existing_events.append((start_time, new_event_html))

            # Sort events by start time
            existing_events.sort(key=lambda x: x[0])

            # Clear existing events in the HTML
            upcoming_streams.clear()

            # Write the sorted events back to the HTML
            for _, event_html in existing_events:
                upcoming_streams.append(BeautifulSoup(event_html, 'html.parser'))

            # Write the updated HTML back to the file
            with open(html_file_path, 'w', encoding='utf-8') as file:
                file.write(str(soup))

            print("Event added successfully!")

        elif choice == '2':
            # Delete all events
            soup = delete_all_events(soup)
            with open(html_file_path, 'w', encoding='utf-8') as file:
                file.write(str(soup))
            print("All events deleted successfully!")

        elif choice == '3':
            print("Exiting...")
            break

        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    main_menu()
