import pandas as pd

### REDUCE DIMENSIONALITY TO RELY ONLY ON SPATIO DIMENSION REMOVING THE TIME DIMENSION ####


# Input CSV file
SCTP_ROUTES_SPATIO_TEMPORAL_JSON = "./datamesh/c_features/datasets/sctp_routes_spatio_temporal.csv"

# Output CSV file
OUTPUT_CSV = "./datamesh/c_features/datasets/sctp_routes_spatio.csv"

# Load the CSV data into a DataFrame
df = pd.read_csv(SCTP_ROUTES_SPATIO_TEMPORAL_JSON, encoding='utf-8')

# Drop the specified columns: service_id, trip_id, arrival_time, departure_time
df_reduced = df.drop(columns=['service_id', 'trip_id', 'arrival_time', 'departure_time'])

# Select only distinct rows based on the remaining columns
df_distinct = df_reduced.drop_duplicates()

# Save the reduced DataFrame to a new CSV file
df_distinct.to_csv(OUTPUT_CSV, index=False, encoding='utf-8')

print(f"Reduced CSV with distinct data has been saved to {OUTPUT_CSV}")
