import json
from math import radians, sin, cos, sqrt, atan2
import os
import sys

# Enabling json utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
import application.services.json_file_utils as jfs

# File paths
PORTO_MAIN_POINTS_OF_INTEREST = './datamesh/b_staging/datasets/porto_city_main_institutions.json'
PORTO_WIFI_DATAPOINTS = './datamesh/b_staging/datasets/porto_digital_wifi_hotspots.json'

# Load JSON data
porto_institutions_json = jfs.load_json_files(PORTO_MAIN_POINTS_OF_INTEREST)
hotspots_json = jfs.load_json_files(PORTO_WIFI_DATAPOINTS)

# Haversine formula to calculate distance between two coordinates
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def add_nearby_entity_fields(entities, locations, radius=1):
    """
    Adds multiple fields for different types of entities to each location.
    
    :param entities: List of entities with latitude/longitude and type
    :param locations: List of locations to check for nearby entities
    :param radius: Radius in kilometers to consider an entity as "nearby"
    :return: Locations with the new fields added
    """
    entity_types = [
        'school',
        'hospital',
        'university',
        'public office',
        'tourist attraction',
        'train station',
        'subway station',
    ]

    # Filter entities by type
    entities_by_type = {
        entity_type: [entity for entity in entities if entity.get('type') == entity_type]
        for entity_type in entity_types
    }

    for location in locations:
        loc_lat = location.get('lat')
        loc_lon = location.get('lon')

        if loc_lat is None or loc_lon is None:
            continue

        # Initialize fields for each entity type
        for entity_type in entity_types:
            location[f'number_of_nearby_{entity_type.replace(" ", "_")}s'] = 0
            location[f'closest_{entity_type.replace(" ", "_")}_km'] = float('inf')

        # Calculate nearby entities and closest distances for each type
        for entity_type, filtered_entities in entities_by_type.items():
            count = 0
            min_distance = float('inf')
            
            for entity in filtered_entities:
                entity_lat = entity.get('lat')
                entity_lon = entity.get('long')

                if entity_lat is None or entity_lon is None:
                    continue

                distance = haversine(loc_lat, loc_lon, entity_lat, entity_lon)
                min_distance = min(min_distance, distance)
                
                if distance <= radius:
                    count += 1

            # Update the count and closest distance fields
            location[f'number_of_nearby_{entity_type.replace(" ", "_")}s'] = count
            location[f'closest_{entity_type.replace(" ", "_")}_km'] = (
                min_distance if min_distance != float('inf') else None
            )

    return locations

# Add the new fields to the locations JSON
updated_locations = add_nearby_entity_fields(porto_institutions_json, hotspots_json)

# Save the updated JSON to a file
output_file_path = './datamesh/c_features/datasets/porto_wifi_hotspots_nearby_poi.json'

with open(output_file_path, 'w', encoding='utf-8') as output_file:
    json.dump(updated_locations, output_file, ensure_ascii=False, indent=4)

# Print confirmation
print(f"Updated JSON with nearby entity counts saved to {output_file_path}")
