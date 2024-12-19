import os
import sys
from folium import Polygon
import requests
import json
from shapely import Point
from shapely.geometry import Polygon as ShapelyPolygon

# Enabling json utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import application.services.json_file_utils as jfs

# File paths
GEO_API_NEIGHBORHOODS_INHABITANTS = './datamesh/a_raw_data/datasets/geoapi.pt/geo_api_neighborhoods_inhabitants.json'
GEO_API_NEIGHBORHOODS_POLYGON_COORDINATES = './datamesh/a_raw_data/datasets/geoapi.pt/geo_api_neighborhoods_polygon.json'
PORTO_WIFI_DATAPOINTS = './datamesh/b_staging/datasets/porto_digital_wifi_hotspots.json'

# Function to check if a point is inside the neighborhood polygon
def is_point_in_polygon(lat, lon, polygon_coords):
    # Create a shapely polygon and point
    polygon = ShapelyPolygon(polygon_coords)
    point = Point(lon, lat)  # Shapely uses (longitude, latitude)
    return point.within(polygon)

wifi_data_points = jfs.load_json_files(PORTO_WIFI_DATAPOINTS)

# Sample first JSON (your initial data with neighborhoods and inhabitants)
neighborhoods_data = jfs.load_json_files(GEO_API_NEIGHBORHOODS_INHABITANTS)

# Sample second JSON (with geojson data and coordinates)
geojson_data =  jfs.load_json_files(GEO_API_NEIGHBORHOODS_POLYGON_COORDINATES)

# Step 1: Create a mapping of 'Freguesia' to coordinates
freguesia_to_coordinates = {
    feature['properties']['Freguesia']: feature['geometry']['coordinates'][0]  # Take the first set of coordinates if multiple polygons
    for feature in geojson_data['geojsons']['freguesias']
}

# Step 2: Enrich the first JSON (neighborhoods_data) with the coordinates and initialize the new field
for neighborhood in neighborhoods_data:
    neighborhood_name = neighborhood['neighborhood_name']
    if neighborhood_name in freguesia_to_coordinates:
        # Convert the coordinate pairs into dicts with lat and lon labels
        enriched_coordinates = [
            {"lat": coord[1], "lon": coord[0]}  # Reversing the order as Shapely uses (lon, lat)
            for coord in freguesia_to_coordinates[neighborhood_name]
        ]
        neighborhood['coordinates'] = enriched_coordinates
        neighborhood['number_of_wifi_hotspots'] = 0  # Initialize the field to 0

# Step 3: Count how many wifi data points are inside each neighborhood polygon
for point in wifi_data_points:
    lat = point['lat']
    lon = point['lon']
    
    # Check each neighborhood's polygon and increment count if the point is inside
    for neighborhood in neighborhoods_data:
        if 'coordinates' in neighborhood:
            if is_point_in_polygon(lat, lon, freguesia_to_coordinates[neighborhood['neighborhood_name']]):
                neighborhood['number_of_wifi_hotspots'] += 1

# Save the enriched data to a new JSON file (optional)
ENRICHED_GEO_API_NEIGHBORHOODS = './datamesh/c_features/datasets/porto_neighborhoods.json'
jfs.save_to_file(neighborhoods_data, ENRICHED_GEO_API_NEIGHBORHOODS)

print(f"Enriched data with number_of_wifi_hotspots saved to {ENRICHED_GEO_API_NEIGHBORHOODS}")
