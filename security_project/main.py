import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from tools.log_parser import parse_log, clean_data
from tools.anomaly_detection import kmeans_clustering, isolation_forest, alert
import threading
import time

app = dash.Dash(__name__)

# Global DataFrame to store logs
log_df = pd.DataFrame(columns=['Timestamp', 'Source', 'Message'])

# Dash layout
app.layout = html.Div([
    dcc.Graph(id='live-update-graph-1'),
    dcc.Graph(id='live-update-graph-2'),
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # in milliseconds
        n_intervals=0
    )
])

@app.callback(Output('live-update-graph-1', 'figure'),
              Output('live-update-graph-2', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph(n):
    global log_df
    fig1 = px.line(log_df['Timestamp'].value_counts().sort_index(), title='Log Events Over Time')
    fig2 = px.bar(log_df['Source'].value_counts(), title='Log Events by Source')
    return fig1, fig2

class LogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global log_df
        if event.src_path.endswith('.log'):
            print(f'Log file modified: {event.src_path}')
            new_logs = parse_log(event.src_path)
            new_logs = clean_data(new_logs)
            if not new_logs.empty:
                log_df = pd.concat([log_df, new_logs], ignore_index=True)
                log_df = kmeans_clustering(log_df)
                log_df = isolation_forest(log_df)
                alert(log_df)

def start_monitoring(log_path):
    observer = Observer()
    observer.schedule(LogHandler(), path=log_path)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    log_path = '/var/log'  # Update this path to your log directory
    monitor_thread = threading.Thread(target=start_monitoring, args=(log_path,))
    monitor_thread.start()
    app.run_server(debug=True)