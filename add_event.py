import os

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
def add_event_to_html(event_html):
    with open('index.html', 'r') as file:
        content = file.readlines()

    # Find the position to insert the new event (before the closing div)
    for i, line in enumerate(content):
        if '</div>' in line:  # Adjust based on your HTML structure
            content.insert(i, event_html + '\n')
            break

    with open('index.html', 'w') as file:
        file.writelines(content)

# Main function
def main():
    title, start_time, end_time, url, image_url = get_event_details()
    event_html = create_event_html(title, start_time, end_time, url, image_url)
    add_event_to_html(event_html)
    print("Event added successfully!")

if __name__ == "__main__":
    main()
