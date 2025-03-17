import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json

def fetch_events(api_url):
    # Set up Chrome options for Selenium (headless mode)
    options = Options()
    options.add_argument('--headless')  # Run Chrome in headless mode (no UI)
    options.add_argument('--disable-gpu')  # Disable GPU acceleration
    options.add_argument('--no-sandbox')  # To avoid issues in some environments

    # Set up ChromeDriver using webdriver_manager (automatically installs the correct version)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    events = []  # Initialize events list before starting the process

    try:
        # Open the URL using Selenium (this will bypass Cloudflare protection)
        driver.get(api_url)

        # Wait for the page to load (replace time.sleep with an explicit wait)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Extract page source after Cloudflare protection is bypassed
        page_source = driver.page_source

        # Optionally save the page source for debugging (remove in production)
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(page_source)

        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')

        # Look for the <script> tag containing JSON data
        json_script = soup.find('script', {'type': 'application/json'})
        if json_script:
            # Extract JSON data from the script tag
            data = json_script.string.strip()  # Strip to remove unwanted whitespace
            print("Extracted JSON Data: ", data)

            # Parse the events from the JSON data (assuming it's in the correct format)
            try:
                # Assuming the JSON data is in a valid format
                json_data = json.loads(data)

                # Extract events from the JSON data
                if isinstance(json_data, dict):
                    streams = json_data.get('streams', [])
                    for category in streams:
                        if 'streams' in category and isinstance(category['streams'], list):
                            for item in category['streams']:
                                event = {
                                    'title': item.get('name', 'No title available'),
                                    'start_time': item.get('starts_at'),
                                    'end_time': item.get('ends_at', item.get('starts_at') + 7200),  # Default to 2 hours if no 'ends_at'
                                    'url': f"https://ppv.land/live/{item.get('uri_name')}",  # Use 'uri_name' for URL
                                    'image_url': item.get('poster', '')  # Use 'poster' for image
                                }
                                events.append(event)
                print(f"Total events fetched: {len(events)}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                events = []  # Ensure events is initialized

        return events

    except Exception as e:
        print(f"Error while fetching events: {e}")
        return []

    finally:
        # Close the browser after fetching the data
        driver.quit()


# Example usage
api_url_upcoming = "https://ppv.land/api/streams?category=16&upcoming=true"
events_upcoming = fetch_events(api_url_upcoming)

# Print the fetched events (for debugging)
for event in events_upcoming:
    print(event)
