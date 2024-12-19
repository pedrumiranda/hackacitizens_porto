import os
import sys
import folium
import json

# Enabling simulation service path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import application.services.simulation_stcp_service as ps

# Dataset with latitude and longitude (load the JSON data)
data_points = ps.load_json_files(ps.PORTO_FREE_WIFI_SIMULATION_DATASET_PATH)

# Initialize the map (starting at a generic location or the first data point)
# For now, we can start with the location of the first data point or a default one
if data_points:
    first_data_point = data_points[0]
    m = folium.Map(location=[first_data_point["lat"], first_data_point["long"]], zoom_start=14)
else:
    m = folium.Map(location=[41.12738760244269, -8.658549201555658], zoom_start=14)  # Default fallback location

# Loop through the dataset and add markers and circles for each data point
for data_point in data_points:
    lat = data_point["lat"]
    lon = data_point["long"]
    point_id = data_point["id"]

    # Add a marker at the data point
    folium.Marker(
        location=[lat, lon],
        popup=f"ID: {point_id}",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

    # Optionally, add a circle to represent the data point with some radius
    folium.Circle(
        location=[lat, lon],
        radius=100,  # radius in meters
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.5
    ).add_to(m)

# Define the specific folder and file name
subfolder = "html"
filename = "data_points.html"

# Get the current script's directory
current_dir = os.path.dirname(__file__)
output_folder = os.path.join(current_dir, subfolder)

# Ensure the folder exists
os.makedirs(output_folder, exist_ok=True)

# Define the full file path
file_path = os.path.join(output_folder, filename)

# Save the map
m.save(file_path)

print("Map saved as data_points.html. Open it in a web browser to view the map.")