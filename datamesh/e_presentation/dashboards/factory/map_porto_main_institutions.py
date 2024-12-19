import os
import sys
import folium
import json

# Enabling simulation service path
# Enabling json utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import application.services.json_file_utils as jfs

def add_porto_main_institutions_datapoints(m):

    PORTO_CITY_MAIN_INSTITUTIONS = './datamesh/b_staging/datasets/porto_city_main_institutions.json'

    # Dataset with latitude and longitude (load the JSON data)
    data_points = jfs.load_json_files(PORTO_CITY_MAIN_INSTITUTIONS)

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
        name = data_point["name"]
        type = data_point["type"]
    #   point_id = data_point["id"]


        type = data_point["type"]

        # Set icon image based on the 'type' value
        if type == "primary school":
            icon_image = "./datamesh/e_presentation/dashboards/factory/html/images/education.png"
        if type == "school":
            icon_image = "./datamesh/e_presentation/dashboards/factory/html/images/education.png"
        elif type == "university":
            icon_image = "./datamesh/e_presentation/dashboards/factory/html/images/education.png"
        elif type == "hospital":
            icon_image = "./datamesh/e_presentation/dashboards/factory/html/images/hospital.png"
        elif type == "park":
            icon_image = "./datamesh/e_presentation/dashboards/factory/html/images/park.png"
        elif type == "community garden":
            icon_image = "./datamesh/e_presentation/dashboards/factory/html/images/park.png"
        elif type == "parks":
            icon_image = "./datamesh/e_presentation/dashboards/factory/html/images/park.png"
        elif type == "shopping mall":
            icon_image = "./datamesh/e_presentation/dashboards/factory/html/images/shopping.png"
        elif type == "tourist attraction":
            icon_image = "./datamesh/e_presentation/dashboards/factory/html/images/camera.png"
        elif type == "public office":
            icon_image = "./datamesh/e_presentation/dashboards/factory/html/images/office.png"
        elif type == "subway station":
            icon_image = "./datamesh/e_presentation/dashboards/factory/html/images/metro.png"
        elif type == "train station":
            icon_image = "./datamesh/e_presentation/dashboards/factory/html/images/metro.png"

        # Create the custom icon using the selected image
        custom_icon = folium.CustomIcon(
            icon_image=icon_image,  # Path to the selected image file
            icon_size=(40, 40)      # Adjust size as needed
        )

        # Add the marker with the custom icon
        folium.Marker(
            location=[data_point["lat"], data_point["long"]],
            icon=custom_icon,
            popup=name
        ).add_to(m)



# Define the specific folder and file name
subfolder = "html"
filename = "map_porto_city_main_institutions.html"

# Get the current script's directory
current_dir = os.path.dirname(__file__)
output_folder = os.path.join(current_dir, subfolder)

# Ensure the folder exists
os.makedirs(output_folder, exist_ok=True)

# Define the full file path
file_path = os.path.join(output_folder, filename)

# Save the map
m.save(file_path)

print("Map saved as porto_city_main_institutions.html. Open it in a web browser to view the map.")