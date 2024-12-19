import os
import sys
import folium
import pandas as pd

# Sample data for neighborhoods with coordinates (only a part of it for this example)
# Enabling simulation service path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import application.services.json_file_utils as jfs

# Dataset with latitude and longitude of wifi hotspots
SCTP_SPATIO_FEATURE = './datamesh/c_features/datasets/sctp_routes_spatio.csv'

# Load the CSV data into a DataFrame
bus_stops_df = pd.read_csv(SCTP_SPATIO_FEATURE, encoding='utf-8')

# Dataset with polygons for neighborhoods
neighborhoods_data = jfs.load_json_files('./datamesh/c_features/datasets/porto_neighborhoods.json')

stadia_tiles = "https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}.png?api_key=3efbf953-e729-4e4a-a46a-90a29827fa12"
# Add attribution for Stadia Maps
stadia_attr = "Map tiles by Stadia Maps, © OpenMapTiles © OpenStreetMap contributors"

# Initialize the map centered around Porto
map_center = [41.15276689657129, -8.595550812543978]  # Rough center of Porto
m = folium.Map(
    attr=stadia_attr,
    control_scale=True,
    tiles=stadia_tiles,
    location=map_center,
    zoom_start=13,
    width="100%",
    height="100%"  # Full size for embedding
)

# Function to add polygons to the map
def add_neighborhood_polygon(neighborhood):
    coordinates = [(coord["lat"], coord["lon"]) for coord in neighborhood["coordinates"]]

    popup = folium.Popup(f"""{neighborhood["neighborhood_name"]} | Wifi Hotspots: {neighborhood["number_of_wifi_hotspots"]}""",
                          max_width=500)

    folium.Polygon(
        locations=coordinates,
        color='grey', # The polygon border color
        fill=True,
        fill_opacity=0.1,
        popup=popup
    ).add_to(m)

# Loop through the neighborhoods and add polygons to the map
for neighborhood in neighborhoods_data:
    add_neighborhood_polygon(neighborhood)

# Function to add data points to the map, now with unique stop_ids
def add_data_points_to_map(df):
    """
    Adds data points from a pandas DataFrame to a folium map.
    
    :param df: A pandas DataFrame containing bus stop data (must include 'stop_lat' and 'stop_lon' columns)
    """
    for _, row in df.iterrows():
        lat = row["stop_lat"]
        lon = row["stop_lon"]

        
        # Add a marker with a custom image icon
        custom_icon = folium.CustomIcon(
            icon_image="./datamesh/e_presentation/dashboards/factory/html/images/bus_stop.png",  # Path to your image file
            icon_size=(30, 30)  # Adjust size as needed
        )

        
        # Add a marker to the map (without custom icon for now)
        folium.Marker(
            location=[lat, lon],
            icon=custom_icon
            
        ).add_to(m)

# Filter the DataFrame to include only unique stop_id values
bus_stops_df_unique = bus_stops_df.drop_duplicates(subset=['stop_id'])

# Add the filtered data points to the map
add_data_points_to_map(bus_stops_df_unique)

# Define the specific folder and file name
subfolder = "html"
filename = "map_porto_bus_stops_datapoints.html"

# Get the current script's directory
current_dir = os.path.dirname(__file__)
output_folder = os.path.join(current_dir, subfolder)

# Ensure the folder exists
os.makedirs(output_folder, exist_ok=True)

# Define the full file path
file_path = os.path.join(output_folder, filename)

# Save the map
m.save(file_path)

print("Map with neighborhood polygons saved to map_porto_bus_stops.html")
