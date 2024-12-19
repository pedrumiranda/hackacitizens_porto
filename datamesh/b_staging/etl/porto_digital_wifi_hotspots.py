import pandas as pd
import requests
import json

RAW_DATA_PORTO_DIGITAL_WIFI_HOTSPOTS = './datamesh/a_raw_data/datasets/hackacity/aps_hackacity.csv'

# Your Google API Key
API_KEY = '# Your Google API Key'

# Function to get address from latitude and longitude using Google Geocoding API
def get_address_from_latlon(lat, lon):
    geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={API_KEY}'
    response = requests.get(geocode_url)
    
    if response.status_code == 200:
        result = response.json()
        if result['status'] == 'OK':
            return result['results'][0]['formatted_address']
        else:
            return None  # If no result found
    else:
        print(f"Error with Geocoding API: {response.status_code}")
        return None

# Load the CSV into a pandas DataFrame
file_path = RAW_DATA_PORTO_DIGITAL_WIFI_HOTSPOTS

# Main execution
if __name__ == "__main__":

    # Load the data
    df = pd.read_csv(file_path, delimiter=';')

    # Rename 'MAC Radius' column to 'MAC_ADDRESS'
    df_renamed = df.rename(columns={'MAC Radius': 'MAC_ADDRESS'})

    # Convert Latitude and Longitude to numeric, replacing commas with dots and coercing non-numeric values to NaN
    df_renamed['Latitude'] = pd.to_numeric(df_renamed['Latitude'].str.replace(',', '.'), errors='coerce')
    df_renamed['Longitude'] = pd.to_numeric(df_renamed['Longitude'].str.replace(',', '.'), errors='coerce')

    # Remove rows with empty Latitude or Longitude
    df_cleaned = df_renamed.dropna(subset=['Latitude', 'Longitude'])

    # Remove duplicate records based on Latitude and Longitude
    df_cleaned = df_cleaned.drop_duplicates(subset=['Latitude', 'Longitude'])

    # Rename 'Latitude' and 'Longitude' columns to 'lat' and 'lon'
    df_cleaned = df_cleaned.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'})

    # Add address to the DataFrame
    addresses = []
    for index, row in df_cleaned.iterrows():
        lat, lon = row['lat'], row['lon']
        address = get_address_from_latlon(lat, lon)
        addresses.append(address if address else "Address not found")
    
    df_cleaned['address'] = addresses

    # Select and reorder the desired columns
    df_cleaned = df_cleaned[['MAC_ADDRESS', 'lat', 'lon', 'address', 'Hotspot', 'Zone', 'Parish']]

    # Save the enriched data to a new JSON file at a specific path
    OUTPUT_PATH = './datamesh/b_staging/datasets/porto_digital_wifi_hotspots.json'

    # Convert the DataFrame to a JSON string
    json_data = df_cleaned.to_json(orient='records')

    # Save the JSON data to the file
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(json_data)

    # Print a confirmation message with the path where the file is saved
    print(f"Enriched data saved to: {OUTPUT_PATH}")
