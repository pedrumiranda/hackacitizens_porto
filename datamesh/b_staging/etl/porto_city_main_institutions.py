import os
import sys
import requests
import json

# Enabling json utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import application.services.json_file_utils as jfs

# Your Google API Key
API_KEY = '# Your Google API Key'


PORTO_CITY_MAIN_INSTITUTIONS = './datamesh/b_staging/datasets/porto_city_main_institutions.json'

# Define the base URL for Google Places API
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

# List of locations for searching (e.g., Porto, Lisbon, etc.)
locations = ["Paranhos, Porto","Bonfim, Porto","Porto, Portugal", "Ramalde, Porto, Portugal", "Boa Vista, Porto, Portugal", "Cedofeita, Porto, Portugal"," Matosinhos, Porto, Portugal"]

# Function to fetch places by type (school, university, hospital) and location
def fetch_places_by_type(query, location):
    # Create the search query (type + city)
    search_query = f"{query} in {location}"
    
    # Prepare the request URL
    url = f"{PLACES_API_URL}?query={search_query}&key={API_KEY}"
    
    # Send the GET request to Google Places API
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()  # Return the JSON response if successful
    else:
        print(f"Error fetching data for {location}: {response.status_code}")
        return None

def load_json_files(file_path):
    # Load the JSON file
    with open(file_path, 'r') as file:
        json_data = json.load(file)

    return json_data

# Function to extract relevant information from the Places API response
def extract_place_info(place_data, place_type, location):
    places_info = []
    
    for place in place_data.get("results", []):
        name = place.get("name")
        address = place.get("formatted_address")
        lat = place["geometry"]["location"].get("lat")
        lng = place["geometry"]["location"].get("lng")
        
        places_info.append({
            "name": name,
            "address": address,
            "lat": lat,
            "long": lng,
            "type": place_type,  # Add the type to the output
            "location": location  # Add the location to the output
        })
    
    return places_info

# Function to fetch and process multiple types (school, university, hospital) across multiple locations
def fetch_all_places():
    types = [
        "primary school", "university", "hospital", "school", 
        "public office", "shopping mall", "tourist attraction", "park", "community garden", "subway station", "train station"
    ]
    all_places = []
    
    # Iterate through each location
    for location in locations:
        for place_type in types:
            print(f"Fetching {place_type}s in {location}...")
            place_data = fetch_places_by_type(place_type, location)
            
            if place_data:
                places_info = extract_place_info(place_data, place_type, location)
                all_places.extend(places_info)  # Add all places to the final list
    
    return all_places

def main():
    # Fetch all places (primary schools, universities, and hospitals) in multiple locations
    places = fetch_all_places()

    # Output the results
    if places:

        jfs.save_to_file(places, PORTO_CITY_MAIN_INSTITUTIONS)

        print(f"Data has been saved to {PORTO_CITY_MAIN_INSTITUTIONS}")
    else:
        print("No places found or an error occurred.")

if __name__ == "__main__":
    main()