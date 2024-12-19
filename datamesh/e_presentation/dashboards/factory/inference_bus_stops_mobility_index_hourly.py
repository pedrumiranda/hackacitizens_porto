import pandas as pd
import plotly.express as px

# Create the DataFrame from the provided input data
data_file = "./datamesh/c_features/datasets/mobility_regression_inference.csv"
df = pd.read_csv(data_file, encoding='utf-8')

# Sort the data by 'hourly_slice' to ensure correct slider order
df = df.sort_values('hourly_slice')

# Create the animated scatter map
fig = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    size="mobility_score",  # This sets the size of the markers based on mobility score
    color="mobility_score",  # This sets the color based on mobility score
    animation_frame="hourly_slice",  # This allows the animation of hourly slices
    title="Mobility Score per Stop by Hourly Slice",
    mapbox_style="carto-positron",  # This defines the map style
    color_continuous_scale="Viridis",  # Color scale for mobility score
    size_max=15,  # Max size of markers
    zoom=12,  # Zoom level for the map
    labels={
        "mobility_score": "Mobility Score",
        "hourly_slice": "Hourly Slice"
    }
)

# Save the plot as an HTML file
output_html_path = "./datamesh/e_presentation/dashboards/factory/html/mobility_score_animation.html"
fig.write_html(output_html_path)

# Show the plot
fig.show()
