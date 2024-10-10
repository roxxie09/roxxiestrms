import requests

def fetch_events(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()  # Parse the JSON response

        print(data)  # Debug: print the raw API response

        # Access the list of events under 'data'
        events = []
        for item in data.get('data', []):  # Safely access 'data' key
            event = {
                'title': item.get('name'),  # Use 'name' based on your API response
                'start_time': item.get('starts_at'),  # Use 'starts_at'
                'end_time': item.get('ends_at', item.get('starts_at') + 7200),  # Optional end time logic
                'url': f"https://ppv.land/live/{item.get('uri')}",  # Build the full URL
                'image_url': item.get('thumbnail')  # Use 'thumbnail'
            }
            events.append(event)

        return events

    except requests.exceptions.RequestException as e:
        print(f"Error fetching events: {e}")
        return []
