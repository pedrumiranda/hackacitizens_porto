import joblib
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

TRIP_COUNT = "./datamesh/c_features/datasets/sctp_bus_stops_trips_hourly.csv"
STCP_STOPS = "./datamesh/c_features/datasets/stcp_stops_nearby_poi.json"
MODEL_PATH = "./datamesh/d_ml_inference/models/mobility_regressor.joblib"
OUTPUT_PATH = "./datamesh/c_features/datasets/mobility_regression_inference.csv"

# load data
trip_count = pd.read_csv(TRIP_COUNT)
stcp_stops = pd.read_json(STCP_STOPS)

# merge trip count with stcp stop geospatial data
merged = pd.merge(trip_count, stcp_stops, left_on=['stop_lat', 'stop_lon'], right_on=['lat', 'lon'], how='left')

# create inference dataset
dates = pd.date_range(start='2024-11-01', end='2024-11-30', freq='D')
df = pd.DataFrame({'date': dates})
df['day_of_month'] = df['date'].dt.day
df['day_of_week'] = df['date'].dt.dayofweek
df["day_of_week_category"] = df["day_of_week"].apply(lambda x: 'SAB' if x == 5 else 'DOM' if x == 6 else 'UTEIS')
final_dataset = pd.merge(df, merged, left_on="day_of_week_category", right_on="service_id", how='inner')

final_dataset_cp = final_dataset.copy()  # for later use

# match inference schema with training schema

# feature engineering
final_dataset["total_pois"] = (
    final_dataset["number_of_nearby_schools"] +
    final_dataset["number_of_nearby_hospitals"] +
    final_dataset["number_of_nearby_universitys"] +
    final_dataset["number_of_nearby_public_offices"] +
    final_dataset["number_of_nearby_tourist_attractions"] +
    final_dataset["number_of_nearby_train_stations"] +
    final_dataset["number_of_nearby_subway_stations"]
)

# drop columns
final_dataset.drop(
    columns=[
        "date",
        "day_of_week_category",
        "stop_id_x",
        "stop_id_y",
        "stop_name_x",
        "stop_name_y",
        "service_id",
        "stop_lat",
        "stop_lon",
        "neighborhood_name",
        "distinct_trip_count"
    ],
    inplace=True
)

# rename columns
final_dataset.rename(columns={"hourly_slice": "hour_slice"}, inplace=True)
final_dataset["hour_slice"] = final_dataset["hour_slice"].apply(lambda x: x.replace("-", "–"))

# inference
model = joblib.load(MODEL_PATH)
y_pred = model.predict(final_dataset)
final_dataset_cp["mobility_score"] = y_pred

# normalize mobility score between 0 and 100 
final_dataset_cp["mobility_score"] = (final_dataset_cp["mobility_score"] - final_dataset_cp["mobility_score"].min()) / (final_dataset_cp["mobility_score"].max() - final_dataset_cp["mobility_score"].min()) * 100
final_dataset_cp["mobility_score"] = final_dataset_cp["mobility_score"].round()
final_dataset_cp["mobility_score"] = final_dataset_cp["mobility_score"].astype(int)

# transform and save
final_transformed = final_dataset_cp[["stop_id_x", "neighborhood_name", "lat", "lon", "date", "day_of_week_category", "hourly_slice", "mobility_score", "distinct_trip_count"]]
final_transformed = final_transformed[final_transformed["stop_id_x"] != "."]
final_transformed.rename(columns={"stop_id_x": "stop_id"}, inplace=True)
final_transformed.to_csv(OUTPUT_PATH, index=False)
