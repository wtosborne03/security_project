import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from log_ingestor import LogIngestor  # Assuming this file is in the same directory
from data_processing import DataProcessor
from ml import isoforest

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Security Logs Visualizer"

# Load and process initial log data
log_ingestor = LogIngestor("/var/log/auth.log")
log_data = log_ingestor.ingest_logs()
processor = DataProcessor(log_data)
processor.clean_data().categorize_severity().categorize_event_type()
processed_data = processor.get_processed_data()

# Layout of the dashboard
app.layout = html.Div([
    html.H1("Security Logs Dashboard", style={"textAlign": "center"}),

    # Date range picker for filtering logs
    dcc.DatePickerRange(
        id="date-picker-range",
        start_date=processed_data["timestamp"].min(),
        display_format="YYYY-MM-DD"
    ),
    

    # Dropdown for severity filter
    dcc.Dropdown(
        id="severity-filter",
        options=[{"label": level, "value": level} for level in processed_data["severity"].unique()],
        multi=True,
        placeholder="Filter by severity level",
        style={"width": "50%"}
    ),
    
    html.H3("5 Most Recent Logs"),
    html.Table(id='recent-logs-table'),
    

    # Live-updating time series graph of log events
    dcc.Graph(id="time-series"),

    # Pie chart for event type distribution
    dcc.Graph(id="event-type-pie"),

    # Bar chart for severity levels
    dcc.Graph(id="severity-bar"),
    
    dcc.Graph(id="anomalies"),
    
    dcc.Graph(id="ip-frequency"),

    # Interval for auto-updating the dashboard
    dcc.Interval(
        id="interval-component",
        interval=3 * 1000,  # 10 seconds
        n_intervals=0
    )
])


@app.callback(
    [Output("time-series", "figure"),
     Output("event-type-pie", "figure"),
     Output("severity-bar", "figure"),
     Output('recent-logs-table', 'children'),
     Output("anomalies", "figure"),
     Output("ip-frequency", "figure")],
    [Input("interval-component", "n_intervals"),
     Input("date-picker-range", "start_date"),
     Input("date-picker-range", "end_date"),
     Input("severity-filter", "value")]
)

def update_dashboard(n_intervals, start_date, end_date, severity_filter):
    """Update all dashboard elements based on filters and time interval."""

    # Reload and process the latest log data
    log_data = log_ingestor.ingest_logs()
    processor = DataProcessor(log_data)
    processor.clean_data().categorize_severity().categorize_event_type()
    
    un_data = processor.get_processed_data()
    
    anomalies = isoforest(un_data)

    # Apply date range filter
    processor.filter_by_date_range(start_date, end_date)

    # Apply severity filter if selected
    if severity_filter:
        processor.filter_by_severity(severity_filter)

    # Get processed data for visualization
    data = processor.get_processed_data()
    
    recent_data = data.sort_values(by="timestamp", ascending=False).head(5)
    
    print(recent_data)
    
    table_rows = [
    html.Tr([html.Th("Timestamp"), html.Th("Event Type"), html.Th("Severity"), html.Th("Message"), html.Th("Ip")])] + [html.Tr([
            html.Td(log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')),
            html.Td(log['event_type']),
            html.Td(log['severity']),
            html.Td(log['message']),
            html.Td(log['ips']),
        ]) for _, log in recent_data.iterrows()]
    
    
    hourly_data = data.groupby(pd.Grouper(key="timestamp", freq="H")).size().reset_index(name="log_count")
    hourly_data["hour"] = hourly_data["timestamp"].dt.strftime('%H:%M')  # Format hour as HH:MM for better display

    # Time Series Plot
    time_series = px.histogram(
        hourly_data,
        x="hour",
        y="log_count",
        title="Average Log Events Per Hour",
        labels={"hour": "Hour", "log_count": "Log Count"}
    )

    # Pie Chart of Event Types
    event_type_counts = data["event_type"].value_counts().reset_index()
    event_type_counts.columns = ["event_type", "count"]  # Rename columns for clarity

    # Create the pie chart
    event_type_pie = px.pie(
        event_type_counts,
        values="count",       # The column with the counts of each event type
        names="event_type",    # The column with the names of event types
        title="Event Type Distribution"
    )

    # Bar Chart of Severity Levels
    severity_counts = data["severity"].value_counts().reset_index()
    severity_counts.columns = ["severity", "count"]  # Rename columns for clarity

    # Create the bar chart
    severity_bar = px.bar(
        severity_counts,
        x="severity",         # Column with severity labels
        y="count",            # Column with counts for each severity
        title="Log Events by Severity",
        labels={"severity": "Severity", "count": "Count"}
    )
    
    anomaly_graph = px.scatter(anomalies, 
                 x='timestamp', 
                 y='severity', 
                 color='anomaly', 
                 labels={'timestamp': 'Timestamp', 'severity': 'Severity'},
                 title='Anomaly Detection in Log Data',
                 color_continuous_scale='RdYlGn',
                 category_orders={'anomaly': [-1, 1]},  # -1 for anomaly, 1 for normal
                 hover_data=['host', 'process', 'event_type', 'ips', 'message'])
    
    ip_counts = data['ips'].value_counts().reset_index()
    ip_counts.columns = ['ip', 'log_count']

    # Create a bubble chart where the size of the bubble is based on the log_count
    ip_bubble = px.scatter(ip_counts, 
                            x='ip', 
                            y='log_count', 
                            size='log_count', 
                            color='log_count', 
                            hover_name='ip', 
                            title="Log Count by IP",
                            labels={'log_count': 'Number of Logs', 'ip': 'IP Address'},
                            color_continuous_scale='Viridis')
    

    return time_series, event_type_pie, severity_bar, table_rows, anomaly_graph, ip_bubble


if __name__ == "__main__":
    app.run_server(debug=True)
