import pandas as pd
import plotly.express as px

# Load the data
data = "./datamesh/c_features/datasets/mobility_regression_inference.csv"
df = pd.read_csv(data, encoding='utf-8')

# Filter for only 20 routes (replace with specific route IDs or use the first 20)
selected_routes = df['stop_id'].unique()[:20]  # Select the first 20 unique stop_ids
df_filtered = df[df['stop_id'].isin(selected_routes)]

# Encode `hourly_slice` numerically for the Z-axis
df_filtered['hourly_slice_encoded'] = df_filtered['hourly_slice'].astype('category').cat.codes

# Create the 3D scatter plot
fig = px.scatter_3d(
    df_filtered,
    x="distinct_trip_count",
    y="mobility_score",
    z="hourly_slice_encoded",
    color="stop_id",  # Color by stop_id to highlight stops
    size="mobility_score",  # Size of markers based on mobility_score
    hover_data=["stop_id", "neighborhood_name", "hourly_slice"],  # Hover data for details
    title="3D Visualization of Mobility Score, Trip Count, and Hourly Slice (Filtered for 20 Routes)",
    labels={"hourly_slice_encoded": "Hourly Slice (Encoded)"},  # Label for Z-axis
)

# Update the layout for better visualization
fig.update_layout(
    scene=dict(
        xaxis_title="Distinct Trip Count",
        yaxis_title="Mobility Score",
        zaxis_title="Hourly Slice",
    ),
    legend_title="Stop ID",
)

# Export the plot to an HTML file
output_file = "3d_mobility_visualization_filtered.html"
fig.write_html(output_file)

print(f"3D plot exported to {output_file}")
