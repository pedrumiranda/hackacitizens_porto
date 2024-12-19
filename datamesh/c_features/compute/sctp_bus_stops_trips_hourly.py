import pandas as pd
import json
from datetime import datetime

OUTPUT_CSV = './datamesh/c_features/datasets/sctp_bus_stops_trips_hourly.csv'

# File paths
SCTP_STAGING_SPATIO_TEMPORAL = "./datamesh/b_staging/datasets/stcp_routes_spatio_temporal.csv"

# Load CSV data
csv_data = pd.read_csv(SCTP_STAGING_SPATIO_TEMPORAL)

# Function to calculate hourly slice
def calculate_hourly_slice(arrival_time):
    try:
        time_obj = datetime.strptime(arrival_time, '%H:%M:%S')
        start = time_obj.replace(minute=0, second=0)
        end = time_obj.replace(minute=59, second=59)
        return f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
    except ValueError:
        return None  # Handle invalid time formats gracefully

# Add hourly slice column
csv_data['hourly_slice'] = csv_data['arrival_time'].apply(calculate_hourly_slice)

# Filter out rows with invalid hourly slices
csv_data = csv_data[csv_data['hourly_slice'].notna()]

# Group by stop_id, service_id, hourly_slice and count distinct trip_ids
aggregated_data = (
    csv_data
    .groupby(['stop_id', 'service_id', 'hourly_slice', 'stop_lat', 'stop_lon', 'stop_name'])
    .agg(distinct_trip_count=('trip_id', 'nunique'))
    .reset_index()
)

# Save the result to a CSV file
aggregated_data.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')

print(f"Aggregated CSV has been saved to {OUTPUT_CSV}")
