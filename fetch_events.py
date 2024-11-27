import requests

def fetch_events(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()  # Parse the JSON response

        # Debugging: Print the raw response to inspect its structure
        print(f"API Response Raw: {data}")  # Print entire response data

        events = []  # List to store the events

        if isinstance(data, dict):
            # Extract the 'streams' directly
            streams = data.get('streams', [])  # Get the 'streams' key from the response

            if streams:
                print(f"Found {len(streams)} categories.")  # Debugging: How many categories
            else:
                print("No streams found in the data.")  # Debugging

            for category in streams:
                print(f"Processing category: {category.get('category')}")  # Debugging

                # Ensure 'streams' key exists within category and is a list
                if 'streams' in category and isinstance(category['streams'], list):
                    print(f"Found {len(category['streams'])} streams in category: {category.get('category')}")  # Debugging
                    for item in category['streams']:
                        event = {
                            'title': item.get('name', 'No title available'),
                            'start_time': item.get('starts_at'),
                            'end_time': item.get('ends_at', item.get('starts_at') + 7200),  # Default to 2 hours if no 'ends_at'
                            'url': f"https://ppv.land/live/{item.get('uri_name')}",  # Use 'uri_name' for URL
                            'image_url': item.get('poster', '')  # Use 'poster' for image
                        }
                        events.append(event)
                else:
                    print(f"No 'streams' found for category: {category.get('category')}")  # Debugging

        print(f"Total events fetched: {len(events)}")  # Debugging
        return events

    except requests.exceptions.RequestException as e:
        print(f"Error fetching events: {e}")
        return []

