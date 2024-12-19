import os
import sys
import plotly.graph_objects as go
import numpy as np

# Sample data for neighborhoods with coordinates (only a part of it for this example)
# Enabling simulation service path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import application.services.json_file_utils as jfs


# Dataset with polygons for neighborhoods
neighborhoods_data = jfs.load_json_files('./datamesh/c_features/datasets/porto_neighborhoods.json')
# Extract the relevant data for plotting
neighborhood_names = [entry["neighborhood_name"] for entry in neighborhoods_data]
inhabitants = [entry["inhabitants"] for entry in neighborhoods_data]
wifi_hotspots = [entry["number_of_wifi_hotspots"] for entry in neighborhoods_data]

# Create a color scale based on the number of wifi hotspots
colors = np.array(wifi_hotspots)  # Color by number of wifi hotspots

# Create the plot using plotly
fig = go.Figure(data=go.Scatter(
    x=inhabitants,
    y=wifi_hotspots,
    mode='markers+text',
    text=neighborhood_names,
    textposition='top right',
    marker=dict(
        size=[entry["inhabitants"] / 1000 for entry in neighborhoods_data],  # Marker size based on number of inhabitants
        color=colors,  # Color by wifi hotspots
        colorscale='Viridis',  # Color scale to represent wifi hotspots
        colorbar=dict(title='Number of Wifi Hotspots'),
        opacity=0.7,
        line=dict(width=1, color='DarkSlateGrey')
    )
))

# Add titles and labels
fig.update_layout(
    title='Distribution of Wifi hotspots per neighborhood',
    xaxis_title='Number of Inhabitants',
    yaxis_title='Number of Wifi Hotspots',
    template='plotly',
    showlegend=False,
    xaxis=dict(type='log'),  # Logarithmic scale for x-axis
    yaxis=dict(type='log'),  # Logarithmic scale for y-axis
)


# Define the specific folder and file name
subfolder = "html"
filename = "scatter_porto_wifi_hotspots.html"

# Get the current script's directory
current_dir = os.path.dirname(__file__)
output_folder = os.path.join(current_dir, subfolder)

# Ensure the folder exists
os.makedirs(output_folder, exist_ok=True)

# Define the full file path
file_path = os.path.join(output_folder, filename)


# Save the plot as an HTML filefile_path
fig.write_html(file_path)

# Show the plot
fig.show()
