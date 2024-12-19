import pandas as pd
import plotly.express as px

# Load the data from the CSV file (replace with your file path)
data_file = "./datamesh/c_features/datasets/sctp_bus_stops_trips_hourly.csv"
df = pd.read_csv(data_file,encoding='utf-8')

# Ensure the 'hourly_slice' is ordered correctly for the animation slider


# Sort the data by 'hourly_slice' to ensure correct slider order
df = df.sort_values('hourly_slice')

# Create the animated scatter map
fig = px.scatter_mapbox(
    df,
    lat="stop_lat",
    lon="stop_lon",
    size="distinct_trip_count",  # This sets the size of the markers
    color="distinct_trip_count",  # This sets the color based on trip count
    animation_frame="hourly_slice",  # This allows the animation of hourly slices
    title="Trip Counts per Stop by Hourly Slice",
    mapbox_style="carto-positron",  # This defines the map style
    color_continuous_scale="Viridis",  # Color scale for trip count
    size_max=15,  # Max size of markers
    zoom=12,  # Zoom level for the map
    labels={
        "distinct_trip_count": "Distinct Trip Count",
        "hourly_slice": "Hourly Slice"
    }
)

# Show the plot
fig.show()
