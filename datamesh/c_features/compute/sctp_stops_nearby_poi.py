import csv
import json
from math import radians, sin, cos, sqrt, atan2

# File paths
# File paths
INSTITUTIONS_JSON = './datamesh/b_staging/datasets/porto_city_main_institutions.json'
STOPS_CSV = './datamesh/c_features/datasets/sctp_routes_spatio_temporal.csv'

# Save the updated JSON to a file
OUTPUT_JSON = './datamesh/c_features/datasets/stcp_stops_nearby_poi.json'

# Haversine formula to calculate distance between two coordinates
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# Load CSV and get distinct stops
def load_distinct_stops(csv_file):
    stops = {}
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            stop_id = row['stop_id']
            if stop_id not in stops:
                stops[stop_id] = {
                    'stop_id': stop_id,
                    'stop_name': row['stop_name'],
                    'lat': float(row['stop_lat']),
                    'lon': float(row['stop_lon']),
                    'neighborhood_name': row['neighborhood_name']
                }
    return list(stops.values())

# Generalized function to compute number of nearby entities of a specific type
def add_nearby_entity_fields(stops, institutions, radius=1.5):
    """
    Adds multiple fields for different types of entities to each stop.
    
    :param stops: List of distinct stops with latitude/longitude
    :param institutions: List of institutions with latitude/longitude and type
    :param radius: Radius in kilometers to consider an entity as "nearby"
    :return: Stops with the new fields added
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

    # Filter institutions by type
    institutions_by_type = {
        entity_type: [inst for inst in institutions if inst.get('type') == entity_type]
        for entity_type in entity_types
    }

    for stop in stops:
        stop_lat = stop['lat']
        stop_lon = stop['lon']

        # Initialize fields for each entity type
        for entity_type in entity_types:
            stop[f'number_of_nearby_{entity_type.replace(" ", "_")}s'] = 0
            stop[f'closest_{entity_type.replace(" ", "_")}_km'] = float('inf')

        # Calculate nearby entities and closest distances for each type
        for entity_type, filtered_institutions in institutions_by_type.items():
            count = 0
            min_distance = float('inf')
            
            for institution in filtered_institutions:
                inst_lat = institution.get('lat')
                inst_lon = institution.get('long')

                if inst_lat is None or inst_lon is None:
                    continue

                distance = haversine(stop_lat, stop_lon, inst_lat, inst_lon)
                min_distance = min(min_distance, distance)
                
                if distance <= radius:
                    count += 1

            # Update the count and closest distance fields
            stop[f'number_of_nearby_{entity_type.replace(" ", "_")}s'] = count
            stop[f'closest_{entity_type.replace(" ", "_")}_km'] = (
                min_distance if min_distance != float('inf') else None
            )

    return stops

# Load JSON data for institutions
def load_institutions(json_file):
    with open(json_file, mode='r', encoding='utf-8') as file:
        return json.load(file)

# Save output to JSON
def save_to_json(data, output_file):
    with open(output_file, mode='w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Main function
def main():
    # Load distinct stops
    stops = load_distinct_stops(STOPS_CSV)

    # Load institutions data
    institutions = load_institutions(INSTITUTIONS_JSON)

    # Add nearby entity counts
    updated_stops = add_nearby_entity_fields(stops, institutions)

    # Save updated stops to JSON
    save_to_json(updated_stops, OUTPUT_JSON)
    print(f"Updated JSON saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
