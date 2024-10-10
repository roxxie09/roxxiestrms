import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from fetch_events import fetch_events  # Import the fetch function

# Function to parse the time and return a datetime object
def parse_time(time_str):
    return datetime.strptime(time_str, '%m/%d/%Y %I:%M %p')

# Function to create the event HTML block
def create_event_html(title, start_time, url, image_url, end_time=None):
    end_time_attr = f'data-end-time="{end_time.strftime("%B %d, %Y %H:%M:%S GMT-0700")}"' if end_time else ''
    event_html = f'''
<div class="px-2 py-2" data-time="{start_time.strftime('%B %d, %Y %H:%M:%S GMT-0700')}" {end_time_attr}>
    <a href="{url}" class="item-card">
        <div class="card bg-black text-white" style="width: 18rem;">
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

    api_url_upcoming = "https://ppv.land/api/streams?category=16&upcoming=true"
    api_url_live = "https://ppv.land/api/streams?category=16&live=true"

    # Fetch events once at startup to populate the list
    events_upcoming = fetch_events(api_url_upcoming)
    events_live = fetch_events(api_url_live)

    while True:
        print("\nMenu:")
        print("1. Add New Event")
        print("2. Delete All Events")
        print("3. List All Events")
        print("4. Exit")
        choice = input("Choose an option (1/2/3/4): ").strip()

        if choice == '1':
            # Get user input for event details
            title = input("Title of event: ")
            now = datetime.now()
            current_year = 2024
            current_month = now.month
            current_day = now.day

            use_current_month = input(f"Use current month ({current_month})? (y/n): ").strip().lower()
            month = current_month if use_current_month == 'y' else int(input("Enter month (1-12): "))

            use_current_day = input(f"Use current day ({current_day})? (y/n): ").strip().lower()
            day = current_day if use_current_day == 'y' else int(input("Enter day (1-31): "))

            start_time_input = input(f"Enter starting time (HH:MM AM/PM): ")
            start_time = parse_time(f"{month}/{day}/{current_year} {start_time_input}")

            end_time_input = input("Enter ending time (HH:MM AM/PM, press Enter to skip): ")
            end_time = None
            if end_time_input.strip():
                end_time = parse_time(f"{month}/{day}/{current_year} {end_time_input}")

            # If end_time is None, default to two hours after start_time
            if end_time is None:
                end_time = start_time + timedelta(hours=2)

            # Prompt for URL and Image URL
            url = input("URL of event: ")
            image_url = input("Image URL of event: ")

            new_event_html = create_event_html(title, start_time, url, image_url, end_time)  
            upcoming_streams = soup.find(id='upcoming-stream-cards')

            existing_events = []
            for event in upcoming_streams.find_all('div', class_='px-2 py-2'):
                existing_time = datetime.strptime(event['data-time'], '%B %d, %Y %H:%M:%S GMT-0700')
                existing_events.append((existing_time, str(event)))

            existing_events.append((start_time, new_event_html))
            existing_events.sort(key=lambda x: x[0])
            upcoming_streams.clear()

            for _, event_html in existing_events:
                upcoming_streams.append(BeautifulSoup(event_html, 'html.parser'))

            with open(html_file_path, 'w', encoding='utf-8') as file:
                file.write(str(soup))

            print("Event added successfully!")

        elif choice == '2':
            soup = delete_all_events(soup)
            with open(html_file_path, 'w', encoding='utf-8') as file:
                file.write(str(soup))
            print("All events deleted successfully!")

        elif choice == '3':
            # Combine live and upcoming events
            events = events_live + events_upcoming

            if not events:
                print("No events available.")
                continue

            print("Available Events:")
            for i, event in enumerate(events):
                title = event['title']
                start_time = datetime.fromtimestamp(event['start_time'])
                end_time = datetime.fromtimestamp(event.get('end_time', event['start_time'] + 7200))  
                print(f"{i + 1}. {title} (Starts at {start_time})")

            event_choice = int(input("Choose the event number to add to your list: ")) - 1
            if 0 <= event_choice < len(events):
                event = events[event_choice]

                title = event['title']
                start_time = datetime.fromtimestamp(event['start_time'])
                end_time = datetime.fromtimestamp(event.get('end_time', start_time + timedelta(hours=2)))
                url = event['url']
                image_url = event['image_url']

                new_event_html = create_event_html(title, start_time, url, image_url, end_time)

                upcoming_streams = soup.find(id='upcoming-stream-cards')

                # Collect existing events
                existing_events = []
                for existing_event in upcoming_streams.find_all('div', class_='px-2 py-2'):
                    existing_time = datetime.strptime(existing_event['data-time'], '%B %d, %Y %H:%M:%S GMT-0700')
                    existing_events.append((existing_time, str(existing_event)))

                # Add new event and sort
                existing_events.append((start_time, new_event_html))
                existing_events.sort(key=lambda x: x[0])  
                upcoming_streams.clear()

                for _, event_html in existing_events:
                    upcoming_streams.append(BeautifulSoup(event_html, 'html.parser'))

                with open(html_file_path, 'w', encoding='utf-8') as file:
                    file.write(str(soup))

                print("Event added successfully!")
            else:
                print("Invalid selection.")

        elif choice == '4':
            print("Exiting...")
            break

        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    main_menu()
