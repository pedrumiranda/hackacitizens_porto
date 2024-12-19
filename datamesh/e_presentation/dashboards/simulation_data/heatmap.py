import os
import sys
import folium
from folium.plugins import HeatMap
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import application.services.simulation_stcp_service as ps

# JSON input data
data = ps.load_json_files(ps.PORTO_FREE_WIFI_SIMULATION_DATASET_PATH)

# Extract latitude and longitude for heatmap
heat_data = [[entry["lat"], entry["long"]] for entry in data]

# Create a folium map centered around the mean of the latitudes and longitudes
center_lat = sum(entry["lat"] for entry in data) / len(data)
center_long = sum(entry["long"] for entry in data) / len(data)
m = folium.Map(location=[center_lat, center_long], zoom_start=13)

# Add heatmap layer
HeatMap(heat_data).add_to(m)


# Define the specific folder and file name
subfolder = "html"
filename = "heatmap.html"

# Get the current script's directory
current_dir = os.path.dirname(__file__)
output_folder = os.path.join(current_dir, subfolder)

# Ensure the folder exists
os.makedirs(output_folder, exist_ok=True)

# Define the full file path
file_path = os.path.join(output_folder, filename)

# Save the map
m.save(file_path)


print("Heatmap saved as heatmap.html. Open it in a web browser to view.")