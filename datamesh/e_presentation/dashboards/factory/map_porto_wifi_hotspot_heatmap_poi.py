import os
import sys
import folium
import pandas as pd
from folium.plugins import HeatMap
import json

# Sample data for neighborhoods with coordinates (only a part of it for this example)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import application.services.json_file_utils as jfs

# Dataset with latitude and longitude of wifi hotspots
wifi_hotspots = jfs.load_json_files('./datamesh/b_staging/datasets/porto_digital_wifi_hotspots.json')

# Convert Wi-Fi hotspot data to a DataFrame
wifi_df = pd.DataFrame(wifi_hotspots)

# Dataset with polygons for neighborhoods
neighborhoods_data = jfs.load_json_files('./datamesh/c_features/datasets/porto_neighborhoods.json')

stadia_tiles = "https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}.png?api_key=3efbf953-e729-4e4a-a46a-90a29827fa12"
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

    popup = folium.Popup(f"""{neighborhood["neighborhood_name"]}""",
                          max_width=700)

    folium.Polygon(
        locations=coordinates,
        color='grey',
        fill=True,
        fill_opacity=0.1,
        popup=popup
    ).add_to(m)

# Loop through the neighborhoods and add polygons to the map
for neighborhood in neighborhoods_data:
    add_neighborhood_polygon(neighborhood)

# Function to add a heatmap of data points to the map
def add_heatmap_to_map(df):
    heat_data = [[row["lat"], row["lon"]] for _, row in df.iterrows()]
    HeatMap(heat_data).add_to(m)

# Add the heatmap of Wi-Fi hotspots to the map
add_heatmap_to_map(wifi_df)

# Function to add Porto main institutions datapoints to map
def add_porto_main_institutions_datapoints_to_map(m):
    PORTO_CITY_MAIN_INSTITUTIONS = './datamesh/b_staging/datasets/porto_city_main_institutions.json'

    # Dataset with latitude and longitude (load the JSON data)
    data_points = jfs.load_json_files(PORTO_CITY_MAIN_INSTITUTIONS)

    # Create a dictionary to store FeatureGroups for each location type
    markers_by_type = {}

    # Loop through the dataset and add markers for each data point
    for data_point in data_points:
        lat = data_point["lat"]
        lon = data_point["long"]
        name = data_point["name"]
        type = data_point["type"]

        # Define icon images based on the type
        type_to_icon = {
            "primary school": "./datamesh/e_presentation/dashboards/factory/html/images/education.png",
            "school": "./datamesh/e_presentation/dashboards/factory/html/images/education.png",
            "university": "./datamesh/e_presentation/dashboards/factory/html/images/education.png",
            "hospital": "./datamesh/e_presentation/dashboards/factory/html/images/hospital.png",
            "park": "./datamesh/e_presentation/dashboards/factory/html/images/park.png",
            "community garden": "./datamesh/e_presentation/dashboards/factory/html/images/park.png",
            "shopping mall": "./datamesh/e_presentation/dashboards/factory/html/images/shopping.png",
            "tourist attraction": "./datamesh/e_presentation/dashboards/factory/html/images/camera.png",
            "public office": "./datamesh/e_presentation/dashboards/factory/html/images/office.png",
            "subway station": "./datamesh/e_presentation/dashboards/factory/html/images/metro.png",
            "train station": "./datamesh/e_presentation/dashboards/factory/html/images/metro.png"
        }

        if type == "train station" or type == "railway station":
            type = "railway station"

        icon_image = type_to_icon.get(type, "./datamesh/e_presentation/dashboards/factory/html/images/metro.png")

        # Create the custom icon using the selected image
        custom_icon = folium.CustomIcon(
            icon_image=icon_image,
            icon_size=(40, 40)  # Adjust size as needed
        )

        popup = folium.Popup(f"""{type}: {name}""",
                              max_width=700)

        # Create the marker
        marker = folium.Marker(
            location=[lat, lon],
            icon=custom_icon,
            popup=popup
        )

        # Add marker to the appropriate FeatureGroup
        if type not in markers_by_type:
            markers_by_type[type] = folium.FeatureGroup(name=type)
        markers_by_type[type].add_child(marker)

    # Add each FeatureGroup to the map
    for feature_group in markers_by_type.values():
        feature_group.add_to(m)

    # Add LayerControl to toggle the visibility of each FeatureGroup
    folium.LayerControl().add_to(m)

# Add Porto Main Institutions datapoints with layers
add_porto_main_institutions_datapoints_to_map(m)

# Define the specific folder and file name
subfolder = "html"
filename = "map_porto_wifi_heatmap_poi.html"

# Get the current script's directory
current_dir = os.path.dirname(__file__)
output_folder = os.path.join(current_dir, subfolder)

# Ensure the folder exists
os.makedirs(output_folder, exist_ok=True)

# Define the full file path
file_path = os.path.join(output_folder, filename)

# Save the map
m.save(file_path)

print("Map with Wi-Fi hotspot heatmap and filtered markers saved to map_porto_wifi_heatmap.html")