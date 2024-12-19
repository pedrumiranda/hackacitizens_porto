import pandas as pd
import plotly.express as px

# Load the data
data_file = "./datamesh/c_features/datasets/porto_wifi_access_per_hotspot_hourly.csv"
df = pd.read_csv(data_file)

# Sort hour_slice for correct order in the slider
hour_order = [
    "00:00–00:59", "01:00–01:59", "02:00–02:59", "03:00–03:59",
    "04:00–04:59", "05:00–05:59", "06:00–06:59", "07:00–07:59",
    "08:00–08:59", "09:00–09:59", "10:00–10:59", "11:00–11:59",
    "12:00–12:59", "13:00–13:59", "14:00–14:59", "15:00–15:59",
    "16:00–16:59", "17:00–17:59", "18:00–18:59", "19:00–19:59",
    "20:00–20:59", "21:00–21:59", "22:00–22:59", "23:00–23:59"
]
df['hour_slice'] = pd.Categorical(df['hour_slice'], categories=hour_order, ordered=True)

# Sort the data by hour_slice to ensure correct slider order
df = df.sort_values('hour_slice')

# Create a heatmap animation
fig = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    size="number_of_sessions_per_hour",
    color="number_of_sessions_per_hour",
    animation_frame="hour_slice",
    title="Network Activity Across Hotspots by Hour",
    mapbox_style="carto-positron",
    color_continuous_scale="Viridis",
    size_max=15,
    zoom=12,
    labels={
        "number_of_sessions_per_hour": "Session Intensity",
        "hour_slice": "Hourly Slice"
    }
)

fig.show()
