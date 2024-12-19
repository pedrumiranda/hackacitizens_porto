import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

# Dataset with latitude and longitude of wifi hotspots
SCTP_IDDLE_TIME = './datamesh/c_features/datasets/sctp_routes_idle_time.csv'

# Load the CSV data into a DataFrame
df = pd.read_csv(SCTP_IDDLE_TIME, encoding='utf-8')



# Sort the data by idle_time_average in descending order for each service_id
df_sorted = df.sort_values(by='idle_time_average', ascending=False)

# Get the top 30 routes for each service_id (DOM, SAB, UTEIS)
top_routes = df_sorted[df_sorted['service_id'].isin(['DOM', 'SAB', 'UTEIS'])]
top_routes = top_routes.groupby('service_id').head(30)

# Create a figure for each service_id
fig_dict = {}

# List of service_ids to include in the grid
service_ids = ['DOM', 'SAB', 'UTEIS']

for service in service_ids:
    # Filter data for each service_id
    service_df = top_routes[top_routes['service_id'] == service]
    
    # Create the histogram for the current service
    fig = go.Figure()
    
    fig.add_trace(
        go.Histogram(
            x=service_df['route_id'].astype(str) + ' - ' + service_df['direction_id'].astype(str),
            y=service_df['idle_time_average'],
            histfunc='sum',
            marker=dict(color='lightblue'),
            name=f'{service}'
        )
    )
    
    # Update layout for better visualization
    fig.update_layout(
        title=f'Top 30 Routes with the Most Idle Time ({service})',
        xaxis_title='Route ID - Direction ID',
        yaxis_title='Total Idle Time (minutes)',
        xaxis_tickangle=-45,
        template='plotly_white',
        height=500,
        margin=dict(t=50, b=150),
    )
    
    # Save the figure to the dictionary
    fig_dict[service] = fig

# Generate the combined HTML layout (grid style)
html_combined = """
<html>
<head>
    <title>Top 30 Routes with Idle Time Analysis</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: grid;
            grid-template-columns: 1fr 1fr; /* Two columns */
            grid-template-rows: 1fr 1fr; /* Two rows */
            height: 100vh;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        .plot-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px;
            height: 100%;  /* Ensure full use of the space */
        }
        h2 {
            text-align: center;
            position: absolute;
            top: 10px;
            left: 10px;
        }
    </style>
</head>
<body>
    <h1>Top 30 Routes with Most Idle Time by Service</h1>
"""

# Add each plot to the HTML content in a 2x2 grid
html_combined += f"""
    <div class="plot-container">
        <h2>DOM</h2>
        """ + pio.to_html(fig_dict['UTEIS'], full_html=False) + """
    </div>
    <div class="plot-container">
        <h2>SAB</h2>
        """ + pio.to_html(fig_dict['SAB'], full_html=False) + """
    </div>
    <div class="plot-container">
        <h2>UTEIS</h2>
        """ + pio.to_html(fig_dict['UTEIS'], full_html=False) + """
    </div>
    <div class="plot-container">
        <!-- Empty div for the 4th rectangle -->
    </div>
</body>
</html>
"""

# Save the combined HTML to a file
combined_html_file = './top_routes_idle_time_combined_2x2.html'
with open(combined_html_file, 'w', encoding='utf-8') as f:
    f.write(html_combined)

print(f"Combined HTML file saved to {combined_html_file}")
