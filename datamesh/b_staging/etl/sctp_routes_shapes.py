import csv
import os
import sys
import pandas as pd
import json

# Enabling json utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import application.services.json_file_utils as jfs

STCP_ROUTES = './datamesh/a_raw_data/datasets/porto_digital/stcp_routes/gtfs_stcp/routes.csv'
STCP_TRIPS = './datamesh/a_raw_data/datasets/porto_digital/stcp_routes/gtfs_stcp/trips.csv'
STCP_SHAPE = './datamesh/a_raw_data/datasets/porto_digital/stcp_routes/gtfs_stcp/shapes.csv'

# Function to read the CSV data and organize by shape_id
def read_shape_csv(csv_file):
    shape_data = {}
    # Open and read the CSV file
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            shape_id = row['shape_id']
            # If shape_id is not in the dictionary, initialize an empty list
            if shape_id not in shape_data:
                shape_data[shape_id] = []
            # Append the coordinates to the list for this shape_id
            shape_data[shape_id].append({
                "shape_pt_lat": float(row['shape_pt_lat']),
                "shape_pt_lon": float(row['shape_pt_lon']),
                "shape_pt_sequence": int(row['shape_pt_sequence'])
            })
    return shape_data

# Read CSV data into a dictionary
shape_data = read_shape_csv(STCP_SHAPE)

# Step 1: Read the CSV data into pandas DataFrames
routes_df = pd.read_csv(STCP_ROUTES, encoding='utf-8')
trips_df = pd.read_csv(STCP_TRIPS, encoding='utf-8')

# Step 2: Keep only the necessary columns for the routes DataFrame
routes_df = routes_df[['route_id', 'route_long_name']]

# Step 3: Keep only the necessary columns for the trips DataFrame
trips_df = trips_df[['route_id', 'trip_id', 'service_id', 'shape_id', 'trip_headsign']]

# Step 4: Merge the routes DataFrame with the trips DataFrame based on route_id
merged_df = pd.merge(trips_df, routes_df, on='route_id', how='left')

# Step 5: Create a list for each route with its respective trips
routes_list = []

for route_id, group in merged_df.groupby(['route_id', 'route_long_name']):
    # Create the route dictionary
    route_info = {
        'route_id': route_id[0],
        'route_long_name': route_id[1],
        'trips': group[['trip_id', 'service_id', 'shape_id', 'trip_headsign']].to_dict(orient='records')
    }
    routes_list.append(route_info)

# Function to remove 'trip_id', deduplicate trips, and append coordinates from CSV
def remove_trip_id_and_extract_shape_ids(data, shape_data):
    for route in data:
        # Create a set to hold unique shape_ids
        unique_shape_ids = set()

        # Remove 'trip_id' and create a set of unique trips
        seen_trips = set()
        unique_trips = []

        for trip in route['trips']:
            # Add the shape_id to the set for later use
            unique_shape_ids.add(trip['shape_id'])

            # Create a trip identifier without 'trip_id' (based on other fields)
            trip_data = {key: trip[key] for key in trip if key != 'trip_id'}
            
            # Convert trip data to a tuple for easy comparison and use in a set (since sets don't allow duplicates)
            trip_tuple = tuple(trip_data.items())
            
            if trip_tuple not in seen_trips:
                seen_trips.add(trip_tuple)
                unique_trips.append(trip_data)

        # Replace the trips list with the deduplicated list
        route['trips'] = unique_trips

        # Store the unique shape_ids at the same level as route_id
        route['unique_shape_ids'] = []

        # Add the coordinates from the CSV to each unique_shape_id
        for unique_shape_id in unique_shape_ids:
            shape_info = {"shape_id": unique_shape_id}

            # Determine trip direction based on shape_id
            if '1_1_shp' in unique_shape_id:
                shape_info['trip_direction'] = 'INBOUND_CITY_CENTER'
            elif '0_1_shp' in unique_shape_id:
                shape_info['trip_direction'] = 'OUTBOUND_CITY_CENTER'
            else:
                shape_info['trip_direction'] = 'UNKNOWN'

            if unique_shape_id in shape_data:
                shape_info['coordinates'] = shape_data[unique_shape_id]
                route['unique_shape_ids'].append(shape_info)
        
        del route['trips']  # Remove trips section as requested

    return data

# Apply the function to the data
cleaned_data = remove_trip_id_and_extract_shape_ids(routes_list, shape_data)

OUTPUT_PATH = './datamesh/b_staging/datasets/stcp_routes_shapes.json'

# Loop through each route_data and modify the unique_shape_ids
for route in cleaned_data:
    for shape in route["unique_shape_ids"]:
        # Sort coordinates by shape_pt_sequence
        sorted_coordinates = sorted(shape["coordinates"], key=lambda x: x["shape_pt_sequence"])

        # Extract the first and last coordinates
        first_coord = sorted_coordinates[0]  # First coordinate (smallest sequence)
        last_coord = sorted_coordinates[-1]  # Last coordinate (largest sequence)

        # Add first_coordinates and last_coordinates fields
        shape["first_coordinates"] = {
            "shape_pt_lat": first_coord["shape_pt_lat"],
            "shape_pt_lon": first_coord["shape_pt_lon"]
        }
        shape["last_coordinates"] = {
            "shape_pt_lat": last_coord["shape_pt_lat"],
            "shape_pt_lon": last_coord["shape_pt_lon"]
        }

output_json = json.dumps(cleaned_data, indent=4, ensure_ascii=False)

# Print or save the JSON output
print(output_json)

# Optionally, save the output to a file
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write(output_json)
