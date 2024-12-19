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
STCP_STOPS = './datamesh/a_raw_data/datasets/porto_digital/stcp_routes/gtfs_stcp/stops.csv'
STCP_STOP_TIMES = './datamesh/a_raw_data/datasets/porto_digital/stcp_routes/gtfs_stcp/stop_times.csv'
STCP_SHAPE = './datamesh/a_raw_data/datasets/porto_digital/stcp_routes/gtfs_stcp/shapes.csv'

# Load the first CSV
trips_df = pd.read_csv(STCP_TRIPS)

# Load the second CSV
stop_times_df = pd.read_csv(STCP_STOP_TIMES)

# Load the third CSV
stops_df = pd.read_csv(STCP_STOPS)


# Perform the join using trip_id as the key
denormalized_df = pd.merge(trips_df, stop_times_df, on='trip_id', how='inner')

# Step 2: Join the resulting table with stops on stop_id
final_denormalized_df = pd.merge(denormalized_df, stops_df, on='stop_id', how='inner')

OUTPUT_CSV = './datamesh/b_staging/datasets/stcp_routes_spatio_temporal.csv'
# Save the denormalized table to a new CSV
final_denormalized_df.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')

print(f"Denormalized table created successfully and saved as {OUTPUT_CSV}")
