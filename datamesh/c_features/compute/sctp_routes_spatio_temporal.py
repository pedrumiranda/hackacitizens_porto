import pandas as pd
import json
from shapely.geometry import Point, Polygon

### ADDING NEW FEATURES ####
# trip_direction (INBOUND_CITY_CENTER, OUTBOUND_CITY_CENTER)
# neighborhood for each stop datapoint
##### neighborhood feature finds if stop coordinate falls inside each Porto neighborhood boundarie

OUTPUT_CSV = './datamesh/c_features/datasets/sctp_routes_spatio_temporal.csv'


# File paths
SCTP_STAGING_SPATIO_TEMPORAL = "./datamesh/b_staging/datasets/stcp_routes_spatio_temporal.csv"
PORTO_NEIGHBORHOODS = "./datamesh/c_features/datasets/porto_neighborhoods.json"


# Load CSV data
csv_data = pd.read_csv(SCTP_STAGING_SPATIO_TEMPORAL)


# Add the trip_direction column based on trip_id
def determine_trip_direction(trip_id):
    if '_1_' in trip_id:
        return 'INBOUND_CITY_CENTER'
    elif '_0_' in trip_id:
        return 'OUTBOUND_CITY_CENTER'
    else:
        return 'Unknown'  # Default value in case the trip_id doesn't match any condition

csv_data['trip_direction'] = csv_data['trip_id'].apply(determine_trip_direction)


# Load JSON data
with open(PORTO_NEIGHBORHOODS, 'r', encoding='utf-8') as f:
    neighborhoods = json.load(f)

# Create a list of neighborhood polygons
neighborhood_polygons = []
for neighborhood in neighborhoods:
    name = neighborhood['neighborhood_name']
    coordinates = [(coord['lat'], coord['lon']) for coord in neighborhood['coordinates']]
    polygon = Polygon(coordinates)
    neighborhood_polygons.append({'name': name, 'polygon': polygon})

# Function to find the neighborhood for a given latitude and longitude
def get_neighborhood(lat, lon):
    point = Point(lat, lon)
    for neighborhood in neighborhood_polygons:
        if neighborhood['polygon'].contains(point):
            return neighborhood['name']
    return 'OUTSIDE_PORTO_MUNICIPALITY_BOUNDARIES'  # Return None if no neighborhood is found

# Apply the function to each row in the CSV
csv_data['neighborhood_name'] = csv_data.apply(
    lambda row: get_neighborhood(row['stop_lat'], row['stop_lon']),
    axis=1
)

# Save the updated DataFrame to a new CSV
csv_data.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')

print(f"CSV with 'neighborhood_name' field has been saved to {OUTPUT_CSV}")
