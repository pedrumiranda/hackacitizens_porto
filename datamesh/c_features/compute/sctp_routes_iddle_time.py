import pandas as pd

# Input and output file paths
SCTP_ROUTES_SPATIO_TEMPORAL_JSON = "./datamesh/c_features/datasets/sctp_routes_spatio_temporal.csv"
OUTPUT = "./datamesh/c_features/datasets/sctp_routes_idle_time.csv"

# Load the data from CSV
df = pd.read_csv(SCTP_ROUTES_SPATIO_TEMPORAL_JSON, encoding='utf-8')

# Ensure columns are of string type for comparison
df['route_id'] = df['route_id'].astype(str)
df['direction_id'] = df['direction_id'].astype(str)
df['stop_sequence'] = df['stop_sequence'].astype(str)

# Clean 'service_id' column by removing leading/trailing spaces
df['service_id'] = df['service_id'].str.strip()

# Convert 'arrival_time' to datetime, and coerce errors to NaT if invalid
df['arrival_time'] = pd.to_datetime(df['arrival_time'], format='%H:%M:%S', errors='coerce')

# Drop rows where 'arrival_time' is NaT (invalid or missing values)
df = df.dropna(subset=['arrival_time'])

# Filter by stop_sequence == '1' (since stop_sequence is a string)
df = df[df['stop_sequence'] == '1']

# Sort by route_id, direction_id, service_id, and arrival_time for correct time difference calculation
df = df.sort_values(by=['route_id', 'direction_id', 'service_id', 'arrival_time'])

# Step 1: Calculate the idle time as the difference in minutes between consecutive rows within each group
df['idle_time'] = df.groupby(['route_id', 'direction_id', 'service_id'])['arrival_time'].diff().dt.total_seconds() / 60

# Step 2: Drop rows where idle_time is NaN (the first row in each group will have NaN idle_time)
df = df.dropna(subset=['idle_time'])

# Ensure that all required columns are of the correct type
df['route_id'] = df['route_id'].astype(str)
df['direction_id'] = df['direction_id'].astype(str)
df['service_id'] = df['service_id'].astype(str)

# Print the number of records after calculating idle_time
print("Number of records after calculating idle_time:", df.shape)

# Step 3: Calculate the mean idle time for the selected group (route_id, direction_id, service_id)
agg_df = df.groupby(['route_id', 'direction_id', 'service_id']).agg(
    idle_time_average=('idle_time', 'mean')
).reset_index()

# Save the aggregated data with mean idle time to a new CSV
agg_df.to_csv(OUTPUT, index=False, encoding='utf-8')

# Optionally print out the first few rows of the aggregated data
print(agg_df.head())

# Let the user know where the file was saved
print(f"The aggregated CSV file with mean idle time has been saved as {OUTPUT}.")
