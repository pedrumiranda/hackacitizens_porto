import pandas as pd
import plotly.express as px

# Dataset with idle time information
SCTP_IDDLE_TIME = './datamesh/c_features/datasets/sctp_routes_idle_time.csv'

# Load the CSV data into a DataFrame
df = pd.read_csv(SCTP_IDDLE_TIME, encoding='utf-8')

# Filter the DataFrame to include only the 'UTEIS', 'SAB', and 'DOM' services
df_filtered = df[df['service_id'].isin(['UTEIS', 'SAB', 'DOM'])]

# Concatenate route_id and direction_id into a single field
df_filtered['route_direction'] = df_filtered['route_id'].astype(str) + '-' + df_filtered['direction_id'].astype(str)

# Create the heatmap using Plotly Express
fig = px.imshow(df_filtered.pivot_table(index='route_direction', columns='service_id', values='idle_time_average'),
                labels={'x': "Service Type", 'y': "Route + Direction", 'color': "Average Idle Time (min)"},
                title="Heatmap of Average Idle Time by Route-Direction and Service",
                color_continuous_scale='YlGnBu', aspect='auto')

# Adjust layout for better visualization
fig.update_layout(
    autosize=True,    # Automatically resize the plot based on content
    width=1500,       # Increase the width of the whole plot to give more space
    height=900,       # Adjust the height for better visualization
    xaxis=dict(
        tickangle=45,      # Rotate the labels for readability
        tickmode='array',  # Ensure that tick labels are spaced properly
        showgrid=True,      # Add grid lines to separate the columns visually
        showline=True,      # Show line on the x-axis for clarity
    ),
    yaxis=dict(
        tickangle=0,       # Keep route labels horizontal
    ),
    title_x=0.5,        # Center the title
    margin=dict(l=100, r=100, t=100, b=100),  # Add margins around the plot for clarity
    xaxis_title="Service Type",
    yaxis_title="Route + Direction",
)

# Save the plot as an interactive HTML file
fig.write_html('./datamesh/e_presentation/dashboards/factory/html/heatmap_stcp_route_iddle_time_average.html')

# Show the figure (optional)
fig.show()
