import os
import sys
import folium
import pandas as pd

# Enabling json utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import application.services.json_file_utils as jfs

STCP_STAGING = './datamesh/b_staging/datasets/stcp_routes.json'

# Load the data from JSON
route_data = jfs.load_json_files(STCP_STAGING)

# Convert the route_data to a pandas DataFrame
routes_df = pd.json_normalize(route_data, 'unique_shape_ids', ['route_id', 'route_long_name'], errors='ignore')

routes_df = routes_df[routes_df["route_id"] == "200"]

# Check if any route matches the filter
if routes_df.empty:
    print("No routes found")

# Create a folium map centered at the average coordinates (you can adjust the map center if needed)
map_center = [41.140801, -8.615485]  # Starting coordinates
stadia_tiles = "https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}.png?api_key=3efbf953-e729-4e4a-a46a-90a29827fa12"
# Add attribution for Stadia Maps
stadia_attr = "Map tiles by Stadia Maps, © OpenMapTiles © OpenStreetMap contributors"
mymap = folium.Map(location=map_center, zoom_start=15, tiles=stadia_tiles, attr=stadia_attr)

# List of colors to assign to each route (you can extend this list)
colors = ['blue', 'green', 'red', 'purple', 'orange', 'darkblue', 'darkgreen', 'cadetblue']

# Create a dictionary to store feature groups for each route_id
route_feature_groups = {}

# Add markers and polyline for each shape in the filtered routes
for i, (_, route) in enumerate(routes_df.iterrows()):
    shape_id = route['shape_id']
    coordinates = route['coordinates']
    
    # Assign a color to each route based on the index
    route_color = colors[i % len(colors)]
    
    # Create a list of coordinates for plotting
    shape_coords = [(coord['shape_pt_lat'], coord['shape_pt_lon']) for coord in coordinates]
    
    # Create a FeatureGroup for each route_id if it doesn't exist
    route_id = route['route_id']
    if route_id not in route_feature_groups:
        route_feature_groups[route_id] = folium.FeatureGroup(name=route['route_long_name'])
    
    # Add the polyline to the feature group
    folium.PolyLine(shape_coords, color=route_color, weight=2.5, opacity=1, tooltip=route["route_long_name"]).add_to(route_feature_groups[route_id])
    
    # Add a marker at the beginning of the route (first coordinate)
    first_coord = shape_coords[0]
    popup_start = folium.Popup(f"""Start route {route['route_id']} | {route['route_long_name']}""", max_width=500)
    folium.Marker(location=first_coord, popup=popup_start, icon=folium.Icon(color=route_color, icon='info-sign')).add_to(route_feature_groups[route_id])
    
    # Add a marker at the end of the route (last coordinate)
    last_coord = shape_coords[-1]
    popup_end = folium.Popup(f"""End route {route['route_id']} | {route['route_long_name']}""", max_width=500)
    folium.Marker(location=last_coord, popup=popup_end, icon=folium.Icon(color=route_color, icon='info-sign')).add_to(route_feature_groups[route_id])

# Add all feature groups to the map
for feature_group in route_feature_groups.values():
    feature_group.add_to(mymap)

# Add LayerControl to allow users to toggle between different routes
layer_control = folium.LayerControl().add_to(mymap)




# Save the map to an HTML file
mymap.save('highlighted_route_map_with_select_all.html')
