import os
import sys
import pandas as pd

# Input CSV file
PORTO_NETWORK_ACTIVITY = "./datamesh/b_staging/datasets/porto_wifi_hotspots_network_activity.csv"

# Load the CSV data into a DataFrame
csv_df = pd.read_csv(PORTO_NETWORK_ACTIVITY, encoding='utf-8')

# Parse the acctstarttime to extract date and hour_slice
csv_df['acctstarttime'] = pd.to_datetime(csv_df['acctstarttime'])
csv_df['date'] = csv_df['acctstarttime'].dt.date

# Generate the hour_slice in HH:00–HH:59 format
csv_df['hour_slice'] = csv_df['acctstarttime'].dt.hour.apply(
    lambda h: f"{h:02d}:00–{h:02d}:59"
)

# Group by calledstationid, date, and hour_slice and count the number of sessions in each group
aggregated_df = csv_df.groupby(['calledstationid', 'date', 'hour_slice']).size().reset_index(name='number_of_sessions_per_hour')

# Save the final DataFrame to a CSV file
aggregated_df.to_csv('./datamesh/c_features/datasets/porto_wifi_access_per_hotspot_hourly.csv', index=False, encoding='utf-8')

# Show a preview of the result
print(aggregated_df.head())
